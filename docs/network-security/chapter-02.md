# Chapter 2 TCP와 메시지 경계

[이전 Chapter 1](chapter-01.md) · [네트워크 보안 커리큘럼](curriculum.md) · [다음 Chapter 3](chapter-03.md)

## 바이트 스트림에서 메시지 꺼내기

TCP는 수신 앱에 순서가 보존된 바이트 스트림을 제공합니다. 전송 쪽이 `HELLO`와 `WORLD`를 따로 쓰더라도 받는 앱은 `HEL`, `LOWORLD`로 나눠 읽을 수 있습니다. 연결을 유지하면서 두 메시지를 구분하려면 앱이 길이 접두사나 구분자를 정합니다. [TCP 명세 RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html#section-2.2)

이 실습의 프레임은 **4바이트 big-endian 길이 + 길이만큼의 본문**입니다. `b"hi"`는 `00 00 00 02 68 69`로 기록됩니다. 앞의 4바이트는 정수 `2`, 뒤의 `68 69`는 `h`, `i`의 바이트입니다. `안`처럼 한글 한 글자도 UTF-8에서는 3바이트이므로 헤더에는 글자 수 대신 인코딩한 바이트 수를 기록합니다. [프레이밍 코드](../../examples/network_security/framing.py)

## 합쳐 보낸 경우와 나눠 보낸 경우

```bash
python3 -m examples.network_security framing
python3 -m unittest tests.test_network_protocols.FramingUnitTests -v
```

```text
TCP: fragmented_writes=False, 3 frames OK
TCP: fragmented_writes=True, 3 frames OK
TCP: oversized payload rejected (frame too large)
```

첫 번째 실행은 빈 메시지, `hello`, `안녕하세요`의 프레임을 이어 보냅니다. 두 번째 실행은 같은 바이트열을 3바이트 단위로 쓰고 수신기가 같은 세 메시지를 복원하는지 확인합니다. 커널이 선택한 실제 TCP 세그먼트 크기는 별도의 패킷 관찰 대상입니다.

`recv_frame`이 `recv_exact`로 먼저 4바이트를 읽고, 길이 상한을 검사한 뒤 본문을 읽는 순서를 따라가세요. 단위 테스트의 `FragmentedReader`는 한 번에 1바이트씩 반환해 부분 읽기를 확실하게 만들 수 있습니다. [프레이밍 테스트](../../tests/test_network_protocols.py)

**확인 문제.** `recv(4)`가 2바이트를 돌려줬을 때 다음 읽기는 몇 바이트를 요청해야 하나요? 4바이트가 완성되기 전에 EOF가 오면 어떻게 처리하나요?

**제출물.** 빈 프레임과 `hi`의 바이트 배열을 적고, 붙어 온 두 프레임·잘린 헤더·잘린 본문·상한 초과에서 기대하는 결과를 표로 작성하세요.
