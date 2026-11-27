# Chapter 9 자원 제한과 가용성

[이전 Chapter 8](chapter-08.md) · [네트워크 보안 커리큘럼](curriculum.md) · [다음 Chapter 10](chapter-10.md)

## 크기·대기 시간·상태를 각각 제한하기

프레임의 4바이트 길이 필드는 큰 정수도 표현할 수 있습니다. 수신기는 프레임 본문을 기다리기 전에 설정한 상한 `4096`바이트와 길이를 비교합니다. 본문이 선언한 길이에 도달하기 전에 EOF가 오면 `truncated frame`으로 처리합니다. [프레이밍 코드](../../examples/network_security/framing.py)

| 제한 | 예제 값 | 적용 지점 |
|---|---:|---|
| 프레임 본문 최대 크기 | 4096바이트 | 헤더를 읽은 직후, 본문을 읽기 전에 검사 |
| 소켓 timeout | 3초 | 데모 서버 `accept`, 연결의 `recv` 등에서 대기 제한 |
| nonce 저장 한도 | 기본 128개 | 만료된 기록 정리 후 새 nonce를 등록하기 전에 검사 |

`recv_exact`는 본문을 여러 번 읽을 수 있으므로 개별 소켓 작업의 timeout과 한 요청 전체의 마감 시각을 따로 설계해야 합니다. 여러 요청이 함께 도착하는 서비스라면 동시 연결과 사용자별 요청량에도 별도 한도가 필요합니다. [소켓 공통 코드](../../examples/network_security/common.py)

## 작은 입력으로 경계값 검증하기

```bash
python3 -m unittest -v \
  tests.test_network_protocols.FramingUnitTests.test_split_header_body_empty_binary_and_limit \
  tests.test_network_protocols.FramingUnitTests.test_truncation_and_oversized_prefix \
  tests.test_network_auth.AuthUnitTests.test_nonce_cache_is_bounded_and_fails_closed \
  tests.test_network_auth.AuthUnitTests.test_concurrent_replay_only_one_request_succeeds
```

초과 길이 검사는 선언한 길이만 담은 메모리 입력으로 확인합니다. 저장소 한도 테스트는 `max_nonces=1`로 줄여 한 건이 저장된 직후 두 번째 새 요청이 `nonce_capacity`로 거부되는지 확인합니다. 중복 검사는 확인과 등록을 같은 잠금 구간에 두어 하나의 nonce로 여러 요청이 동시에 처리되는 상황을 막습니다. [검증기 코드](../../examples/network_security/auth.py)

메모리 저장소는 프로세스 수명 동안 유지됩니다. 재시작 후에도 차단 기록을 유지하거나 여러 서버가 공유해야 한다면 만료와 원자적 등록을 지원하는 저장소를 설계해야 합니다.

**확인 문제.** 저장 공간이 가득 찼을 때 아직 유효한 nonce 기록을 지워 자리를 만든다면 어떤 판단을 다시 내리게 되나요? 개별 읽기 timeout만 있을 때 요청 전체의 최대 시간을 어떻게 정할 수 있나요?

**제출물.** 크기·시간·상태 한도별로 검사 순서, 통과·거부 경계값, 해당 한도가 다루지 못하는 운영 조건을 적으세요.
