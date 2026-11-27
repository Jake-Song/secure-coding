# C 언어 입문 튜토리얼

처음 C를 배우는 사람을 위한 실습입니다. **직접 컴파일하고, 출력값을 예상하고, 코드를 바꾸는 것**을 목표로 합니다. 변수부터 시작해 배열·함수·포인터·구조체·동적 메모리·입력 검증을 익히고, 마지막에는 성적을 CSV 파일로 저장합니다.

Linux, macOS 또는 Windows의 WSL 터미널을 기준으로 합니다. C17을 지원하는 C 컴파일러와 `make`가 필요하며 Python이나 웹 앱은 필요하지 않습니다. 설치되어 있는지 먼저 확인합니다.

```bash
cc --version
make --version
```

도구가 없다면 Ubuntu/WSL에서는 `sudo apt install build-essential`, macOS에서는 `xcode-select --install`로 준비할 수 있습니다.

## 학습 순서

한 단계마다 설명→소스 읽기→실행→수정 과제 순서로 진행합니다. 하루 한 단계씩 진행해도 좋습니다.

| 단계 | 배울 내용 | 실행할 소스 |
|---|---|---|
| 1 | 프로그램 구조와 컴파일 | [01_hello.c](../examples/c_tutorial/01_hello.c) |
| 2 | 변수·연산·조건·반복 | [02_basics.c](../examples/c_tutorial/02_basics.c) |
| 3 | 함수·배열·길이 | [03_functions_arrays.c](../examples/c_tutorial/03_functions_arrays.c) |
| 4 | 주소·포인터·문자열 | [04_pointers_strings.c](../examples/c_tutorial/04_pointers_strings.c) |
| 5 | 구조체 | [05_structs.c](../examples/c_tutorial/05_structs.c) |
| 6 | 동적 메모리와 수명 | [06_heap.c](../examples/c_tutorial/06_heap.c) |
| 7 | 표준 입력과 정수 검증 | [07_input.c](../examples/c_tutorial/07_input.c) |
| 8 | 명령행 인자와 파일 저장 | [08_score_report.c](../examples/c_tutorial/08_score_report.c) |

## 1. 첫 프로그램: 소스에서 실행 파일까지

아래 명령은 **저장소 루트**에서 실행합니다. 이후 명령도 같은 위치를 기준으로 합니다.

```bash
mkdir -p examples/c_tutorial/build
cc -std=c17 -Wall -Wextra -Wpedantic -g \
  examples/c_tutorial/01_hello.c \
  -o examples/c_tutorial/build/01_hello
./examples/c_tutorial/build/01_hello
```

출력:

```text
Hello, C!
```

소스 전체는 다음과 같습니다.

```c
#include <stdio.h>

int main(void) {
    puts("Hello, C!");
    return 0;
}
```

- `#include <stdio.h>`: 표준 입출력 함수의 선언을 가져옵니다.
- `int main(void)`: 프로그램 시작 함수입니다. 이 형태에서는 인자를 받지 않습니다.
- `{ ... }`: 함수나 제어문의 실행 범위를 묶습니다.
- `puts(...)`: 문자열을 출력하고 줄바꿈합니다. 문자열은 큰따옴표로 감쌉니다.
- `;`: 선언이나 표현식 문장을 끝냅니다.
- `return 0`: 운영체제에 정상 종료를 알립니다.

`.c`는 소스 파일이고 `-o` 뒤의 경로는 생성할 실행 파일입니다. 코드를 고쳤으면 다시 컴파일해야 출력이 바뀝니다. `-std=c17`은 언어 규칙, `-Wall -Wextra -Wpedantic`은 경고, `-g`는 디버깅 정보를 지정합니다.

컴파일러는 소스를 처리해 기계어를 만들고, 링커는 필요한 코드들을 연결해 실행 파일을 만듭니다. **컴파일 오류**는 실행 파일을 만들지 못한 상태이고, **실행 중 오류**는 만들어진 프로그램을 실행하면서 생긴 문제입니다.

이제 예제 전체를 빌드합니다.

```bash
make -C examples/c_tutorial
```

결과는 `examples/c_tutorial/build/`에 생성됩니다. 이후 소스를 수정한 뒤 같은 명령을 실행하면 변경된 예제를 다시 빌드합니다. Makefile은 추가로 `-Wconversion -Wshadow -O0`을 사용해 변환·이름 가림을 경고하고 최적화를 끕니다.

