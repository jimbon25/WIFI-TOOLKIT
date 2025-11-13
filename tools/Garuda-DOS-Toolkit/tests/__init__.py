import unittest
from garuda.modules.attacks.slowloris import SlowlorisAttack
from garuda.modules.attacks.http_flood import HttpFloodAttack
from types import SimpleNamespace
import asyncio

class DummyStats:
    def increment(self, key): pass
    def decrement(self, key): pass

class DummyTarget:
    def __init__(self, url):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        self.hostname = parsed.hostname
        self.port = parsed.port
        self.scheme = parsed.scheme
        self.path = parsed.path
        self.geturl = lambda: url

class TestAttacks(unittest.TestCase):
    def test_slowloris_init(self):
        attack = SlowlorisAttack(
            target=DummyTarget('http://localhost/'),
            connections=1,
            stats=DummyStats(),
            duration=1,
            stealth=False
        )
        self.assertIsInstance(attack, SlowlorisAttack)

    def test_httpflood_init(self):
        attack = HttpFloodAttack(
            target=DummyTarget('http://localhost/'),
            connections=1,
            stats=DummyStats(),
            duration=1,
            stealth=False
        )
        self.assertIsInstance(attack, HttpFloodAttack)

    def test_slowloris_execute(self):
        attack = SlowlorisAttack(
            target=DummyTarget('http://localhost/'),
            connections=1,
            stats=DummyStats(),
            duration=1,
            stealth=False
        )
        async def run():
            try:
                await asyncio.wait_for(attack.execute(), timeout=2)
            except Exception:
                pass
        asyncio.run(run())

    def test_httpflood_execute(self):
        attack = HttpFloodAttack(
            target=DummyTarget('http://localhost/'),
            connections=1,
            stats=DummyStats(),
            duration=1,
            stealth=False
        )
        async def run():
            try:
                await asyncio.wait_for(attack.execute(), timeout=2)
            except Exception:
                pass
        asyncio.run(run())
