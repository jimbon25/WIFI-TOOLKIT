import asyncio
import importlib
import sys

from .base_attack import BaseAttack

class MixedAttack(BaseAttack):
    """
    Implementasi serangan gabungan (mixed attack).

    Serangan ini memungkinkan kombinasi beberapa metode serangan yang berbeda
    untuk dijalankan secara bersamaan. Setiap metode serangan dimuat sebagai
    instance terpisah dan dikelola oleh kelas ini.

    Attributes:
        attack_methods (list): Daftar nama metode serangan yang akan digunakan.
        attack_instances (list): Daftar instance serangan yang dimuat.
    """

    def __init__(self, target, connections, attacks: list, stealth: bool = False):
        """
        Inisialisasi serangan gabungan.

        Args:
            target (ParseResult): Target serangan dalam bentuk URL yang telah diurai.
            connections (int): Jumlah koneksi yang akan dibuat selama serangan.
            attacks (list): Daftar nama metode serangan yang akan digunakan.
            stealth (bool, optional): Opsi untuk mengaktifkan mode stealth. Default adalah False.

        Behavior:
            - Memuat modul serangan berdasarkan nama metode yang diberikan.
            - Membuat instance serangan untuk setiap metode yang dimuat.
            - Menangani kesalahan jika modul atau kelas serangan tidak ditemukan.

        Exceptions:
            - Menghentikan program jika salah satu sub-serangan gagal dimuat.
        """
        super().__init__(target, connections, stealth)
        self.attack_methods = attacks
        self.attack_instances = []

        for method_name in self.attack_methods:
            try:
                module_name = method_name.replace('-', '_')
                class_name = f"{''.join(word.capitalize() for word in module_name.split('_'))}Attack"
                module_path = f"garuda.modules.attacks.{module_name}"
                
                attack_module = importlib.import_module(module_path)
                attack_class = getattr(attack_module, class_name)
                
                instance = attack_class(self.target, self.connections, stealth=self.stealth)
                self.attack_instances.append(instance)
                print(f"[INFO] Sub-serangan '{class_name}' berhasil dimuat untuk mode mixed.")
            except (ImportError, AttributeError) as e:
                print(f"[FATAL] Gagal memuat sub-serangan '{method_name}' untuk mode mixed.", file=sys.stderr)
                print(f"  > Detail: {e}", file=sys.stderr)
                sys.exit(1)

    @BaseAttack.is_running.setter
    def is_running(self, value: bool):
        """
        Mengatur status `is_running` untuk semua sub-serangan.

        Args:
            value (bool): True untuk menandai serangan sedang berjalan, False untuk berhenti.
        """
        self._is_running = value
        for instance in self.attack_instances:
            instance.is_running = value

    async def _aggregate_stats(self):
        """
        Menggabungkan statistik dari semua sub-serangan secara berkala.

        Behavior:
            - Mengumpulkan statistik seperti jumlah paket terkirim, koneksi gagal,
              dan koneksi aktif dari semua sub-serangan.
            - Memperbarui statistik gabungan setiap 0.5 detik.
            - Menghentikan pengumpulan statistik jika serangan dihentikan.
        """
        while self.is_running:
            total_stats = {
                "sent_packets": 0,
                "failed_connections": 0,
                "active_connections": 0,
            }
            for instance in self.attack_instances:
                total_stats["sent_packets"] += instance.stats.get("sent_packets", 0)
                total_stats["failed_connections"] += instance.stats.get("failed_connections", 0)
                total_stats["active_connections"] += instance.stats.get("active_connections", 0)
            
            for key, value in total_stats.items():
                self.stats[key] = value
            
            try:
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break

    async def execute(self):
        """
        Menjalankan semua sub-serangan secara bersamaan.

        Behavior:
            - Memulai eksekusi setiap sub-serangan secara asinkron.
            - Menggabungkan statistik dari semua sub-serangan selama serangan berlangsung.
            - Menghentikan semua sub-serangan setelah selesai.
        """
        self.is_running = True
        tasks = [instance.execute() for instance in self.attack_instances]
        tasks.append(self._aggregate_stats())
        await asyncio.gather(*tasks, return_exceptions=True)