**수정 과제:** 인사말을 바꾸고 `puts`를 하나 더 추가합니다. 세미콜론을 지웠을 때 컴파일러가 가리키는 위치도 읽어 봅니다.

## 2. 변수·연산·조건문·반복문

변수는 자료형과 이름을 붙인 저장 공간입니다. 초기값을 함께 지정하는 습관을 들입니다.

```c
int score = 85;
double ratio = 0.85;
char grade = 'B';
```

| 자료형 | 용도 | `printf` 출력 형식 |
|---|---|---|
| `int` | 범위 내 정수 | `%d` |
| `long` | 정수, `strtol`의 반환형 | `%ld` |
| `double` | 실수의 근삿값 | `%f`, 소수 둘째 자리까지는 `%.2f` |
| `char` | 문자 코드 한 단위 | `%c` |
| `bool` | 참·거짓, `<stdbool.h>` 필요 | `%d`로 1·0 출력 |
| `size_t` | 객체 크기·배열 인덱스 | `%zu` |

자료형 크기는 환경에 따라 달라질 수 있습니다. C에서 `sizeof(char)`는 1이며, 다른 자료형의 바이트 크기도 `sizeof`로 확인합니다. `char` 하나에 UTF-8 한글 한 글자가 들어간다고 가정하지 않습니다. 출력 형식과 인자 자료형을 맞춰야 합니다.

주요 연산:

| 종류 | 연산자 | 예 |
|---|---|---|
| 산술 | `+ - * / %` | 정수 `5 / 2`는 2, `5 % 2`는 1 |
| 대입 | `= += -=` | `total += 3`은 `total = total + 3` |
| 비교 | `== != < <= > >=` | `score >= 60` |
| 논리 | `&&` · `||` · `!` | `score >= 0 && score <= 100` |

`=`는 대입이고 `==`는 비교입니다. `5.0 / 2.0`은 실수 연산으로 2.5입니다. 정수 나눗셈의 소수 부분은 0 방향으로 버립니다. 0으로 나누면 안 되며, 표현 범위를 벗어나는 signed 정수 연산도 피해야 합니다.

조건과 반복은 다음처럼 작성합니다.

```c
if (score >= 60) {
    puts("pass");
} else {
    puts("retry");
}

int total = 0;
for (int number = 1; number <= 5; ++number) {
    total += number;
}
```

`for`의 세 부분은 **초기화; 계속할 조건; 매 반복 후 갱신**입니다. `++number`는 1을 더합니다. 반복 횟수를 미리 모르면 `while (조건) { ... }`도 사용합니다. `switch`는 값에 맞는 `case`로 이동하며, `break`는 해당 `switch`나 가장 가까운 반복문을 끝냅니다.

```bash
./examples/c_tutorial/build/02_basics
```

출력:

```text
score=85 ratio=0.85 grade=B passed=1
integer division=2 real division=2.50
pass
sum 1..5=15
good
```

**수정 과제:** 점수를 59로 바꿔 합격 여부를 확인합니다. 이어서 합계를 1~10으로 바꾸고 55가 나오는지 확인합니다. 이 예제의 `ratio`와 `grade`는 별도로 초기화한 값이므로 점수만 바꿔도 자동 갱신되지는 않습니다.

## 3. 함수와 배열

함수는 입력을 받아 일을 수행하고 결과를 반환합니다. 배열은 같은 자료형의 값을 연속해서 저장합니다.

```c
static int sum_scores(const int scores[], size_t count) {
    int total = 0;
    for (size_t index = 0; index < count; ++index) {
        total += scores[index];
    }
    return total;
}
```

반환형은 `int`, 함수 이름은 `sum_scores`, 매개변수는 `scores`와 `count`입니다. 파일 수준 함수의 `static`은 다른 소스 파일에서 이 이름으로 연결해 사용할 수 없게 합니다. `const int scores[]`는 이 매개변수를 통해 배열 원소를 수정하지 않겠다는 뜻입니다.

```c
const int scores[] = {70, 80, 90};
size_t count = sizeof scores / sizeof scores[0];
int total = sum_scores(scores, count);
double average = (double)total / (double)count;
```

인덱스는 0부터 시작합니다. 위 배열에서 유효한 위치는 `scores[0]`부터 `scores[2]`까지입니다. `scores[3]`은 범위 밖이며 C가 자동으로 막아 주지 않습니다.

