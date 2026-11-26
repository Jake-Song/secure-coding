# 3주차 패킷과 캡처 읽기

[이전 2주차](week-02.md) · [12주 커리큘럼](curriculum.md) · [다음 4주차](week-04.md)

## 파일 오프셋과 패킷 오프셋

PCAP은 패킷 바이트와 캡처 정보를 담는 파일 형식입니다. 이 샘플은 DNS 질의와 응답을 코드로 만든 **합성 자료**입니다. 파일 전체 헤더 24바이트와 첫 패킷 기록 헤더 16바이트 뒤, 파일 오프셋 40부터 첫 Ethernet 프레임이 시작합니다. [PCAP 생성 코드](../../examples/network_security/pcap.py)

| 계층 | 첫 프레임 안의 시작 위치 | 파일 안의 시작 위치 | 확인할 값 |
|---|---:|---:|---|
| Ethernet | 0 | 40 | EtherType `0x0800` |
| IPv4 | 14 | 54 | 출발지 `192.0.2.10`, 목적지 `192.0.2.53` |
| UDP | 34 | 74 | 출발지 `53000`, 목적지 `53` |
| DNS | 42 | 82 | 트랜잭션 ID `0x1234`, 질문 `service.test` |

IPv4 헤더 첫 바이트 `45`에서 상위 4비트 `4`는 버전, 하위 4비트 `5`는 4바이트 단위의 헤더 길이입니다. 이 샘플에서는 `5 × 4 = 20`바이트 뒤에 UDP 헤더가 있습니다. UDP 헤더는 8바이트이므로 DNS는 프레임 안의 `14 + 20 + 8 = 42`에서 시작합니다.

## 파일로 만들어 직접 읽기

```bash
capture_dir=$(mktemp -d /tmp/network-study.XXXXXX)
python3 -m examples.network_security pcap --output "$capture_dir/dns.pcap"
file "$capture_dir/dns.pcap"
wc -c < "$capture_dir/dns.pcap"
od -An -tx1 -j 82 -N 12 "$capture_dir/dns.pcap"
```

샘플 파일은 `216`바이트이고, `od` 결과는 `12 34 01 00 00 01 00 00 00 00 00 00`입니다. 처음 2바이트는 ID, 그 뒤 2바이트는 플래그, `00 01`은 질문 1개를 나타냅니다. Wireshark가 있다면 파일을 열고 `dns` 표시 필터로 두 행을 확인하세요. 응답의 IP와 UDP 포트는 요청의 반대 방향이고, DNS의 A 응답 값은 `127.0.0.1`, TTL은 `60`입니다. [PCAP 테스트](../../tests/test_network_protocols.py)

**확인 문제.** UDP 목적지 포트 `53`과 DNS 응답 안의 `127.0.0.1`은 각각 무엇을 의미하나요? 파일 오프셋과 프레임 내부 오프셋이 다른 이유를 설명하세요.

**제출물.** 두 프레임의 방향, IPv4·UDP 길이, DNS ID를 표로 적으세요. 어떤 사실을 합성 파일에서 읽었는지, 실제 통신을 관찰하려면 어떤 자료가 필요한지도 적으세요.
