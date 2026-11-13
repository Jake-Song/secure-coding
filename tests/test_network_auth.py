from concurrent.futures import ThreadPoolExecutor
import unittest

from examples.network_security.auth import Verifier, exchange, sign


class AuthUnitTests(unittest.TestCase):
    def setUp(self):
        self.key = b"test-only-key-not-for-deployment"
        self.now = 1000

    def verifier(self, **kwargs):
        return Verifier({"alice": self.key}, clock=lambda: self.now, **kwargs)

    def request(self, **kwargs):
        return sign(self.key, timestamp=self.now, **kwargs)

    def test_valid_signature_and_tamper(self):
        request = self.request()
        self.assertTrue(self.verifier().handle(request)["ok"])
        for field, value in (("note", 2), ("user", "bob"), ("nonce", "f" * 32)):
            self.assertEqual(self.verifier().handle({**request, field: value})["reason"], "authentication")

    def test_signed_request_still_needs_authorization(self):
        for note in (2, 999):
            self.assertEqual(self.verifier().handle(self.request(note=note))["reason"], "forbidden")

    def test_replay_fails_but_fresh_nonce_succeeds(self):
        verifier = self.verifier()
        request = self.request()
        self.assertTrue(verifier.handle(request)["ok"])
        self.assertEqual(verifier.handle(request)["reason"], "replay")
        self.assertTrue(verifier.handle(self.request())["ok"])

    def test_mac_alone_does_not_prevent_replay(self):
        verifier = self.verifier(freshness=False)
        request = self.request()
        self.assertTrue(verifier.handle(request)["ok"])
        self.assertTrue(verifier.handle(request)["ok"])

    def test_old_and_future_timestamps(self):
        for stamp in (969, 1031):
            self.assertEqual(self.verifier().handle(sign(self.key, timestamp=stamp))["reason"], "expired")
        for stamp in (970, 1030):
            self.assertTrue(self.verifier().handle(sign(self.key, timestamp=stamp))["ok"])

    def test_nonce_retained_through_future_timestamp_window(self):
        verifier = self.verifier()
        request = sign(self.key, timestamp=1030)
        self.assertTrue(verifier.handle(request)["ok"])
        self.now = 1060
        self.assertEqual(verifier.handle(request)["reason"], "replay")
        self.now = 1061
        self.assertEqual(verifier.handle(request)["reason"], "expired")
        self.assertTrue(verifier.handle(self.request())["ok"])
        self.assertEqual(len(verifier.seen), 1)

    def test_nonce_cache_is_bounded_and_fails_closed(self):
        verifier = self.verifier(max_nonces=1)
        self.assertTrue(verifier.handle(self.request())["ok"])
        self.assertEqual(verifier.handle(self.request())["reason"], "nonce_capacity")

    def test_concurrent_replay_only_one_request_succeeds(self):
        verifier, request = self.verifier(), self.request()
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(verifier.handle, [request] * 8))
        self.assertEqual(sum(result["ok"] for result in results), 1)

    def test_invalid_schema_and_non_ascii_mac_fail_cleanly(self):
        original = self.request()
        for value in ([], {}, {**original, "extra": 1}, {**original, "user": []},
                      {**original, "timestamp": True}, {**original, "timestamp": 10**500},
                      {**original, "note": True}, {**original, "mac": "가" * 64},
                      {**original, "nonce": "x" * 32}, {**original, "action": "delete"}):
            self.assertEqual(self.verifier().handle(value)["reason"], "schema")


class AuthSocketTests(unittest.TestCase):
    def test_real_tcp_accept_replay_tamper_authorization_and_expiry(self):
        key = b"test-only-key"
        verifier = Verifier({"alice": key}, clock=lambda: 1000)
        original = sign(key, timestamp=1000)
        requests = [original, original, {**sign(key, timestamp=1000), "note": 2},
                    sign(key, timestamp=1000, note=2), sign(key, timestamp=900)]
        responses = exchange(verifier, requests)
        self.assertTrue(responses[0]["ok"])
        self.assertEqual([r["reason"] for r in responses[1:]],
                         ["replay", "authentication", "forbidden", "expired"])


if __name__ == "__main__":
    unittest.main()
