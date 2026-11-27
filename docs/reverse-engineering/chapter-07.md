# Chapter 7: 입력 검증 로직 복원

[이전: Chapter 6](chapter-06.md) · [역엔지니어링 커리큘럼](curriculum.md) · [다음: Chapter 8](chapter-08.md)

이 Chapter 목표는 **여러 단계로 입력을 검사하는 함수의 수락 조건을 완전히 복원**하고, 그 조건을 만족하는 입력을 계산으로 만들어 내는 것입니다. 대상은 `07_validate_stripped`입니다. 소스 [07_validate.c](../../examples/reverse_engineering/07_validate.c)는 8절에서 대조할 때까지 열지 않습니다.

수락 조건을 알아내는 것과 디버거로 실행 중 값을 바꿔 출력만 바꾸는 것은 다른 일입니다. 이 Chapter에는 두 가지를 모두 해 보고 보고서에서 분명히 구분합니다.

## 1. 학습 순서와 시간

| 단계 | 시간 | 결과 |
|---|---|---|
| 블랙박스 관찰 | 0.5시간 | 출력·종료 코드, 질문 정하기 |
| 검사 함수 찾기와 단계 분리 | 2시간 | 거부 경로마다 조건과 반환값 |
| 단계별 조건 복원 | 2시간 | 길이·문자 범위·변환·누적값 의사 코드 |
| 입력 생성기 | 1.5시간 | 수락 입력 생성과 실제 실행 검증 |
| 실패 조건·보고서 | 1시간 | 거부 입력별 실패 단계 표 |

## 2. 먼저 읽을 개념: 검사 함수의 전형적 모양

입력 검증 함수는 보통 **앞 단계가 실패하면 즉시 반환**합니다. 그래서 디스어셈블에는 서로 다른 상수를 반환하는 짧은 블록이 여러 개 있고, 모두 하나의 함수 끝으로 모입니다.

```text
검사 1 실패 → mov eax, 1 → 끝으로 jmp
검사 2 실패 → mov eax, 2 → 끝으로 jmp
...
모두 통과   → mov eax, 0 → 끝
```

이런 함수를 만나면 **반환 상수마다 그 블록에 도달하는 조건**을 표로 정리합니다. 표가 완성되면 그 역이 수락 조건입니다.

| 단계 | 흔한 구현 | 디스어셈블 단서 |
|---|---|---|
| 길이 | `strlen` 결과 비교 | `call strlen` 다음 `cmp rax, 상수` |
| 문자 범위 | 각 바이트를 범위 상수와 비교 | 루프 안 `cmp BYTE PTR ..., 0x60`/`0x7a`/`0x2f`/`0x39` 등 ASCII 경계 |
| 바이트 변환 | XOR·덧셈·곱셈 후 표와 비교 | `.rodata` 표 주소를 읽는 `lea`, 바이트 비교 `cmp al, dl` |
| 누적값 | 루프로 합·곱·해시 계산 후 상수와 비교 | 루프 뒤 `cmp eax, 큰 상수` |

ASCII 경계값은 외워 두면 편합니다. `0x2f` 다음이 `'0'`(0x30), `0x39`는 `'9'`, `0x40` 다음이 `'A'`(0x41), `0x5a`는 `'Z'`, `0x60` 다음이 `'a'`(0x61), `0x7a`는 `'z'`입니다. `cmp x,0x60; jbe 실패`는 "x가 0x60 이하이면 실패", 즉 `x >= 'a'`를 요구한다는 뜻입니다.

## 3. 실습 A: 블랙박스 관찰

```bash
make -C examples/reverse_engineering
cd examples/reverse_engineering/build
for key in "" a abcdefgh ABCDEFGH abcdefghi 12345678 'abcd efg'; do
  printf '%-12s ' "[$key]"; ./07_validate_stripped "$key"; echo "  exit=$?"
done
./07_validate_stripped; echo "exit=$?"
strings -a 07_validate_stripped | grep -vE '^[._]|GLIBC|gcc|GCC'
```

출력은 `accepted`/`rejected`, 종료 코드는 0/1, 인자 개수가 틀리면 2입니다. 출력만으로는 **어느 단계에서 거부됐는지 알 수 없습니다**. 그래서 내부 반환값을 봐야 합니다.

`strings` 결과에 수락 키처럼 보이는 문자열이 있는지 기록합니다. 기준 빌드에서는 `6>>v.` 같은 짧은 조각이 보였습니다. 이것이 키인지, 키를 변환한 표인지, 우연히 출력 가능한 바이트인지는 **참조와 사용 방식**을 확인하기 전까지 알 수 없습니다. Chapter 1의 `strcmp(input, "trace")`와 달리, 이번에는 비교 대상이 문자열 그대로 저장돼 있지 않을 수 있습니다.