`sizeof scores / sizeof scores[0]`는 **실제 배열이 선언된 범위**에서 원소 수를 계산합니다. 함수 매개변수의 배열 표기는 포인터로 조정되므로 함수 안의 `sizeof scores`로 원래 원소 수를 구할 수 없습니다. 그래서 길이를 별도 인자로 전달합니다.

`(double)`은 명시적 형 변환입니다. 정수 나눗셈 전에 변환해야 소수 부분을 얻습니다. 평균을 계산하기 전에는 개수가 0이 아닌지도 확인해야 합니다. 예제는 고정된 세 점수라 이 조건을 만족합니다. 합산 함수도 작은 점수용이며 임의의 큰 정수 목록을 처리하는 범용 구현은 아닙니다.

```bash
./examples/c_tutorial/build/03_functions_arrays
```

출력: `count=3 total=240 average=80.00`

**수정 과제:** 점수 100을 추가해 개수 4, 합계 340, 평균 85.00을 확인합니다. 이후 `max_score` 함수를 만들어 최댓값을 반환하되, 빈 배열을 어떻게 처리할지 먼저 정합니다.

## 4. 포인터와 문자열

포인터는 객체의 주소를 저장합니다.

```c
int score = 80;
int *pointer = &score;
*pointer = 81;
```

| 표현 | 의미 |
|---|---|
| `score` | 정숫값 81 |
| `&score` | `score`의 주소 |
| `pointer` | 저장한 주소 |
| `*pointer` | 그 주소에 있는 정수 객체 |
| `&pointer` | 포인터 변수 자신의 주소 |

선언의 `int *pointer`는 포인터 자료형을 나타내고, 표현식의 `*pointer`는 역참조입니다. C는 함수 인자를 값으로 전달합니다. 함수에 `&score`를 전달하면 주소의 복사본을 받지만, 그 주소를 역참조해 호출자의 `score`를 수정할 수 있습니다.

배열과 포인터는 관련이 있지만 서로 다른 개념입니다. 많은 표현식에서 배열은 첫 원소의 포인터로 변환됩니다. 포인터 자체에는 배열 길이 정보가 없습니다.

문자열은 끝에 **널 문자 `\0`**가 있는 문자 배열입니다.

```c
char name[] = "Alice";          /* A l i c e \0 : 6바이트 */
const char *message = "hello"; /* 문자열 리터럴을 가리킴 */
name[0] = 'M';
```

`name`의 원소는 수정할 수 있습니다. 문자열 리터럴을 수정하려 하면 정의되지 않은 동작이므로 `message`에는 `const char *`를 사용합니다. `sizeof name`은 널 문자를 포함한 배열 크기 6, `strlen(name)`은 널 문자 전 바이트 수 5입니다. `strlen`은 유효하게 널 종료된 문자열에만 사용합니다. UTF-8 문자열에서는 바이트 수와 글자 수가 다릅니다.

```bash
./examples/c_tutorial/build/04_pointers_strings
```

출력 예:

```text
score=81 pointed value=81
address=0x...환경마다 다른 주소...
name=Mlice bytes=6 length=5
hello
```

주소는 `%p`와 `(void *)pointer`로 출력합니다. `NULL`은 아무 객체도 가리키지 않는 포인터 값이며 역참조할 수 없습니다. 함수의 지역 변수를 가리키는 포인터를 반환해 함수 종료 후 사용하는 것도 잘못입니다.

**수정 과제:** 두 정수의 주소를 받아 값을 교환하는 `swap(int *left, int *right)`를 작성합니다. 임시 변수 하나를 사용하고, 호출 전후 값을 출력합니다.

## 5. 구조체: 관련된 값 묶기

```c
struct Student {
    char name[32];
    int score;
};

struct Student student = {.name = "Alice", .score = 85};
```

구조체는 서로 다른 자료형의 필드를 하나로 묶습니다. 객체의 필드는 `student.score`, 구조체 포인터의 필드는 `student_pointer->score`로 접근합니다. `pointer->score`는 `(*pointer).score`와 같습니다.

예제의 `has_passed(const struct Student *student)`는 구조체 주소를 받아 합격 여부를 반환합니다. `const`는 이 포인터를 통한 필드 수정을 막습니다. `condition ? yes : no`는 조건이 참이면 `yes`, 거짓이면 `no`를 선택하는 연산자입니다.

