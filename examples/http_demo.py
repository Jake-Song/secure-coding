"""실제 loopback HTTP로 로그인 후 취약/방어 경로 응답을 비교한다."""
import http.cookiejar
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener


def main(base="http://127.0.0.1:5000"):
    client = build_opener(ProxyHandler({}), HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(path, *, form=None, payload=None, token=None):
        headers = {}
        data = None
        if form is not None:
            data = urlencode(form).encode()
        if payload is not None:
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        if token:
            headers["X-CSRF-Token"] = token
        req = Request(base + path, data=data, headers=headers)
        try:
            response = client.open(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            body = response.read().decode()
            return response.status, body

    _, body = call("/session")
    call("/login", form={"username": "alice", "password": "alice-lab",
                         "csrf": json.loads(body)["csrf"]})
    _, body = call("/session")
    token = json.loads(body)["csrf"]

    probes = [
        ("IDOR", "/notes/2", {}),
        ("SQLi", "/search?" + urlencode({"q": "x' UNION SELECT id, body FROM notes -- "}), {}),
        ("XSS", "/greet?" + urlencode({"name": "<script>document.title='LAB_XSS'</script>"}), {}),
        ("CSRF", "/status", {"form": {"display_name": "changed without token"}}),
        ("Mass assignment", "/profile", {"payload": {"is_admin": 1}, "token": token}),
    ]
    for label, path, kwargs in probes:
        # 방어 경로를 먼저 호출해 취약 경로의 상태 변경 영향을 피한다.
        for mode in ("safe", "vuln"):
            status, body = call("/" + mode + path, **kwargs)
            print(f"{label:16} {mode:4} HTTP {status}: {body[:180].strip()}")
    print("주의: 이 실행은 Alice를 관리자 상태로 변경합니다. 서버 재시작으로 초기화하세요.")
    print("XSS 출력은 HTML 검사입니다. 실제 스크립트 실행은 브라우저에서 확인하세요.")


if __name__ == "__main__":
    main()
