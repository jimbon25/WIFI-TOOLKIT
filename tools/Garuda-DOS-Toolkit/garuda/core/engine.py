import asyncio
import sys
import importlib
import platform
import signal
from argparse import Namespace
from urllib.parse import urlparse

from garuda.core.monitor import Monitor
from garuda.modules.attacks.base_attack import BaseAttack

class GarudaEngine:
    """
    Kelas utama untuk mengelola eksekusi serangan.

    Kelas ini bertanggung jawab untuk memuat modul serangan, memulai serangan,
    memonitor statistik serangan, dan menangani penghentian serangan.

    Attributes:
        config (Namespace): Konfigurasi serangan yang diterima dari CLI atau file konfigurasi.
        target_info (ParseResult): Informasi target yang diurai dari URL.
        loop (asyncio.AbstractEventLoop): Event loop yang digunakan untuk menjalankan tugas asinkron.
        attack_instance (BaseAttack): Instance dari kelas serangan yang dimuat.
        monitor_instance (Monitor): Instance monitor untuk mencetak statistik serangan.
        shutdown_event (asyncio.Event): Event untuk menangani penghentian serangan.
    """

    def __init__(self, config: Namespace):
        """
        Inisialisasi monitor.

        Args:
            attack_instance (BaseAttack): Instance serangan yang akan dimonitor.
            interval (float, optional): Interval waktu untuk mencetak statistik. Default adalah 1.0 detik.
        """
        self.config = config
        self.target_info = urlparse(config.target)

        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        self.attack_instance: BaseAttack = self._load_attack_module()
        self.monitor_instance: Monitor = Monitor(self.attack_instance)
        self.shutdown_event = asyncio.Event()

    def _load_attack_module(self) -> BaseAttack:
        """
        Mencetak statistik serangan secara real-time.

        Behavior:
            - Menampilkan durasi serangan, jumlah koneksi aktif, paket terkirim, dan koneksi gagal.
            - Statistik diperbarui setiap interval waktu yang ditentukan.
        """
        method_name = self.config.method.replace('-', '_')
        module_path = f"garuda.modules.attacks.{method_name}"
        class_name = f"{''.join(word.capitalize() for word in method_name.split('_'))}Attack"

        try:
            attack_module = importlib.import_module(module_path)
            attack_class = getattr(attack_module, class_name)
            print(f"[INFO] Modul serangan '{class_name}' berhasil dimuat.")

            attack_args = {
                "target": self.target_info,
                "connections": self.config.connections,
                "stealth": self.config.stealth
            }

            if self.config.method == 'mixed':
                attack_args["attacks"] = self.config.attacks

            return attack_class(**attack_args)
        except (ImportError, AttributeError) as e:
            print(f"[FATAL] Gagal memuat modul serangan '{class_name}'.", file=sys.stderr)
            print(f"  > Detail: {e}", file=sys.stderr)
            sys.exit(1)

    async def _main_task(self):
        """
        Menjalankan monitor untuk mencetak statistik secara berkala.

        Behavior:
            - Memanggil `_print_stats` setiap interval waktu yang ditentukan.
            - Menghentikan monitor jika tugas dibatalkan.
        """
        print("\n[*] Serangan dimulai. Tekan Ctrl+C untuk berhenti.")
        attack_task = self.loop.create_task(self.attack_instance.execute())
        monitor_task = self.loop.create_task(self.monitor_instance.run())
        
        shutdown_waiter = self.loop.create_task(self.shutdown_event.wait())
        duration_waiter = self.loop.create_task(asyncio.sleep(self.config.duration))

        done, pending = await asyncio.wait(
            {shutdown_waiter, duration_waiter},
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

        self.attack_instance.is_running = False
        attack_task.cancel()
        monitor_task.cancel()
        await asyncio.gather(attack_task, monitor_task, return_exceptions=True)
        
        self.monitor_instance.display_final_report()

    async def _shutdown_handler(self):
        """
        Handler untuk menangani sinyal shutdown (SIGINT/SIGTERM).

        Behavior:
            - Men-trigger shutdown_event untuk menghentikan serangan
            - Memastikan serangan berhenti dengan graceful
        """
        print("\n[INFO] Menerima sinyal shutdown. Menghentikan serangan...")
        self.shutdown_event.set()

    def start(self):
        """
        Menampilkan laporan akhir serangan.

        Behavior:
            - Menampilkan total durasi serangan, total paket terkirim, koneksi gagal,
              rata-rata paket per detik, dan tingkat keberhasilan.
            - Mengambil informasi target dari instance serangan.
        """
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(sig, lambda: asyncio.create_task(self._shutdown_handler()))
        
        try:
            self.loop.run_until_complete(self._main_task())
        finally:
            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    self.loop.remove_signal_handler(sig)
                except Exception:
                    pass
            if not self.loop.is_closed():
                print("\n[INFO] Proses selesai. Menutup event loop.")
                self.loop.close()