## 4. 실습 B: 검사 함수 찾기와 단계 분리

Chapter 5 방법으로 `rejected` 문자열의 참조에서 `main`을 찾고, `puts` 직전 분기를 결정하는 `call`을 찾습니다. 그 호출 대상이 검사 함수입니다. Ghidra에서는 `check_key` 같은 이름을 붙이고, CLI로는 다음처럼 범위를 좁힙니다.

```bash
objdump -d -M intel 07_validate_stripped > validate.asm
grep -nE 'call|cmp |mov +eax,0x[0-9]$' validate.asm
```

기준 빌드의 검사 함수는 `0x1232`에서 시작했습니다. 그 함수의 반환 상수 블록을 찾아 다음 표를 채웁니다. 주소는 자기 결과를 씁니다.

| 반환값 | 블록 주소 | 도달 조건(직전 비교와 분기) | 의미(가설) |
|---|---|---|---|
| 1 | | `call strlen` 결과와 `cmp rax,0x8`, `je` 실패 | 길이 ≠ 8 |
| 2 | | 바이트마다 호출하는 작은 함수의 결과가 0 | 허용 문자가 아님 |
| 3 | | 바이트 변환 결과와 `.rodata` 표 바이트가 다름 | 앞부분 불일치 |
| 4 | | 다른 함수의 반환값과 `cmp eax,edx`(`edx`=상수) | 누적값 불일치 |
| 0 | | 위를 모두 통과 | 수락 |

`main`이 이 반환값을 0과만 비교한다는 사실도 확인합니다(`test eax,eax`). 즉 1~4의 구분은 출력에 드러나지 않는 내부 정보입니다.

### GDB로 실패 단계 확인

Chapter 6 방법으로 실행 중 반환값을 봅니다. 디버그 빌드는 이름으로, strip 파일은 `$base + 0x1232`로 중단합니다.

```bash
cat > notes/private/week07-stage.gdb <<'EOF'
set pagination off
set disable-randomization off
break check_key
run
finish
print $eax
continue
EOF
for key in abcdefg Abcdefgh abcdefgh; do
  echo "== $key"
  gdb -q -batch -x notes/private/week07-stage.gdb \
    --args examples/reverse_engineering/build/07_validate "$key" | grep -E '^\$|accepted|rejected'
done
```

`notes/private/`가 없으면 먼저 `mkdir -p notes/private`를 실행합니다. 명령은 저장소 루트에서 실행합니다. 디버그 빌드를 쓰는 것은 실패 단계를 빠르게 보기 위해서이며, 조건 자체는 strip 파일의 명령어에서 복원합니다.

## 5. 실습 C: 단계별 조건 복원

### 단계 2: 허용 문자

바이트마다 호출되는 작은 함수에는 비교 네 개가 있습니다.

```text
cmp BYTE PTR [rbp-0x4],0x60 ; jbe 다음검사
cmp BYTE PTR [rbp-0x4],0x7a ; jbe 참
다음검사:
cmp BYTE PTR [rbp-0x4],0x2f ; jbe 거짓
cmp BYTE PTR [rbp-0x4],0x39 ; ja  거짓
참: mov eax,1
```

화살표를 따라가면 `('a' <= c <= 'z') || ('0' <= c <= '9')`입니다. `jbe`/`ja`이므로 unsigned 비교이고, 0x80 이상의 바이트(UTF-8의 한글 바이트 등)는 모두 거부됩니다. 루프 종료 비교 `cmp ...,0x7; jbe`는 인덱스 0~7, 즉 8바이트 전체를 검사한다는 뜻입니다.

### 단계 3: 바이트 변환과 표

변환 함수는 두 인자(바이트, 인덱스)를 받습니다.

```text
movzx eax,BYTE PTR [rbp-0x4]   ; c
xor   eax,0x5a                 ; c ^ 0x5a
mov   ecx,인덱스
add   eax,eax / add eax,ecx    ; 인덱스*2 + 인덱스 = 인덱스*3
add   eax,edx                  ; (c ^ 0x5a) + 인덱스*3
```

호출한 쪽은 결과의 하위 8비트(`al`)를 `.rodata` 표의 바이트(`dl`)와 비교합니다. 그래서 변환은 **8비트로 잘린 값**입니다. 루프 종료 비교 `cmp ...,0x3; jbe`는 앞 4바이트만 검사한다는 뜻입니다. 표의 위치는 `lea rcx,[rip+...]`의 대상이며 내용을 확인합니다.

```bash
objdump -s -j .rodata 07_validate_stripped
```

변환이 XOR과 덧셈이므로 역변환이 가능합니다.