```bash
./examples/c_tutorial/build/05_structs
```

첫 줄은 `Alice: 85 (pass)`입니다. 다음 줄은 구조체 크기입니다. 컴파일러가 정렬을 위한 패딩을 넣을 수 있어, 구조체 크기는 필드 크기를 단순 합산한 값과 다를 수 있습니다. 구조체 메모리를 그대로 파일에 저장하면 환경에 따라 형식이 달라질 수 있습니다.

**수정 과제:** 학생 구조체 3개를 배열에 저장하고, 반복문으로 이름·점수·합격 여부를 출력합니다. `name[32]`에 넣을 문자열은 널 문자를 포함해 32바이트 이하여야 합니다.

## 6. 동적 메모리: `malloc`과 `free`

필요한 저장 공간을 실행 중 요청할 때 동적 할당을 사용합니다.

```c
int *values = malloc(count * sizeof *values);
if (values == NULL) {
    /* 할당 실패 처리 */
}
/* 원소에 값을 저장하고 사용 */
free(values);
values = NULL;
```

`<stdlib.h>`에 선언된 `malloc`은 요청한 바이트 수의 공간을 할당하며, 실패하면 `NULL`을 반환합니다. C에서는 반환값을 캐스팅할 필요가 없습니다. `sizeof *values`는 원소 자료형의 크기를 계산하므로 `int` 크기를 직접 적지 않아도 됩니다.

예제는 할당 전에 `count > SIZE_MAX / sizeof *values`를 검사합니다. `count * sizeof *values`가 `size_t`의 범위를 넘어 작은 값으로 돌아가면 필요한 양보다 적게 할당할 수 있기 때문입니다. `count == 0`도 이 예제에서는 거부합니다.

반드시 지킬 규칙:

1. 할당 성공을 확인한 뒤 사용합니다.
2. `malloc`의 공간은 초기화되어 있지 않으므로 읽기 전에 값을 저장합니다.
3. 유효한 인덱스 범위만 접근합니다.
4. 사용이 끝나면 할당한 블록을 한 번 해제합니다. 중간 오류 경로에서도 정리합니다.
5. 해제 후에는 해당 공간을 읽거나 쓰지 않습니다.

`values = NULL`은 그 변수의 재사용 실수를 줄입니다. 같은 공간을 가리키던 다른 포인터까지 바꾸지는 않습니다. 지역 변수는 해당 블록의 실행이 끝나면 수명이 끝나지만, 동적 할당 공간은 함수를 벗어나도 자동으로 해제되지 않습니다.

```bash
./examples/c_tutorial/build/06_heap
```

출력: `1 2 3 4 5`

**수정 과제:** `count`를 10으로 바꾸어 출력합니다. 이 예제의 `(int)index`는 작은 고정 개수에서 사용합니다. 임의의 큰 크기를 허용하도록 확장할 때는 형 변환 범위도 검토합니다.

## 7. 사용자 입력: 읽기와 해석을 나누기

이 예제는 터미널에서 **한 줄의 텍스트**를 읽어 점수로 해석합니다. `fgets`로 읽을 크기를 제한한 뒤 `strtol`로 정수를 변환합니다.

```bash
./examples/c_tutorial/build/07_input
```

`85`를 입력하고 Enter를 누르면 `accepted=85`가 출력됩니다. 파이프로도 시험할 수 있습니다.

```bash
printf '85\n' | ./examples/c_tutorial/build/07_input
printf '85abc\n' | ./examples/c_tutorial/build/07_input
printf '101\n' | ./examples/c_tutorial/build/07_input
```

첫 입력은 성공하고 나머지는 실패합니다. 바로 다음 명령으로 `echo $?`를 실행하면 성공은 0, 실패는 0이 아닌 종료 코드를 확인할 수 있습니다.

소스에서 다음 검사가 각각 무엇을 막는지 찾습니다.

| 검사 | 목적 |
|---|---|
| `fgets(...) == NULL` | EOF·읽기 실패 후 버퍼 사용 방지 |
| 줄바꿈 포함 여부 | 잘린 긴 입력을 정상 한 줄로 처리하지 않음 |
| 변환 전 `errno = 0` | 이전 오류와 이번 변환 오류 구분 |
| `end == buffer` | 숫자를 전혀 읽지 못한 경우 거부 |
| `errno == ERANGE` | `long`으로 표현할 수 없는 수 거부 |
| 공백을 넘긴 뒤 `*end == '\0'` | `85abc`, `85 90` 같은 나머지 입력 거부 |
| `0 <= score && score <= 100` | 프로그램에서 허용한 점수 범위 검사 |

