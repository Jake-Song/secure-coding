# 4주차 UDP·DNS와 응답 검증

[이전 3주차](week-03.md) · [12주 커리큘럼](curriculum.md) · [다음 5주차](week-05.md)

## 한 질문과 한 응답 연결하기

DNS 메시지는 12바이트 헤더로 시작하고, 질문 영역에는 이름·타입·클래스가 들어갑니다. 예제는 `IN A` 질문만 처리합니다. 응답의 압축 이름 `c0 0c`는 DNS 메시지 시작에서 12바이트 떨어진 이름을 가리킵니다. 이 메시지에서는 질문 영역의 이름을 재사용합니다. [DNS 메시지 형식 RFC 1035](https://www.rfc-editor.org/rfc/rfc1035.html#section-4.1)

로컬 서버가 `service.test`를 알면 A 레코드에 `127.0.0.1`을 담아 돌려줍니다. `missing.test`에는 DNS 응답 코드 `3`인 NXDOMAIN을 반환합니다. 예제 클라이언트는 이를 Python의 `None`으로 표현합니다. 응답을 받지 못해 기다리다 실패하는 경우에는 소켓 timeout이 발생합니다. [DNS 코드](../../examples/network_security/dns.py)

## 정상 응답과 거부 조건 확인하기

```bash
python3 - <<'PY'
from examples.network_security.dns import lookup

print("service.test", lookup("service.test"))
print("missing.test", lookup("missing.test"))
PY
python3 -m unittest tests.test_network_protocols.DNSUnitTests.test_id_name_and_response_bit_must_match -v
```

앞의 두 줄은 `service.test 127.0.0.1`, `missing.test None`입니다. `lookup`의 UDP 소켓은 지정된 서버의 IP·포트를 상대 endpoint로 설정합니다. 응답이 오면 `parse`가 형식을 읽고 `validate_response`가 세 조건을 검사합니다. 응답 비트가 설정돼 있어야 하고, 트랜잭션 ID와 질문 이름이 원래 요청과 같아야 합니다. 클래스와 타입은 이 제한된 파서에서 정해진 `IN A` 형식으로 검사합니다.

테스트는 메모리 안에서 응답 비트·ID·이름이 맞지 않는 경우를 거부하는지 확인합니다. 이 검사로 요청과 응답의 일치를 판단할 수 있습니다. DNS 데이터의 출처와 무결성을 암호학적으로 확인하려면 DNSSEC 같은 별도 검증이 필요합니다. [DNS 테스트](../../tests/test_network_protocols.py)

**확인 문제.** 같은 서버에서 이전 질문의 응답이 왔다면 어떤 값으로 현재 질문과 구분하나요? NXDOMAIN과 timeout은 관찰 결과가 어떻게 다른가요?

**제출물.** `정상 A 응답·NXDOMAIN·응답 불일치·응답 대기 시간 초과`를 표로 비교하고, UDP 소켓과 DNS 검사 함수가 각각 확인하는 조건을 표시하세요.
