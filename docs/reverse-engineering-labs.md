# 역엔지니어링 1~4주차 학습자료

[12주 커리큘럼](reverse-engineering.md)의 첫 네 주를 실제로 따라 할 수 있도록 풀어 쓴 자료입니다. **주 6~8시간, Linux x86-64, C17, GCC·GNU Binutils·GDB**를 기준으로 합니다. 각 주차는 개념 → 예측 → 실행 → 근거 기록 → 수정 과제 순서입니다.

| 주차 | 학습자료 | 핵심 질문 | 제출물 |
|---|---|---|---|
| 1 | [C와 빌드 흐름](reverse-engineering/week-01.md) | 소스가 어떤 단계를 거쳐 실행 파일이 되는가? | 빌드 단계 그림, 입력·출력·종료 코드 표 |
| 2 | [포인터와 프로세스 메모리](reverse-engineering/week-02.md) | 값·주소·바이트·객체 수명은 어떻게 다른가? | 메모리 그림, GDB 관찰표, 구조체 배치 |
| 3 | [x86-64 명령어와 제어 흐름](reverse-engineering/week-03.md) | 명령어가 값과 다음 실행 위치를 어떻게 바꾸는가? | C/어셈블리 대응표, 명령 추적표, 루프 그림 |
| 4 | [함수 호출과 ELF](reverse-engineering/week-04.md) | 함수 인자와 파일의 바이트는 실행 중 어디에 있는가? | 호출 상태표, ELF 지도, 주소 변환 계산 |

## 시작하기

조건문·반복문·함수 작성이 낯설면 먼저 [C 입문 튜토리얼](c-tutorial.md)을 진행합니다. 이번 자료는 소스를 함께 보면서 분석하는 기반 과정이며, 소스 없는 독립 분석은 이후 주차에서 진행합니다. 실습에는 저장소에서 직접 빌드한 프로그램을 사용합니다.

명령은 별도 표시가 없으면 **저장소 루트**에서 실행합니다. WSL2도 Linux 터미널 안에서 진행합니다. ARM 머신은 x86-64 Linux 가상 머신을 사용합니다.

```bash
uname -m
gcc --version
gdb --version
readelf --version
make -C examples/reverse_engineering
```

`uname -m`은 `x86_64`여야 합니다. 도구가 없다면 Ubuntu/Debian 실습 머신에서 설치합니다.

```bash
sudo apt update
sudo apt install build-essential binutils file gdb python3
```

빌드 결과는 `examples/reverse_engineering/build/`에 생성합니다. 웹 앱 실행이나 Python 가상환경은 필요 없습니다. 기본 빌드는 `-O0 -g -fno-omit-frame-pointer -fPIE -pie`를 사용합니다. 최적화를 줄이고 디버그 정보를 남기면서 PIE 주소 변화를 관찰하기 위한 설정입니다. 4주차에만 별도의 non-PIE 비교본을 함께 만듭니다.

| 실행 파일 | 용도 |
|---|---|
| `01_build` | C, 문자열 판정, 빌드 산출물 비교 |
| `02_memory` | 포인터, 구조체, 동적 할당, 바이트 관찰 |
| `03_flow` | 산술, signed/unsigned 비교, 반복문, 비트 연산 |
| `03_registers` | 짧은 수제 어셈블리로 부분 레지스터와 `lea` 관찰 |
| `04_elf`, `04_elf_nopie` | 일곱 인자 함수 호출, ELF 구조와 주소 비교 |

소스는 [예제 디렉터리](../examples/reverse_engineering/)에 있습니다. `registers.S`는 명령 순서를 고정한 관찰용 예제입니다. C를 컴파일한 결과가 반드시 이 순서여야 한다는 뜻은 아닙니다.

## 주간 진행 방식

| 시간 | 할 일 |
|---|---|
| 1~2시간 | 개념 읽기, 실행 전 결과 예측 |
| 3~4시간 | 기본 실습, 입력·중단점·바이트 관찰, 수정 과제 |
| 2시간 | 보고서 작성, 다른 터미널에서 절차 재실행, 자가 점검 |

예상 주소·스택 오프셋·명령어 배열은 환경에 따라 달라집니다. 문서의 고정 숫자를 찾기보다 **자신의 실행에서 주소를 구하고 값의 관계를 확인**합니다. 수정 과제는 예제 소스를 임시 작업 폴더에 복사해 진행해도 됩니다.

매주 아래 양식으로 보고서를 남깁니다. 개인 학습 기록을 저장소에 남기려면 Git에서 제외된 `notes/private/`를 사용할 수 있습니다.

```text
주차 / 날짜:
환경: OS, uname -m, GCC·Binutils·GDB 버전
대상: 소스 경로, 빌드 명령, 실행 파일 SHA-256
분석 질문:
실행 전 예측:
재현 절차: 터미널 명령과 GDB 명령을 구분
관찰: 입력, 출력, 종료 코드, 주소, 바이트, 레지스터
해석: 관찰이 가설을 지지하거나 반박한 이유
미확인: 아직 확인하지 못한 조건과 다음 확인 방법
수정 과제: 변경 내용과 정상·오류·경계 입력 결과
```

```bash
sha256sum examples/reverse_engineering/build/01_build
python3 -m unittest tests.test_reverse_engineering -v
```

자동 테스트는 빌드·프로그램 동작·ELF 속성을 확인합니다. GDB로 중단하고 값을 관찰하는 학습은 각 주차 절차로 별도 수행합니다. 실제 검증 범위는 [검증 기록](validation.md)에 적습니다.

## 막혔을 때

| 증상 | 확인과 해결 |
|---|---|
| `Exec format error` | `uname -m`과 `file 실행파일`을 비교하고 x86-64 Linux에서 재빌드 |
| `No debugging symbols found` | 제공 Makefile로 다시 빌드하고 `build/`의 디버그 실행 파일 열기 |
| GDB에서 지역 변수가 안 보임 | 초기화가 끝난 위치인지, 해당 함수 프레임인지 확인. `bt`, `frame`, `info locals` 사용 |
| `ptrace: Operation not permitted` | 컨테이너·샌드박스의 디버깅 제한. ptrace가 허용된 개인 실습 VM에서 동적 관찰 진행 |
| 주소가 문서와 다름 | 자신의 `disassemble`, `p/x &변수`, `info proc mappings` 결과로 기록 |
| 소스를 바꿨는데 결과가 같음 | `make -C examples/reverse_engineering` 후 실행 파일 경로와 수정 시간을 확인 |

GDB에 입력할 명령은 `gdb` 코드 블록으로 표시합니다. `$rax` 같은 표기는 GDB 안에서 해석해야 하므로 셸에 붙여 넣지 않습니다. 셸의 `echo $?`는 대상 실행 직후에 사용해야 해당 종료 코드를 얻습니다.

4주차를 마치면 [커리큘럼의 5주차 Ghidra](reverse-engineering.md#5주차-ghidra)로 이어갑니다.