```text
code = ((c ^ 0x5a) + 3*i) & 0xff
c    = ((code - 3*i) & 0xff) ^ 0x5a
```

표의 4바이트를 역변환하면 앞 4글자가 정해집니다. 직접 계산한 뒤 Python으로 확인합니다.

```bash
python3 -c 'code = bytes.fromhex("자신이_찾은_표_8자리_16진수"); print(bytes(((b - 3*i) & 0xff) ^ 0x5a for i, b in enumerate(code)))'
```

### 단계 4: 가중 합

```text
movzx eax,BYTE PTR [rax]       ; key[i]
mov   rdx,i ; add edx,0x1      ; i + 1
imul  eax,edx                  ; key[i] * (i+1)
add   DWORD PTR [rbp-0xc],eax  ; total += ...
cmp   QWORD PTR [rbp-0x8],0x7 ; jbe   ; i = 0..7
...
mov   edx,상수 ; cmp eax,edx   ; total == 상수 ?
```

`total`은 32비트 unsigned 누적값입니다. 이번 입력은 8바이트이고 바이트 최댓값이 255이므로 합이 32비트를 넘지 않습니다. 그래도 일반적인 재구현에서는 Chapter 8처럼 `& 0xffffffff`를 고려합니다.

### 수락 조건 의사 코드

```text
check_key(s):
    if strlen(s) != 8:                         return 1
    for i in 0..7:  if s[i] not in [a-z0-9]:   return 2
    for i in 0..3:  if ((s[i]^0x5a)+3i)&0xff != TABLE[i]: return 3
    if sum(s[i] * (i+1) for i in 0..7) != TARGET: return 4
    return 0
```

`TABLE`과 `TARGET`은 자기 분석에서 찾은 값으로 채웁니다.

## 6. 실습 D: 입력 생성기

앞 4글자는 표에서 정해지고, 뒤 4글자는 가중 합 조건 하나만 만족하면 됩니다. 조건이 하나뿐이므로 해가 여러 개입니다. 아래 틀의 빈 값을 자신의 분석 결과로 채웁니다.

```python
"""week07 key generator: fill the constants from your own analysis."""
import itertools
import string
import subprocess
import sys

TABLE = bytes.fromhex("________")  # .rodata의 4바이트
XOR_KEY = 0x__
STEP = _
TARGET = ____
ALLOWED = (string.ascii_lowercase + string.digits).encode()

prefix = bytes(((code - STEP * i) & 0xFF) ^ XOR_KEY for i, code in enumerate(TABLE))
assert all(c in ALLOWED for c in prefix), prefix
partial = sum(c * (i + 1) for i, c in enumerate(prefix))

def suffixes():
    for a, b, c in itertools.product(ALLOWED, repeat=3):
        rest = TARGET - partial - (a * 5 + b * 6 + c * 7)
        if rest % 8 == 0 and rest // 8 in ALLOWED:
            yield bytes([a, b, c, rest // 8])

keys = [prefix + tail for tail in suffixes()]
print(f"accepted keys: {len(keys)}")
binary = sys.argv[1]
for key in keys[:5] + keys[-5:]:
    result = subprocess.run([binary, key.decode()], capture_output=True, text=True)
    print(key.decode(), result.stdout.strip(), result.returncode)
```

```bash
python3 notes/private/week07_keygen.py examples/reverse_engineering/build/07_validate_stripped
```

마지막 글자를 반복으로 찾지 않고 `rest // 8`로 **계산**한다는 점이 핵심입니다. 4글자 전체를 무작위로 시도하면 36⁴ ≈ 168만 번이지만, 이 방식은 36³ ≈ 4.7만 번이면 모든 해를 셉니다.

생성한 키는 반드시 원본 실행 파일로 확인합니다. 생성기의 계산이 맞아도 분석이 틀렸다면 원본은 거부합니다.

## 7. 실습 E: 실패 조건과 실행 중 값 변경

### 거부 입력 표

수락 입력 하나(`K`라고 부릅니다)에서 출발해 한 가지씩 바꿉니다. 실행 전에 실패 단계를 예측하고, 4절의 GDB 스크립트로 확인합니다.

| 입력 | 바꾼 것 | 예측 단계 | 관찰 단계 | 근거 명령 |
|---|---|---|---|---|
| `K`의 앞 7글자 | 길이 부족 | 1 | | |
| `K` + `x` | 길이 초과 | 1 | | |
| 첫 글자를 대문자로 | 허용 범위 밖 | 2 | | |
| 마지막 글자를 `-`로 | 허용 범위 밖 | 2 | | |
| 첫 글자를 다른 소문자로 | 앞부분 표 불일치 | 3 | | |
| 마지막 글자를 다른 소문자로 | 가중 합 불일치 | 4 | | |
| 뒤 4글자 중 둘의 순서 교환 | 가중치가 달라짐 | 대부분 4 | | |
| 빈 문자열 `""` | 길이 0 | 1 | | |
| `K`의 마지막 글자 대신 `한` | UTF-8로 3바이트 | 1 | | |

