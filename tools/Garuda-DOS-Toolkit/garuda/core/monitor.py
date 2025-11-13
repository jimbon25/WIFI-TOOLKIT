import asyncio
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from garuda.modules.attacks.base_attack import BaseAttack

class Monitor:
    """
    Kelas untuk memonitor statistik serangan secara real-time.

    Kelas ini bertanggung jawab untuk mencetak statistik serangan secara berkala
    dan menampilkan laporan akhir setelah serangan selesai.

    Attributes:
        attack (BaseAttack): Instance serangan yang sedang dimonitor.
        interval (float): Interval waktu (dalam detik) untuk mencetak statistik.
        _start_time (float): Waktu mulai monitor dalam satuan monotonic time.
        total_duration (float): Total durasi serangan dalam detik.
    """

    def __init__(self, attack_instance: "BaseAttack", interval: float = 1.0):
        """
        Inisialisasi monitor.

        Args:
            attack_instance (BaseAttack): Instance serangan yang akan dimonitor.
            interval (float, optional): Interval waktu untuk mencetak statistik. Default adalah 1.0 detik.
        """
        self.attack = attack_instance
        self.interval = interval
        self._start_time = time.monotonic()
        self.total_duration = 0.0

    def _print_stats(self):
        """
        Mencetak statistik serangan secara real-time.

        Behavior:
            - Menampilkan durasi serangan, jumlah koneksi aktif, paket terkirim, dan koneksi gagal.
            - Statistik diperbarui setiap interval waktu yang ditentukan.
            - Menggunakan thread-safe access yang sudah built-in di ThreadSafeStats.
        """
        stats = self.attack.stats.copy()
        
        elapsed = time.monotonic() - self._start_time
        
        print(
            f"\r[+] Durasi: {elapsed:<5.1f}s | "
            f"Aktif: {stats.get('active_connections', 0):<5} | "
            f"Terkirim: {stats.get('sent_packets', 0):<7} | "
            f"Gagal: {stats.get('failed_connections', 0):<5}",
            end=""
        )

    async def run(self):
        """
        Menjalankan monitor untuk mencetak statistik secara berkala.

        Behavior:
            - Memanggil `_print_stats` setiap interval waktu yang ditentukan.
            - Menghentikan monitor jika tugas dibatalkan.
            - Memberikan sedikit delay sebelum mulai monitoring untuk stabilitas.
        """
        await asyncio.sleep(0.1)
        
        while True:
            try:
                self._print_stats()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                self.total_duration = time.monotonic() - self._start_time
                self._print_stats()
                break

    def display_final_report(self):
        """
        Menampilkan laporan akhir serangan.

        Behavior:
            - Menampilkan total durasi serangan, total paket terkirim, koneksi gagal,
              rata-rata paket per detik, dan tingkat keberhasilan.
            - Mengambil informasi target dari instance serangan.
            - Menggunakan thread-safe access yang sudah built-in di ThreadSafeStats.
        """
        if self.total_duration == 0:
            self.total_duration = time.monotonic() - self._start_time

        stats = self.attack.stats.copy()
        
        sent = stats.get('sent_packets', 0)
        failed = stats.get('failed_connections', 0)
        total_attempts = self.attack.connections
        
        requests_per_second = (sent / self.total_duration) if self.total_duration > 0 else 0
        
        if sent > 0:
            success_rate = (sent / (sent + failed) * 100) if (sent + failed) > 0 else 0
        else:
            success_rate = 0.0

        print("\n\n" + "━"*60)
        print(" " * 17 + "LAPORAN AKHIR SERANGAN")
        print("━"*60)

        target_url = getattr(getattr(self.attack, 'target', None), 'geturl', lambda: "N/A")()
        print(f"{'Target':<25}: {target_url}")
        print(f"{'Total Durasi':<25}: {self.total_duration:.2f} detik")
        print("─"*60)
        print(f"{'Total Paket Terkirim':<25}: {sent}")
        print(f"{'Total Koneksi Gagal':<25}: {failed}")
        print(f"{'Rata-rata Paket/Detik':<25}: {requests_per_second:.2f}")
        print(f"{'Tingkat Keberhasilan':<25}: {success_rate:.2f}%")
        print("━"*60)