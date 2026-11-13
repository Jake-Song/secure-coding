# 네트워크 보안 실습 실행 안내

모든 명령은 **저장소 루트**에서 실행합니다. Python 표준 라이브러리만 사용하며 TLS에는 OpenSSL CLI가 필요합니다. loopback 소켓을 사용할 수 있는 환경이어야 합니다. 예제는 임시 포트에서 서버와 클라이언트를 함께 실행한 뒤 종료합니다.

```bash
python3 -m examples.network_security --help
python3 -m examples.network_security all
```

아래 여섯 실습 중 DNS 실습은 `dns`와 `pcap` 두 명령으로 나뉩니다. `all`은 PCAP을 메모리에서 생성해 요약만 출력합니다. 파일 저장은 `pcap --output`으로 명시해야 합니다.

## 실습 1 TCP 프레이밍

코드: [framing.py](../examples/network_security/framing.py)의 `encode_frame`, `recv_exact`, `recv_frame`, `exchange_frames`.

```bash
python3 -m examples.network_security framing
```

기대 출력:

```text
TCP: fragmented_writes=False, 3 frames OK
TCP: fragmented_writes=True, 3 frames OK
TCP: oversized payload rejected (frame too large)
```

형식은 `[길이: 4바이트 big-endian][payload: 길이만큼]`이며 payload 상한은 4096바이트입니다. 빈 프레임도 허용합니다. 첫 실행은 여러 프레임을 합쳐 쓰고, 두 번째는 전체 바이트열을 3바이트씩 나눠 씁니다. 둘 다 세 메시지를 원형대로 받아야 합니다. 쓰기 단위가 TCP 패킷 또는 `recv` 호출과 대응한다고 해석하지 않습니다.

직접 해 볼 것:

1. `messages`에 다른 한글 문자열을 추가하고 글자 수와 UTF-8 바이트 수를 비교합니다.
2. 테스트의 `FragmentedReader`에서 수신 한도를 1·2·5바이트로 바꿔 같은 결과를 확인합니다.
3. `recv_frame`의 상한 검사가 payload 읽기보다 먼저 실행되는 이유를 적습니다. 크기 검사를 제거하지 않고 경계값을 테스트합니다.

잘린 헤더·본문, 두 프레임이 붙은 입력, 정확히 4096바이트, 초과 길이는 테스트에서 확인합니다.

## 실습 2 UDP DNS와 PCAP

코드: [dns.py](../examples/network_security/dns.py)의 `make_query`, `parse`, `make_response`, `validate_response`, `lookup`; [pcap.py](../examples/network_security/pcap.py).

```bash
python3 -m examples.network_security dns
capture_dir=$(mktemp -d /tmp/network-capture.XXXXXX)
python3 -m examples.network_security pcap --output "$capture_dir/dns.pcap"
file "$capture_dir/dns.pcap"
```

DNS 기대 결과:

```text
DNS: service.test -> 127.0.0.1
DNS: missing.test -> None (NXDOMAIN)
DNS: mismatched transaction rejected (response does not match query)
```

`service.test`는 외부 DNS에 등록하거나 질의하지 않습니다. 로컬 UDP 서버가 아는 이름 하나입니다. 클라이언트는 지정한 loopback 주소·포트로 UDP를 연결하고 응답 ID·질문·형식을 검사합니다. NXDOMAIN은 Python의 `None`으로 표현합니다. 불일치 ID 사례는 수신한 바이트의 검사 함수에 직접 넣는 예제이며 네트워크 위조 패킷을 보내지 않습니다.

PCAP은 **실제 캡처가 아닌, 코드로 생성한 DNS 질의·응답 2패킷**입니다. 파일에는 Ethernet·IPv4·UDP 헤더와 체크섬이 있습니다. 문서 전용 주소 `192.0.2.10`→`192.0.2.53`, 클라이언트 포트53000→DNS 포트53을 사용합니다. DNS 응답의 A 값은 `127.0.0.1`입니다. 파일의 주소를 실제 loopback 소켓 주소와 혼동하지 않습니다.

Wireshark가 준비되어 있다면 File → Open으로 생성한 파일을 열고 display filter `dns`를 적용합니다. Transaction ID `0x1234`, 질문 `service.test`, 요청·응답 방향, A 값, TTL 60을 확인합니다. Wireshark GUI는 작성 환경에서 실행 확인하지 않았으며, 자동 테스트는 PCAP 구조·IP/UDP 체크섬·DNS 내용 일치를 검증합니다.

