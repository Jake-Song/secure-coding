from concurrent.futures import ThreadPoolExecutor
import socket
import unittest

from examples.tcp_client import exchange
from examples.tcp_server import serve_once


class TCPLabTests(unittest.TestCase):
    def test_round_trip_empty_unicode_and_multiple_chunks(self):
        for message in (b"", b"hello", "안녕하세요".encode(), bytes(range(256)) * 80):
            with self.subTest(size=len(message)), socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                listener.listen(1)
                listener.settimeout(10)
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(serve_once, listener)
                    self.assertEqual(exchange(message, listener.getsockname()[1]), message)
                    future.result(timeout=10)

    def test_oversize_message_is_rejected_before_connecting(self):
        with self.assertRaises(ValueError):
            exchange(b"x" * (64 * 1024 + 1))


if __name__ == "__main__":
    unittest.main()
