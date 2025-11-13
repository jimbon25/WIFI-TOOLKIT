import random

REFERER_LIST = [
    "https://www.facebook.com/",
    "https://www.twitter.com/",
    "https://www.instagram.com/",
    "https://www.youtube.com/",
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
    "https://www.duckduckgo.com/",
]

def get_random_referer() -> str:
    """
    Mengambil sebuah URL referer acak dari daftar.
    """
    return random.choice(REFERER_LIST)