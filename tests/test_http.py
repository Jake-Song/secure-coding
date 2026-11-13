from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from http.server import HTTPServer
import io
import unittest
from urllib.request import ProxyHandler, build_opener

from werkzeug.serving import make_server

from app import create_app
from examples.csrf_server import Handler
from examples.http_demo import main


class HTTPLabTests(unittest.TestCase):
    def test_http_demo_with_real_cookie_login_and_requests(self):
        app = create_app(testing=True)
        self.addCleanup(app.extensions["lab_db"].close)
        with make_server("127.0.0.1", 0, app) as server:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(server.serve_forever, poll_interval=0.05)
                output = io.StringIO()
                try:
                    with redirect_stdout(output):
                        main(f"http://127.0.0.1:{server.server_port}")
                finally:
                    server.shutdown()
                future.result(timeout=10)
        text = output.getvalue()
        for label, safe_status in (("IDOR", 404), ("SQLi", 200), ("XSS", 200),
                                   ("CSRF", 403), ("Mass assignment", 400)):
            self.assertIn(f"{label:16} safe HTTP {safe_status}", text)
            self.assertIn(f"{label:16} vuln HTTP 200", text)
        self.assertIn("Bob private memo", text)
        self.assertIn("&lt;script&gt;", text)

    def test_csrf_demo_page_over_http(self):
        with HTTPServer(("127.0.0.1", 0), Handler) as server:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(server.serve_forever, poll_interval=0.05)
                try:
                    client = build_opener(ProxyHandler({}))
                    with client.open(f"http://127.0.0.1:{server.server_port}", timeout=5) as response:
                        body = response.read().decode()
                        self.assertEqual(response.status, 200)
                        self.assertIn("127.0.0.1:5000/vuln/status", body)
                        self.assertIn("127.0.0.1:5000/safe/status", body)
                finally:
                    server.shutdown()
                future.result(timeout=10)


if __name__ == "__main__":
    unittest.main()
