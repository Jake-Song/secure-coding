# Chapter 11 통합 설계와 첫 실행

[이전 Chapter 10](chapter-10.md) · [네트워크 보안 커리큘럼](curriculum.md) · [다음 Chapter 12](chapter-12.md)

## 어느 단계에서 무엇을 결정하는가

메모 조회 서비스는 연결을 TLS로 감싼 뒤 길이 제한이 있는 JSON 프레임 하나를 읽습니다. TLS는 전송 채널을 보호하고, 메시지 검증기는 요청한 사용자와 대상 메모의 권한을 확인합니다.

```text
로컬 연결 → TLS 핸드셰이크 → 길이 제한 프레임 → JSON 스키마
          → HMAC → 시간과 nonce → 메모 소유권 → 응답
```

| 신뢰 경계 | 확인할 정보 | 코드 |
|---|---|---|
| 클라이언트가 연결한 서버 | CA와 인증서 이름 | [tls.py](../../examples/network_security/tls.py) |
| 네트워크 바이트에서 요청 객체로 | 길이 상한, UTF-8과 JSON 형식 | [framing.py](../../examples/network_security/framing.py) |
| 요청 객체에서 메모 읽기로 | 스키마, 사용자 키, 시간, nonce, 소유권 | [auth.py](../../examples/network_security/auth.py) |

## 정상 요청을 한 번 통과시키기

아래 예제는 임시 CA와 키를 생성하고, 로컬 TLS 연결로 Alice의 본인 메모를 요청합니다. 프레임·인증·인가 함수를 연결한 뒤 응답 성공 여부를 확인합니다.

```bash
python3 - <<'PY'
import secrets
import socket
from tempfile import TemporaryDirectory

from examples.network_security.auth import Verifier, sign
from examples.network_security.common import HOST, TIMEOUT, tcp_server
from examples.network_security.framing import recv_json, send_json
from examples.network_security.tls import create_certificates, client_context, server_context


def main():
    key = secrets.token_bytes(32)
    verifier = Verifier({"alice": key})
    with TemporaryDirectory() as temporary:
        certs = create_certificates(temporary)
        server = server_context(certs)
        client = client_context(certs / "ca.crt")

        def serve(connection):
            with server.wrap_socket(connection, server_side=True) as secure:
                request = recv_json(secure)
                send_json(secure, verifier.handle(request))

        with tcp_server(serve) as port:
            with socket.create_connection((HOST, port), TIMEOUT) as connection:
                with client.wrap_socket(connection, server_hostname="localhost") as secure:
                    send_json(secure, sign(key))
                    response = recv_json(secure)
                    assert response == {"ok": True, "note": "Alice lab note"}
                    print(f"{secure.version()} / 메모 조회 성공")


main()
PY
```

예상 출력은 `TLSv1.3 / 메모 조회 성공`입니다. 환경에 따라 협상 버전은 TLS 1.2일 수 있습니다. 이 실행을 바탕으로 거부 경로를 설계하세요. 연결의 실제 상대 주소가 필요하면 소켓에서 읽고, 클라이언트가 JSON에 넣은 문자열은 별도의 입력으로 취급합니다. 로그에는 시간, 단계, 거부 사유처럼 분석에 필요한 항목만 남기고 원문 키·MAC·메모 본문은 기록에서 가립니다.

**확인 문제.** 인증서 검증 실패와 메모 소유권 실패는 각각 누가 어느 계층에서 판단하나요? 다음 연결에서도 nonce 기록을 유지하려면 `Verifier`는 어디서 만들어야 하나요?

**제출물.** 첫 통합 실행 결과, 입력과 신뢰 경계 그림, 임시 키와 인증서의 수명, 각 실패 단계에서 처리할 예외와 검증 계획을 적으세요.
