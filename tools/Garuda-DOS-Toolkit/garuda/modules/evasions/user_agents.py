import random
from fake_useragent import UserAgent, FakeUserAgentError

try:
    ua = UserAgent()
except FakeUserAgentError:
    ua = None
    print("[WARNING] Gagal mengambil daftar User-Agent. Menggunakan fallback statis.")

FALLBACK_AGENTS = [
    f"Mozilla/5.0 (Windows NT {random.randint(7, 10)}.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randrange(100, 138)}.0.{random.randint(0000, 9999)}.{random.randint(000, 999)} Safari/537.36",
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(13, 15)}_{random.randint(0, 7)}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.randint(13, 15)}.{random.randint(0, 6)}.1 Safari/605.1.15",
    f"Mozilla/5.0 (X11; Linux x86_64; rv:{random.randint(89, 127)}.0) Gecko/20100101 Firefox/{random.randint(89, 127)}.0",
]

def get_random_user_agent() -> str:
    """
    Mengambil sebuah string User-Agent acak yang valid.
    Menggunakan fake-useragent dengan fallback ke daftar statis.
    """
    if ua:
        return ua.random
    return random.choice(FALLBACK_AGENTS)