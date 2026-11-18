# 8주차: 바이트 변환과 재구현

[이전: 7주차](week-07.md) · [12주 커리큘럼](../reverse-engineering.md) · [다음: 9주차 파일 형식](../reverse-engineering.md#9주차-파일-형식)

이번 주 목표는 **바이트 변환 알고리즘을 명령어에서 복원하고 Python으로 똑같이 재구현**하는 것입니다. "비슷하게"가 아니라 정상·경계·무작위 입력 모두에서 바이트 단위로 같은 결과를 내야 합니다. 대상은 [08_transform.c](../../examples/reverse_engineering/08_transform.c)의 `08_transform`이며, 비교 도구 [compare_transform.py](../../examples/reverse_engineering/compare_transform.py)를 사용합니다.

이번 대상은 함수 하나만 분석하므로 디버그 빌드를 사용합니다. 대신 **C 소스는 재구현이 비교를 통과할 때까지 열지 않습니다**.

## 1. 학습 순서와 시간

| 단계 | 시간 | 결과 |
|---|---|---|
| C와 Python의 정수 차이 | 1시간 | 폭·부호·나눗셈·시프트 규칙표 |
| 블랙박스 실험 | 1시간 | 입력 한 바이트 변경이 출력에 주는 영향 |
| 명령어에서 알고리즘 복원 | 2시간 | 관용 패턴 해석, 의사 코드 |
| 재구현과 비교 | 2시간 | 21개 비교 입력 일치 |
| 보고서 | 1시간 | 비교표, 실패 원인 기록 |

## 2. 먼저 읽을 개념: C 정수와 Python 정수

Python의 `int`는 크기 제한이 없고, C의 `uint8_t`·`uint32_t`는 고정 폭에서 값이 돌아갑니다. 재구현에서 틀리는 대부분의 원인은 이 차이입니다.

| 항목 | C (기준 환경 GCC, x86-64) | Python에서 같게 만들기 |
|---|---|---|
| `uint8_t` 덧셈 결과 저장 | 2⁸으로 나눈 나머지 | `(a + b) & 0xff` |
| `uint32_t` 곱셈·덧셈 | 2³²로 나눈 나머지 | `(a * b + c) & 0xffffffff` |
| `uint8_t`를 `int8_t`로 변환 | 0x80~0xff는 음수(-128~-1). 표준상 구현 정의, GCC는 2의 보수로 정의 | `b - 256 if b >= 0x80 else b` |
| 음수를 `uint32_t`로 변환 | 2³²을 더한 값(표준 규칙) | `x & 0xffffffff` |
| 정수 나눗셈 `/` | **0 방향으로 버림**: `-1 / 4 == 0`, `-5 / 4 == -1` | `//`는 **아래로 내림**: `-1 // 4 == -1`. `int(a / b)` 또는 부호 처리 |
| 8비트 왼쪽 회전 | `(k << 1) | (k >> 7)`을 8비트로 저장 | `((k << 1) | (k >> 7)) & 0xff` |

나눗셈 행이 가장 많이 틀리는 곳입니다. 양수에서는 C의 `/`와 Python의 `//`가 같아서, 양수만 시험하면 오류를 발견하지 못합니다. 그래서 비교 입력에 0x80 이상 바이트가 반드시 들어가야 합니다.

C의 부호 있는 정수 오버플로는 정의되지 않은 동작이라 Python에서 흉내 낼 기준이 없습니다. 이번 대상은 누적값을 unsigned로 계산하므로 2³² 나머지 규칙만 적용하면 됩니다.

## 3. 실습 A: 블랙박스 실험

```bash
make -C examples/reverse_engineering
cd examples/reverse_engineering/build
printf '' | ./08_transform
printf 'A' | ./08_transform
printf 'B' | ./08_transform
printf 'D' | ./08_transform
printf 'AA' | ./08_transform
printf 'BA' | ./08_transform
head -c 64 /dev/zero | ./08_transform
head -c 65 /dev/zero | ./08_transform; echo "exit=$?"
```

입력은 표준 입력에서 읽으므로 명령행 인자로 넣을 수 없는 **NUL 바이트**도 넣을 수 있습니다. 임의 바이트는 `printf '\x00\x7f\x80\xff'` 또는 다음처럼 파일로 만듭니다.

```bash
python3 -c 'import sys; sys.stdout.buffer.write(bytes([0x00, 0x7f, 0x80, 0xff]))' > edge.bin
./08_transform < edge.bin
```

관찰할 질문과 기록표:

| 질문 | 실험 | 관찰 |
|---|---|---|
| 출력 길이는 입력 길이와 같은가? | 길이 0·1·2·64 | `length=`와 `out=`의 바이트 수 |
| 최대 길이는? | 64·65바이트 | 65바이트는 오류, 종료 코드 2 |
| 한 바이트를 바꾸면 `out`의 어디가 바뀌는가? | `AA`→`BA` | 0번 바이트만 바뀌면 바이트별 독립 변환 |
| 같은 바이트라도 위치에 따라 결과가 다른가? | 64개의 NUL | 위치·키에 의존하는 값이 섞임 |
| `acc`는 입력의 모든 비트를 반영하는가? | `A`·`B`·`D` | `A`와 `B`는 `out`이 달라도 `acc`가 같고, `D`에서 처음 바뀜 |
| 빈 입력의 `acc`는? | `''` | 초기값이 그대로 출력됨 |

`A`(0x41)와 `B`(0x42)의 `acc`가 같다는 관찰은 중요한 단서입니다. 누적값 계산이 입력 바이트의 **하위 비트 일부를 버린다**는 뜻이고, 4절에서 그 연산이 4로 나누기임을 확인합니다. 이런 충돌은 블랙박스 실험에서 미리 찾아 두면 재구현을 검증할 때도 좋은 입력이 됩니다.

64개의 NUL을 넣었을 때 `out`은 **입력과 무관하게 위치에만 의존하는 값**입니다. XOR 기반 변환에서 0바이트를 넣으면 섞이는 키가 그대로 드러나는 경우가 많습니다. 다만 이 변환은 덧셈도 섞여 있어 그 값이 키 자체는 아닙니다. 다음 절에서 확인합니다.

## 4. 실습 B: 명령어에서 알고리즘 복원

```bash
objdump -d -M intel --no-show-raw-insn --disassemble=transform 08_transform
```

인자는 4주차 규칙대로 `rdi`=입력 포인터, `rsi`=길이, `rdx`=출력 포인터입니다. 프롤로그에서 각각 `[rbp-0x28]`, `[rbp-0x30]`, `[rbp-0x38]`에 저장됩니다. 지역 변수와 초기값을 먼저 정리합니다.

| 위치 | 크기 | 초기값 | 역할(가설) |
|---|---|---|---|
| `[rbp-0x13]` | 1바이트 | `0xa7` | 바이트 키 |
| `[rbp-0x10]` | 4바이트 | `0x1234` | 누적값, 마지막에 `eax`로 반환 |
| `[rbp-0x8]` | 8바이트 | 0 | 인덱스, `cmp rax,[rbp-0x30]; jb`로 길이와 비교 |

`-O0` 빌드에서도 GCC는 곱셈·나눗셈을 짧은 명령 조합으로 바꿉니다. 아래는 기준 빌드(GCC 13.3)에서 관찰한 관용 패턴입니다.

| 명령 조합 | 계산 | 확인 방법 |
|---|---|---|
| `mov eax,edx` / `shl eax,0x3` / `sub eax,edx` | `x*8 - x = x*7` | `x=1, 2`를 손으로 대입 |
| `xor al,BYTE PTR [rbp-0x13]` ... `lea edx,[rcx+rsi*1]` / `mov BYTE PTR [rax],dl` | `out[i] = (in[i] ^ key) + i*7`의 하위 8비트 | `dl` 저장 = 8비트 절단 |
| `lea edx,[rax+rax*1]` / `shr al,0x7` / `or eax,edx` / 바이트 저장 | `(key << 1) | (key >> 7)`, 8비트 왼쪽 회전 | `0xa7 → 0x4f → 0x9e` |
| `lea edx,[rax+0x3]` / `test al,al` / `cmovs eax,edx` / `sar al,0x2` / `movsx eax,al` | 부호 있는 8비트 값을 **0 방향으로** 4로 나눔 | 음수면 3을 더한 뒤 산술 시프트 |
| `shl eax,0x5` / `sub eax,edx` | `x*32 - x = x*31` | |
| `add eax,ecx` / `mov DWORD PTR [rbp-0x10],eax` | `acc = acc*31 + q`, 32비트 저장 | |

나눗셈 패턴을 자세히 봅니다. 산술 시프트 `sar`만 쓰면 `-1 >> 2 == -1`로 **아래로 내림**이 됩니다. C의 `/`는 0 방향 버림이어야 하므로, 음수일 때만(`test al,al`이 SF를 세우면 `cmovs`) 먼저 `4-1=3`을 더합니다. `-1 + 3 = 2`, `2 >> 2 = 0`이므로 `-1/4 == 0`이 됩니다. 이 네 명령을 보면 "부호 있는 2의 거듭제곱 나눗셈"을 떠올립니다.

`movzx`(0 확장)와 `movsx`(부호 확장)도 구분합니다. 입력 바이트를 읽을 때는 `movzx`로 unsigned, 나눗셈 결과는 `movsx`로 부호를 보존해 32비트로 넓힙니다.

복원한 의사 코드:

```text
transform(in, n, out):
    key = 0xa7                 ; 8비트
    acc = 0x1234               ; 32비트 unsigned
    for i in 0..n-1:
        out[i] = ((in[i] ^ key) + i*7) mod 2^8
        key    = rotl8(key, 1)
        s      = in[i]을 부호 있는 8비트로 해석
        q      = s / 4  (0 방향 버림)
        acc    = (acc*31 + q) mod 2^32
    return acc
```

### GDB로 반복마다 값 확인

명령어 해석이 맞는지 반복마다 값을 찍어 봅니다. 디버그 정보가 있으므로 `dprintf`를 소스 줄에 둘 수 있습니다. 줄 번호는 `list transform`으로 확인한 **누적값을 갱신하는 줄**을 사용합니다(기준 소스 16번 줄).

```bash
gdb -q ./08_transform
```

```gdb
set pagination off
set disable-randomization off
list transform
dprintf 08_transform.c:16,"i=%lu value=%02x out=%02x next_key=%02x quarter=%d acc_before=%08x\n", index, value, output[index], key, quarter, accumulator
run < edge.bin
```

`edge.bin`(00 7f 80 ff)에 대한 기대 결과입니다. 이 줄이 실행되기 **전**에 멈추므로 `acc_before`는 갱신 전 값, `next_key`는 이미 회전된 다음 키입니다.

```text
i=0 value=00 out=a7 next_key=4f quarter=0 acc_before=00001234
i=1 value=7f out=37 next_key=9e quarter=31 acc_before=0002344c
i=2 value=80 out=2c next_key=3d quarter=-32 acc_before=00445553
i=3 value=ff out=d7 next_key=7a quarter=0 acc_before=084654ed
```

`0xff`(-1)의 `quarter`가 -1이 아니라 0인 것을 확인합니다. `0x80`(-128)은 정확히 나누어떨어져 -32입니다.

## 5. 실습 C: Python 재구현과 비교

재구현 파일을 `notes/private/transform.py`에 만듭니다. 함수 이름과 반환 형식은 비교 도구가 요구하는 대로 맞춥니다.

```python
def transform(data: bytes) -> tuple[bytes, int]:
    """Return (output bytes, 32-bit accumulator) exactly like 08_transform."""
    key = ...
    accumulator = ...
    output = bytearray()
    for index, value in enumerate(data):
        ...
    return bytes(output), accumulator
```

비교 도구는 원본 실행 파일과 재구현에 같은 입력 21개를 넣고 결과를 비교합니다. 고정 입력 11개(빈 입력, NUL, 0x7f·0x80·0xff, ASCII, 음수·양수 나눗셈 경계, 키 회전 한 바퀴를 넘는 9바이트, 0~63, 최대 길이 0xff×64)와 시드를 고정한 무작위 입력 10개입니다.

```bash
python3 examples/reverse_engineering/compare_transform.py \
  examples/reverse_engineering/build/08_transform notes/private/transform.py
```

모두 일치하면 `21/21 matched`와 종료 코드 0입니다. 불일치 행에는 `out`의 첫 번째 다른 바이트 위치나 `acc`의 기대값이 표시됩니다. 불일치 모양으로 원인을 좁힙니다.

| 증상 | 의심할 원인 |
|---|---|
| `out`이 첫 바이트부터 다름 | 키 초기값, XOR와 덧셈 순서 |
| `out`이 1번 바이트부터 다름 | 키 갱신 위치(사용 전/후), 회전 방향 |
| `out` 중간에서 `ValueError: byte must be in range(0, 256)` | `& 0xff` 누락 |
| `out`은 모두 맞고 0x80 이상 입력에서만 `acc` 다름 | 부호 해석 누락 |
| `out`은 맞고 `0xff`·`negative /4 edge`에서만 `acc` 다름 | `//` 사용(내림). 0 방향 버림이 필요 |
| 짧은 입력은 맞고 긴 입력의 `acc`만 다름 | `& 0xffffffff` 누락 또는 위치 |

일부러 틀린 버전을 만들어 위 표를 직접 확인하는 것도 좋은 연습입니다. 예를 들어 0 방향 버림 대신 `//`를 쓰면 `0xff`, `negative /4 edge`, `max 0xff` 등의 `acc`만 `DIFF`가 됩니다.

## 6. 실습 D: 경계 입력 비교표

비교 도구의 21개와 별도로, 자신이 고른 입력 10개 이상으로 원본/재구현 비교표를 만듭니다. 아래 범주를 반드시 포함합니다.

| 범주 | 입력 예 | 확인하는 것 |
|---|---|---|
| 빈 입력 | `b""` | 초기 누적값 |
| 최소 길이 | 1바이트 | 첫 반복 |
| 최대 길이 | 64바이트 | 인덱스 큰 쪽의 `i*7` 절단(63×7=441) |
| 최대 초과 | 65바이트 | 원본은 종료 코드 2. 재구현은 어떻게 처리할지 명세에 적음 |
| NUL 포함 | `b"a\x00b"` | 문자열 함수를 쓰지 않음 |
| 부호 경계 | 0x7f, 0x80 | 양수 최댓값과 음수 최솟값 |
| 나눗셈 경계 | 0xfc~0xff, 0x01~0x04 | -4~-1과 1~4의 버림 |
| 키 주기 | 8·9·16바이트 | 8비트 회전의 주기 8 |

```text
| 입력(hex) | 길이 | 원본 out | 재구현 out | 원본 acc | 재구현 acc | 일치 |
```

`acc`를 비교할 때 원본은 `%08x`로 출력하므로 재구현 값도 같은 형식으로 적습니다.

## 7. 정리: 이 변환이 하지 못하는 것

이번 변환은 분석 연습용입니다. 현대 암호로 해석하지 않습니다.

- 키 스케줄 `0xa7`의 회전은 입력과 무관하므로, 같은 위치에 같은 바이트를 넣으면 항상 같은 출력이 나옵니다.
- `out`은 바이트마다 독립이고 역변환이 쉽습니다: `in[i] = ((out[i] - 7i) & 0xff) ^ key_i`.
- `acc`는 오류 검출용 체크섬처럼 보이지만 `A`·`B`처럼 한 바이트만 달라도 충돌하며, 의도적인 충돌도 쉽게 만들 수 있습니다.

알려진 상수(예: FNV 해시의 `0x811c9dc5`, CRC-32 표)가 보이면 이미 공개된 알고리즘일 가능성을 검토하되, 상수 하나만으로 단정하지 않고 이번 주처럼 재구현 비교로 확인합니다.

## 8. 수정 과제와 제출물

1. 재구현에 역변환 `untransform(output: bytes) -> bytes`를 추가하고, 비교 입력 전부에서 `untransform(transform(x)[0]) == x`를 확인합니다.
2. C 소스 복사본에서 `signed_value / 4`를 `signed_value >> 2`로 바꿉니다. 디스어셈블에서 사라지는 명령을 예측하고, 재구현을 어떻게 바꿔야 하는지 확인합니다. (부호 있는 음수의 오른쪽 시프트 결과는 C 표준에서 구현 정의이며, GCC는 산술 시프트로 정의합니다.)
3. `-O2`로 빌드한 복사본을 디스어셈블합니다. 같은 알고리즘이 어떻게 달라 보이는지 기록하고, 재구현이 그대로 통과하는지 비교 도구로 확인합니다. 최적화 비교는 10주차에서 자세히 다룹니다.

제출물:

- 관용 패턴 해석표와 의사 코드(각 줄에 근거 명령 주소)
- `dprintf` 반복 추적 기록 1개
- `compare_transform.py` 실행 결과 전체와 자신의 비교표(10개 이상)
- 처음 실패했던 재구현이 있다면 그 증상과 원인

자가 점검:

- 모든 중간값에 C 자료형의 폭을 적용했는가? (`& 0xff`, `& 0xffffffff`)
- `0xff`를 넣었을 때 `q`가 0이 되는 이유를 명령어로 설명할 수 있는가?
- `movzx`와 `movsx`가 어떤 값에 쓰였는지 구분했는가?
- 원본이 거부하는 65바이트 입력의 처리를 재구현 명세에 적었는가?

**완료 기준:** 비교 도구가 `21/21 matched`를 출력하고, 자신이 고른 경계 입력 10개 이상에서도 원본과 재구현이 일치하면 통과입니다. 이제 C 소스를 열어 의사 코드와 대조합니다.
