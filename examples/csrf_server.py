"""http://127.0.0.1:8001 에서 고정된 로컬 CSRF 데모 페이지만 제공한다."""
from http.server import BaseHTTPRequestHandler, HTTPServer


PAGE = """<!doctype html><html lang="ko"><meta charset="utf-8">
<title>CSRF 실습</title><h1>다른 origin에서 폼 전송</h1>
<p>먼저 http://127.0.0.1:5000 에서 로그인하세요.</p>
<form method="post" action="http://127.0.0.1:5000/vuln/status">
<input type="hidden" name="display_name" value="CSRF changed">
<button>토큰 없이 취약 경로에 전송</button></form>
<form method="post" action="http://127.0.0.1:5000/safe/status">
<input type="hidden" name="display_name" value="CSRF changed">
<button>토큰 없이 방어 경로에 전송</button></form></html>""".encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)


if __name__ == "__main__":
    print("CSRF 페이지: http://127.0.0.1:8001", flush=True)
    HTTPServer(("127.0.0.1", 8001), Handler).serve_forever()