`end`는 `strtol`이 변환을 멈춘 위치입니다. `isspace`는 공백 문자를 판별하며, 음수 `char` 값을 직접 넘기지 않도록 `(unsigned char)`로 변환합니다. 출력에는 `printf`, 오류 메시지에는 `fprintf(stderr, ...)`나 `fputs(..., stderr)`를 사용합니다.

이 예제는 Enter로 끝나는 입력만 받으며, 줄바꿈 전 최대 62바이트를 허용합니다. 줄바꿈 없는 EOF는 거부합니다. `strtol`의 규칙에 따라 앞뒤 공백과 `+85`는 허용하지만, 소수나 두 개의 숫자는 거부합니다. 한 줄만 처리하고 종료하므로 긴 입력을 비우고 재입력받는 루프는 포함하지 않습니다.

`atoi`는 변환 오류를 상세히 구별하기 어렵습니다. `scanf`를 사용할 때도 반환값, 문자열의 최대 폭, 남은 입력을 처리해야 합니다. 여기서는 먼저 한 줄을 확보하는 방법을 익힙니다.

**수정 과제:** `0`, `100`, `-1`, 빈 줄, `3.14`, 아주 긴 정수를 넣고 성공·실패 이유를 표로 적습니다. 이후 최대 세 번 재입력하도록 바꾸되, 긴 줄의 남은 입력을 처리할 방법도 정합니다.

## 8. 종합 실습: 성적 보고서 만들기

마지막 예제는 명령행으로 출력 파일 경로와 점수를 받아 개수·합계·평균을 CSV로 저장합니다.

```bash
report_dir=$(mktemp -d)
./examples/c_tutorial/build/08_score_report "$report_dir/scores.csv" 70 80 90
cat "$report_dir/scores.csv"
```

프로그램 출력은 `count=3 total=240 average=80.00`, 파일 내용은 다음과 같습니다.

```csv
count,total,average
3,240,80.00
```

소스는 다음 순서로 읽습니다.

1. `main(int argc, char *argv[])`: `argc`는 프로그램 이름을 포함한 인자 개수입니다. `argv[0]`은 호출 이름, `argv[1]`은 파일 경로, `argv[2]`부터는 점수 문자열입니다.
2. 점수 개수가 1~100개인지 검사합니다. 0개이면 나눗셈을 하지 않고 종료합니다.
3. `parse_score`는 각 문자열을 검증해 정수로 바꿉니다. `07_input`보다 엄격하게 **ASCII 숫자만** 허용하며 `+85`, 공백, 음수는 거부합니다. `001`은 1로 해석합니다.
4. 배열에 저장한 점수를 합산합니다. 점수당 최대 100, 최대 100개이므로 합계는 최대 10,000입니다.
5. 모든 점수가 유효할 때만 `fopen(path, "wx")`로 새 파일을 엽니다. 기존 파일이 있으면 실패합니다. `"w"`는 기존 파일 내용을 지우므로 차이를 알아둡니다.
6. `fprintf`로 텍스트를 쓰고 `fclose`로 닫습니다. 쓰기 결과와 닫기 결과를 모두 검사합니다. 버퍼에 있던 출력의 오류가 닫을 때 드러날 수도 있습니다.

명령행 인자는 항상 문자열입니다. `parse_score`는 성공 여부를 반환하고, 변환한 점수는 `int *result`를 통해 호출자에게 전달합니다. 4단계에서 배운 포인터의 쓰임을 확인합니다.

실패 동작도 확인합니다.

```bash
# 이미 만든 파일: 실패하며 원래 내용 유지
./examples/c_tutorial/build/08_score_report "$report_dir/scores.csv" 100

# 잘못된 점수: 실패하며 새 파일을 만들지 않음
./examples/c_tutorial/build/08_score_report "$report_dir/invalid.csv" 70 101

# 점수 없음: 사용법 출력 후 실패
./examples/c_tutorial/build/08_score_report "$report_dir/empty.csv"
```

파일 생성 후 디스크 쓰기가 실패하면 새 파일이 불완전하게 남을 수 있으며 프로그램은 오류로 종료합니다. 파일 내용을 다시 읽는 기능은 확장 과제로 남겨둡니다.