직접 해 볼 것: DNS의 12바이트 헤더를 해석하고 압축 포인터 `c0 0c`가 가리키는 위치를 찾습니다. 잘린 패킷·순환 포인터·질문 불일치가 거부되는 테스트를 읽습니다. 이 파서는 교육용 제한 구현으로 일반 DNS 리졸버에 사용하지 않습니다.

## 실습 3 TLS와 인증서

코드: [tls.py](../examples/network_security/tls.py)의 `create_certificates`, `client_context`, `server_context`, `exchange`.

```bash
openssl version
python3 -m examples.network_security tls
```

기대 출력 예:

```text
TLS: trusted CA + localhost -> accepted (TLSv1.3)
TLS: untrusted CA -> certificate rejected
TLS: hostname mismatch -> certificate rejected
```

협상 버전은 환경에 따라 TLS 1.2 또는 1.3일 수 있습니다. 코드는 TLS 1.2 이상을 허용합니다.

데모는 유효기간 2일의 임시 CA와 별도 서버 인증서를 생성합니다. 서버 SAN은 `DNS:localhost`이며, 클라이언트 한 개의 SSL context에만 CA를 추가합니다. 시스템 CA 저장소를 변경하지 않고, 종료하면 임시 인증서와 키가 삭제됩니다. 검증을 끄는 context는 사용하지 않습니다.

직접 해 볼 것:

1. 연결 IP는 같아도 `server_hostname="wrong.test"`가 거부되는 이유를 설명합니다.
2. 테스트에서 최대 TLS 버전을 1.2로 지정한 경우를 확인합니다.
3. TLS의 서버 인증이 애플리케이션 사용자 인증·메모 소유권 검사까지 대신하지 않는 이유를 적습니다.

오류가 `openssl 실행 파일이 필요합니다`라면 TLS만 실행할 수 없는 상태입니다. `PermissionError`가 소켓 생성에서 발생하면 실행 환경의 네트워크 권한을 확인합니다. 인증서 오류를 해결하려고 검증을 끄지 말고 CA·호스트명·시간을 확인합니다.

## 실습 4 메시지 인증 재전송 인가

코드: [auth.py](../examples/network_security/auth.py)의 `sign`, `Verifier.handle`, `exchange`.

```bash
python3 -m examples.network_security auth
```

기대 출력:

```text
AUTH: MAC-only replay -> [True, True]
AUTH: MAC + freshness -> ['accepted', 'replay']
AUTH: tampered / other owner's note / stale -> ['authentication', 'forbidden', 'expired']
```

요청은 `user`, `timestamp`, `nonce`, `action`, `note`, `mac` 필드가 있는 JSON입니다. MAC은 `mac`을 제외한 모든 필드를 정렬·고정 형식으로 직렬화한 바이트에 HMAC-SHA256을 적용합니다. 필드 순서나 공백 표현의 차이를 의미 변화와 구분합니다. MAC 비교에는 `hmac.compare_digest`를 사용합니다.

| 입력 | 결과 | 이유 |
|---|---|---|
| Alice 키·본인 메모·정상 시간·새 nonce | accepted | 정상 요청 |
| 똑같은 유효 요청 재사용 | replay | 이미 사용한 nonce |
| 서명 이후 메모 번호 변경 | authentication | 메시지와 MAC 불일치 |
| Alice가 Bob 메모2를 올바르게 서명해 요청 | forbidden | 인증은 성공했지만 소유권 없음 |
| 60초 전 timestamp로 올바르게 서명 | expired | 허용 시간 창 ±30초 밖 |

nonce는 인증된 사용자와 묶어서 보관하며, 동시에 동일 요청이 들어와도 하나만 성공하도록 잠금으로 검사·등록합니다. timestamp가 현재보다 앞선 요청도 유효기간 전체에 걸쳐 nonce를 보존합니다. 최대128개가 저장되면 새 요청을 거부합니다. 거부 요청도 MAC·시간 검증을 통과했다면 nonce를 소비할 수 있습니다.

데모 키는 매 실행마다 무작위 생성하고 출력·저장하지 않습니다. 이 예제의 TCP 전송은 평문이므로 MAC이 있어도 내용은 보입니다. 운영용 키 배포·회전·TLS 결합·재시작 후 재전송 차단은 별도 설계가 필요합니다.

