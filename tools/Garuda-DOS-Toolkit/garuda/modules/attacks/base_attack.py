from abc import ABC, abstractmethod
import threading
from typing import Dict
from urllib.parse import ParseResult

class ThreadSafeStats:
    """
    Kelas untuk menangani statistik serangan dengan akses thread-safe.
    
    Menyediakan akses aman untuk read/write statistik dari multiple threads
    atau coroutine tanpa menyebabkan race condition.
    """
    
    def __init__(self, initial_stats: Dict[str, int]):
        """
        Inisialisasi statistik dengan nilai awal.
        
        Args:
            initial_stats: Dictionary dengan nilai statistik awal
        """
        self._stats = initial_stats.copy()
        self._lock = threading.Lock()
    
    def __getitem__(self, key: str) -> int:
        """Akses thread-safe untuk membaca nilai statistik."""
        with self._lock:
            return self._stats.get(key, 0)
    
    def __setitem__(self, key: str, value: int):
        """Akses thread-safe untuk mengubah nilai statistik."""
        with self._lock:
            self._stats[key] = value
    
    def get(self, key: str, default: int = 0) -> int:
        """Akses thread-safe untuk membaca nilai dengan default."""
        with self._lock:
            return self._stats.get(key, default)
    
    def __iter__(self):
        """Iterator thread-safe untuk statistik."""
        with self._lock:
            return iter(dict(self._stats))
    
    def keys(self):
        """Akses thread-safe untuk keys."""
        with self._lock:
            return list(self._stats.keys())
    
    def values(self):
        """Akses thread-safe untuk values."""
        with self._lock:
            return list(self._stats.values())
    
    def items(self):
        """Akses thread-safe untuk items."""
        with self._lock:
            return list(self._stats.items())
    
    def copy(self) -> Dict[str, int]:
        """Membuat copy thread-safe dari statistik."""
        with self._lock:
            return self._stats.copy()
    
    def increment(self, key: str, amount: int = 1):
        """Thread-safe increment untuk statistik."""
        with self._lock:
            self._stats[key] = self._stats.get(key, 0) + amount
    
    def decrement(self, key: str, amount: int = 1):
        """Thread-safe decrement untuk statistik."""
        with self._lock:
            self._stats[key] = max(0, self._stats.get(key, 0) - amount)

class BaseAttack(ABC):
    """
    Kelas abstrak untuk mendefinisikan serangan dasar.

    Kelas ini menyediakan kerangka kerja untuk serangan dengan atribut
    dan metode yang dapat digunakan oleh subclass. Setiap serangan harus
    mengimplementasikan metode `execute`.

    Attributes:
        target (ParseResult): Target serangan dalam bentuk URL yang telah diurai.
        connections (int): Jumlah koneksi yang akan dibuat selama serangan.
        stealth (bool): Opsi untuk mengaktifkan mode stealth (penyerangan lambat).
        stats (ThreadSafeDict): Statistik serangan, termasuk jumlah paket terkirim,
            koneksi yang gagal, dan koneksi aktif dengan akses thread-safe.
        _is_running (bool): Status internal apakah serangan sedang berjalan.
    """

    def __init__(self, target: ParseResult, connections: int, stealth: bool = False):
        """
        Inisialisasi objek serangan.

        Args:
            target (ParseResult): Target serangan dalam bentuk URL yang telah diurai.
            connections (int): Jumlah koneksi yang akan dibuat selama serangan.
            stealth (bool, optional): Opsi untuk mengaktifkan mode stealth. Default adalah False.
        """
        self.target = target
        self.connections = connections
        self.stealth = stealth
        self.stats = ThreadSafeStats({
            "sent_packets": 0,
            "failed_connections": 0,
            "active_connections": 0,
        })
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """
        Cek apakah serangan sedang berjalan.

        Returns:
            bool: True jika serangan sedang berjalan, False jika tidak.
        """
        return self._is_running

    @is_running.setter
    def is_running(self, value: bool):
        """
        Setel status apakah serangan sedang berjalan.

        Args:
            value (bool): True untuk menandai serangan sedang berjalan, False untuk berhenti.
        """
        self._is_running = value

    @abstractmethod
    async def execute(self):
        """
        Eksekusi serangan.

        Metode ini harus diimplementasikan oleh setiap subclass untuk
        mendefinisikan logika serangan spesifik.
        """
        raise NotImplementedError