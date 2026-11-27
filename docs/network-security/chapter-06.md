# Chapter 6 메시지 인증과 재전송

[이전 Chapter 5](chapter-05.md) · [네트워크 보안 커리큘럼](curriculum.md) · [다음 Chapter 7](chapter-07.md)

## HMAC, 시간, nonce가 하는 일

HMAC은 공유 키와 메시지 바이트로 MAC 값을 계산합니다. 수신기는 같은 입력으로 계산한 값과 받은 MAC을 비교해, 해당 키를 아는 쪽이 메시지를 인증했는지와 내용이 바뀌었는지를 확인합니다. 기밀성은 TLS 같은 암호화 계층이 담당합니다.

이 예제는 `user`, `timestamp`, `nonce`, `action`, `note`를 정렬된 JSON으로 직렬화해서 HMAC에 넣습니다. 송수신 양쪽이 같은 직렬화 규칙을 써야 같은 값을 계산할 수 있습니다. 수신기는 `hmac.compare_digest`로 결과를 비교합니다. [메시지 인증 코드](../../examples/network_security/auth.py)

시간 검사는 요청이 허용 시간 창 안에 들어오는지 확인합니다. nonce는 이 요청에 부여한 일회용 값입니다. 같은 MAC을 가진 이전 요청도 MAC 자체는 여전히 유효할 수 있으므로, 서버는 인증된 사용자의 nonce 사용 기록을 확인해 중복을 거부합니다. TCP가 전달 과정에서 유실된 데이터를 다시 보내는 동작은 TCP 계층의 복구이고, 여기서 비교하는 것은 앱이 별도의 요청으로 받은 메시지입니다.

## 보호된 검증기에서 세 조건 확인하기

```bash
python3 -m unittest -v \
  tests.test_network_auth.AuthUnitTests.test_replay_fails_but_fresh_nonce_succeeds \
  tests.test_network_auth.AuthUnitTests.test_old_and_future_timestamps \
  tests.test_network_auth.AuthUnitTests.test_nonce_retained_through_future_timestamp_window
```

| 입력 조건 | 예상 결과 |
|---|---|
| 정상 시간, 유효한 MAC, 새 nonce | 성공 |
| 동일 사용자의 이미 처리한 nonce | `replay` |
| 현재 시각과 요청 시각 차이가 30초를 초과 | `expired` |

단위 테스트는 시계를 고정해 시간 경계를 확인합니다. `now=1000`일 때 `970`과 `1030`은 경계 안이고, `969`와 `1031`은 범위 밖입니다. 미래 쪽 경계인 `1030`을 허용한 경우 기록은 그 요청의 허용이 끝나는 `1060`까지 필요합니다. [인증 테스트](../../tests/test_network_auth.py)

**확인 문제.** 동일한 메시지와 유효한 MAC이 도착했을 때 HMAC 비교만으로 이번 요청이 처음 들어왔는지 판단할 수 있나요? 시간과 nonce가 각각 어떤 정보로 이를 보완하나요?

**제출물.** MAC·TLS·시간 창·nonce가 보호하는 속성을 표로 작성하고, 고정 시각 테스트 세 건의 예상과 실제 결과를 적으세요.