**확장 과제:** 최솟값·최댓값을 보고서에 추가합니다. 이어서 `fopen(path, "r")`, `fgets`, `fclose`를 사용해 보고서를 읽는 기능을 만듭니다. 파일이 없거나 한 줄이 너무 길 때도 처리합니다.

## 오류를 찾는 연습

C에서 정의되지 않은 동작은 항상 같은 오류 메시지나 충돌을 만들지 않습니다. 우연히 출력이 맞더라도 올바른 코드라고 판단할 수 없습니다.

| 흔한 실수 | 점검할 것 |
|---|---|
| 초기화하지 않은 변수 읽기 | 첫 사용 전에 값 저장 |
| 배열 경계 초과 | 항상 `index < count` 유지 |
| 문자열 끝의 `\0` 누락 | 데이터 길이 외에 종료 문자 공간 확보 |
| `printf` 형식 불일치 | `%d`, `%ld`, `%zu` 등 자료형에 맞추기 |
| 사용자 문자열을 출력 형식으로 사용 | `printf("%s", text)`처럼 고정 형식 사용 |
| 지역 변수 주소를 반환 | 객체 수명이 끝난 주소를 사용하지 않기 |
| 해제 후 접근·중복 해제 | 할당한 공간의 소유자와 해제 지점 정하기 |
| 큰 길이의 곱셈 오버플로 | 할당 전에 `SIZE_MAX / 원소크기`와 비교 |

GCC 또는 Clang에서 AddressSanitizer·UndefinedBehaviorSanitizer를 지원한다면 다음처럼 별도의 실행 파일을 만들 수 있습니다. 해당 런타임 설치가 필요할 수 있습니다.

```bash
cc -std=c17 -Wall -Wextra -Wpedantic -g \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  examples/c_tutorial/06_heap.c -o examples/c_tutorial/build/06_heap_checked
./examples/c_tutorial/build/06_heap_checked
```

Sanitizer는 실행한 경로의 일부 메모리 오류 등을 찾는 데 도움을 줍니다. 모든 오류나 모든 입력에 대한 안전성을 보장하지는 않습니다.

디버거나 추적 환경에서 `LeakSanitizer does not work under ptrace` 오류가 나면 추적 없이 실행하거나 아래처럼 누수 검사만 끄고 다시 실행합니다. 이 실행에서는 메모리 누수 여부를 확인할 수 없습니다.

```bash
ASAN_OPTIONS=detect_leaks=0 ./examples/c_tutorial/build/06_heap_checked
```

자동 검증은 Python 3와 C 컴파일러가 있을 때 저장소 루트에서 실행합니다.

```bash
python3 -m unittest tests.test_c_tutorial -v
```

이 테스트는 임시 디렉터리에서 예제를 컴파일하고, 정상 출력·입력 거부·점수 개수 경계·기존 파일 보존을 검사합니다. 컴파일러가 없으면 건너뜁니다.

2026-11-15, Linux의 GCC 13.3.0에서 예제 8개의 빌드와 자동 테스트 9개 통과를 확인했습니다. 동적 메모리 예제는 누수 검사를 끈 AddressSanitizer·UndefinedBehaviorSanitizer 실행에서도 오류가 없었습니다. 이 환경에서는 LeakSanitizer 실행이 제한되었습니다.

## 마친 뒤 확인할 것

- 소스를 수정하고 다시 컴파일해 실행할 수 있다.
- 배열의 유효 인덱스와 함수에 길이를 전달하는 이유를 설명할 수 있다.
- `p`, `*p`, `&p`와 객체의 수명을 구별할 수 있다.
- 문자열 길이와 저장 공간의 크기를 구별할 수 있다.
- 할당·입력 변환·파일 입출력의 실패를 처리할 수 있다.
- 종합 예제에 기능 하나를 추가하고 정상·오류 입력으로 검증할 수 있다.

다음에는 [C++ 튜토리얼](cpp-tutorial.md)의 참조·컨테이너·RAII나 [Rust 튜토리얼](rust-tutorial.md)의 소유권·빌림과 비교해 봅니다. [역엔지니어링 과정](reverse-engineering/curriculum.md)의 Chapter 1~2로 이어가 같은 C 코드가 어셈블리와 메모리에서 어떻게 보이는지 관찰할 수도 있습니다.
