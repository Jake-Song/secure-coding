# 8주차 인증과 객체별 인가

[이전 7주차](week-07.md) · [12주 커리큘럼](curriculum.md) · [다음 9주차](week-09.md)

## 요청의 작성자와 메모의 소유자

네트워크 정책은 연결이 가능한 경로를 정합니다. 연결 안에서 HMAC은 요청을 인증하고, 서버의 소유권 검사는 인증된 작성자가 특정 메모를 읽을 수 있는지 판단합니다. 예제 데이터에서 메모 1은 Alice, 메모 2는 Bob의 소유입니다.

| 서버가 확인하는 조건 | 예상 결과 | 실패 지점 |
|---|---|---|
| Alice가 자기 메모를 요청하고 모든 검사 통과 | 성공 | 해당 없음 |
| 받은 내용과 MAC이 일치하지 않음 | `authentication` | 메시지 인증 |
| Alice의 정상 MAC과 새 nonce가 있고 소유권 없음 | `forbidden` | 객체별 인가 |
| Alice의 정상 MAC과 새 nonce가 있고 객체가 없음 | `forbidden` | 객체 조회와 인가 |

`Verifier.handle`에서 먼저 JSON 필드와 타입을 확인합니다. 다음으로 사용자 키로 MAC을 검증하고 시간·nonce를 확인합니다. 마지막에 `NOTES`에서 객체를 조회한 뒤 기록의 소유자와 인증된 사용자가 같은지 확인합니다. 객체가 없거나 권한이 없으면 같은 응답을 사용합니다. [검증기 코드](../../examples/network_security/auth.py)

## 회귀 테스트로 경계 확인하기

```bash
python3 -m unittest -v \
  tests.test_network_auth.AuthUnitTests.test_valid_signature_and_tamper \
  tests.test_network_auth.AuthUnitTests.test_signed_request_still_needs_authorization \
  tests.test_network_auth.AuthUnitTests.test_invalid_schema_and_non_ascii_mac_fail_cleanly
```

세 테스트가 `OK`이면 정상 인증, 내용 불일치, 권한 거부, 스키마 오류를 각각 처리한 것입니다. 테스트 데이터에서 `user`는 처음에는 클라이언트가 보낸 문자열입니다. 서버가 그 사용자의 키로 MAC을 확인한 뒤에야 소유권 판단에 사용할 수 있습니다. 같은 판단을 웹 앱의 세션과 비교해 보세요. [웹 보안의 객체 접근 제어](../web-security/week-05.md)

**확인 문제.** MAC이 올바른 요청에서 `forbidden`이 반환될 수 있는 이유는 무엇인가요? 출발지 IP가 정책에 맞는다는 사실로 사용자의 소유권까지 알 수 있나요?

**제출물.** 인증과 인가의 결과를 각각 표시한 표와 `스키마 → MAC → 시간·nonce → 소유권` 코드 흐름을 작성하세요.
