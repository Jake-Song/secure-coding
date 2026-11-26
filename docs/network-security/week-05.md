# 5주차 TLS와 신뢰

[이전 4주차](week-04.md) · [12주 커리큘럼](curriculum.md) · [다음 6주차](week-06.md)

## 연결 주소와 인증서 이름

TCP는 바이트 전달을 담당합니다. TLS는 그 연결 위에서 통신 내용을 보호하고 상대의 신뢰 조건을 검증합니다. 이 실습의 TCP 목적지는 `127.0.0.1`이고, 클라이언트가 인증서에서 확인하는 이름은 `localhost`입니다. [TLS 1.3 명세 RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html)

클라이언트는 서버 인증서를 발급한 CA를 신뢰하는지 확인하고, 인증서의 SAN(Subject Alternative Name)에 접속하려는 이름이 들어 있는지 확인합니다. 예제의 발급자는 임시 CA, SAN 값은 `DNS:localhost`입니다. 임시 CA는 이 실습을 위한 클라이언트 context에 로드됩니다. [TLS 코드](../../examples/network_security/tls.py)

## 신뢰 조건을 하나씩 바꿔 보기

```bash
openssl version
python3 -m examples.network_security tls
```

| TCP 목적지 | 신뢰 CA | 확인할 이름 | 기대 결과 |
|---|---|---|---|
| `127.0.0.1` | 임시 CA 등록 | `localhost` | 허용, 암호화된 채널에서 에코 성공 |
| `127.0.0.1` | 임시 CA 미등록 | `localhost` | 인증서 검증 실패 |
| `127.0.0.1` | 임시 CA 등록 | `wrong.test` | 인증서 이름 검증 실패 |

첫 행은 `accepted (TLSv1.3)`처럼 협상 버전을 표시합니다. 환경에 따라 TLS 1.2가 나올 수 있습니다. 나머지 두 행에서는 `certificate rejected`가 나옵니다. `server_context`가 로드하는 인증서·키와 `client_context`가 로드하는 CA 파일의 역할을 코드에서 찾으세요. 임시 파일은 실행 종료 시 정리됩니다.

**확인 문제.** 같은 IP로 접속해도 `wrong.test`에서 검증이 실패하는 이유는 무엇인가요? TLS의 서버 인증에 성공한 뒤 메모 조회 요청에서 서버가 추가로 확인해야 할 것은 무엇인가요?

**제출물.** 신뢰 조건 세 가지와 실제 결과, 협상한 TLS 버전을 적고, TCP 연결·TLS 핸드셰이크·앱 데이터의 순서를 그림으로 그리세요.