직접 해 볼 것: `freshness=False`가 MAC 검사를 끄는 것이 아님을 확인합니다. timestamp만 검사하고 nonce 검사를 하지 않으면 시간 창 안의 재전송에 어떤 결과가 나올지 설명합니다. 제공 테스트의 오래된 요청, 미래 시각 경계, 동시 재전송, 저장 한도 사례를 실행합니다.

## 실습 5 접근 정책 모델

코드: [policy.py](../examples/network_security/policy.py)의 `Flow`, `Rule`, `allowed`.

```bash
python3 -m examples.network_security policy
```

기대 결과: `client -> web HTTPS`, `web -> database`는 ALLOW, `client -> database`, `client -> web SSH`, `client -> web UDP/443`은 DENY입니다.

주소와 역할:

| 역할 | 주소 | 허용된 요청 |
|---|---|---|
| 클라이언트 구역 | `192.0.2.0/24` | 웹 서버 TCP/443 |
| 웹 서버 | `198.51.100.10` | DB 서버 TCP/5432 |
| DB 서버 | `203.0.113.20` | 제공 모델에서 새 아웃바운드 요청 없음 |

문서 전용 주소를 사용한 **오프라인 허용 목록 모델**입니다. 실제 방화벽 규칙이나 인터페이스·라우팅을 변경하지 않으며 해당 주소로 패킷을 보내지 않습니다. 요청 방향만 판단하므로 연결의 응답 트래픽을 허용하는 상태 기반 방화벽과 다릅니다.

직접 해 볼 것: 목적지·포트·프로토콜을 하나씩 바꾸어 기대 결과를 먼저 적습니다. 새 규칙 하나를 추가하면 어떤 경로가 더 열리는지 표로 비교합니다. 운영체제 방화벽 적용은 별도 격리 실습으로 남깁니다.

## 실습 6 로그와 탐지

코드: [detection.py](../examples/network_security/detection.py)의 `load_events`, `detect`; 입력: [events.jsonl](../examples/network_security/events.jsonl).

```bash
python3 -m examples.network_security detection
```

기대 결과: 10개 이벤트에서 2개 경보가 나옵니다.

- 시간4, `192.0.2.50`→`198.51.100.10`: 서로 다른 거부 포트4개인 `many_denied_ports`.
- 시간7, `192.0.2.60`→`198.51.100.10`: 인증 실패3회인 `repeated_auth_failures`.

입력은 합성 로그입니다. `time`은 초 단위 숫자이며 샘플은 시간0을 기준으로 한 상대 시각입니다. 실제 데이터를 넣을 때도 같은 시각 기준과 단위를 유지합니다. 형식·시간 정렬·행 길이·최대10000행을 검사합니다. 동일 source·destination 쌍별 `[현재 시각 - 10, 현재 시각]` 창에서 집계하며 경계 시각을 포함합니다.

자신의 사본에서 시간·포트·이벤트를 바꿔 비교합니다.

```bash
log_dir=$(mktemp -d /tmp/network-log.XXXXXX)
cp examples/network_security/events.jsonl "$log_dir/events.jsonl"
# 편집기로 위 사본을 수정한 뒤 실행
python3 -m examples.network_security detection --events "$log_dir/events.jsonl"
```

직접 해 볼 것: 모든 거부 포트를22로 바꾸면 고유 포트 경보가 사라지는지, 간격을20초로 벌리면 시간 창 경보가 사라지는지 확인합니다. NAT로 여러 사용자가 한 IP로 보이는 경우의 오탐과 느린 스캔의 미탐을 기록합니다. IP와 포트만으로 실제 공격자나 공격 성공을 확정하지 않습니다.

## 테스트 실행

신규 실습의 전체 테스트:

```bash
python3 -m unittest tests.test_network_protocols tests.test_network_auth tests.test_network_tls tests.test_network_policy -v
```

소켓·OpenSSL 없이 가능한 부분만 검사하려면:

```bash
python3 -m unittest tests.test_network_protocols.FramingUnitTests tests.test_network_protocols.DNSUnitTests tests.test_network_protocols.PcapTests tests.test_network_auth.AuthUnitTests tests.test_network_policy -v
```

각각 36개와 27개 테스트입니다. 첫 명령에는 실제 TCP·UDP·TLS 연결과 OpenSSL 인증서 생성이 포함됩니다. 두 번째 명령의 통과를 실제 통신 검증으로 해석하지 않습니다. 전체 저장소 회귀 테스트는 기존 가상환경에서 `python -m unittest discover -s tests -v`로 실행합니다.