마지막 행은 화면의 글자 수(8)가 아니라 **바이트 수**(10)로 길이를 검사한다는 점을 보여 줍니다. 순서 교환은 두 글자가 같거나 가중 합 차이가 우연히 0이 되는 경우 수락될 수도 있으므로 "대부분"이라고 적었습니다. 실제로 그런 예가 있는지 생성기로 찾아봅니다.

### 실행 중 값 변경은 수락 조건이 아니다

GDB로 검사 함수의 반환값을 바꾸면 틀린 입력에도 `accepted`가 출력됩니다.

```gdb
set disable-randomization off
break check_key
run wrongkey
finish
print $eax
set var $rax = 0
continue
```

`wrongkey`는 단계 3에서 실패하지만(`$eax`=3) 출력은 `accepted`입니다. 이것은 **프로세스의 레지스터를 바꾼 결과**이며 입력 `wrongkey`가 유효해진 것이 아닙니다. 디버거 없이 다시 실행하면 여전히 거부됩니다. 보고서에는 두 결과를 다른 절에 나눠 적습니다.

| 구분 | 바뀌는 것 | 지속성 | 이 Chapter 용도 |
|---|---|---|---|
| 수락 조건 복원 | 아무것도 바꾸지 않음. 입력을 계산 | 원본으로 언제든 재현 | 목표 |
| 실행 중 값 변경 | 한 프로세스의 레지스터·메모리 | 그 실행에서만 | 분기의 역할 확인용 실험 |
| 파일 패치 | 실행 파일의 바이트 | 파일에 남음 | Chapter 11, 자기 프로그램 복사본만 |

## 8. 소스 대조와 수정 과제

이제 소스를 열고 대조합니다. 디버그 빌드와 같은 함수를 링크해 단계별 반환값을 직접 확인할 수도 있습니다.

```bash
cd examples/reverse_engineering
gcc -std=c17 -Wall -Wextra -Dmain=lesson_main -c 07_validate.c -o build/07_functions.o
cat > build/07_harness.c <<'EOF'
#include <stdio.h>
int check_key(const char *input);
int main(int argc, char **argv) {
    for (int i = 1; i < argc; ++i) printf("%-12s stage=%d\n", argv[i], check_key(argv[i]));
    return 0;
}
EOF
gcc build/07_harness.c build/07_functions.o -o build/07_harness
./build/07_harness abcdefg Abcdefgh abcdefgh
```

`-Dmain=lesson_main`은 원본의 `main` 이름을 바꿔 하네스의 `main`과 충돌하지 않게 합니다.

수정 과제(복사본에서):

1. 허용 문자에 대문자를 추가합니다. 문자 범위 함수의 비교 개수와 생성기의 해 개수가 어떻게 바뀌는지 예측하고 확인합니다.
2. 가중 합을 `total = total * 31 + key[i]`로 바꿉니다. 마지막 글자를 계산으로 정하는 생성기 방식이 여전히 가능한지 설명하고 생성기를 고칩니다. (힌트: 마지막 글자는 곱해지지 않고 더해집니다.)
3. `KEY_BAD_SUM` 검사를 `KEY_BAD_PREFIX` 앞으로 옮기면 거부 입력 표의 어느 행이 달라지는지 예측합니다.

제출물:

- 반환값별 도달 조건 표와 수락 조건 의사 코드
- 입력 생성기와 실행 결과(원본으로 확인한 수락 입력 10개 이상, 전체 해 개수)
- 거부 입력 표(예측과 관찰)
- 실행 중 값 변경 실험과, 그것이 수락 조건과 다른 이유

자가 점검:

- 각 단계의 상수가 어떤 명령에서 나왔는지 주소로 말할 수 있는가?
- 변환 결과가 8비트로 잘린다는 근거(`cmp al,dl`)를 찾았는가?
- 길이를 글자 수가 아닌 바이트 수로 검사한다는 것을 입력으로 보였는가?
- 실행 중 값 변경과 수락 조건 복원을 섞어 쓰지 않았는가?

**완료 기준:** 다른 사람이 생성기를 실행해 원본 실행 파일이 수락하는 입력을 얻고, 거부 입력 표의 단계를 GDB로 재현할 수 있으면 통과입니다.

**확인 답:** 표는 `36 3e 3e 76`, 앞 4글자는 `lab7`, 가중 합 목표는 `0xe2e`(3630)입니다. 기준 소스의 수락 입력은 `lab7open`을 포함해 1,689개입니다.
