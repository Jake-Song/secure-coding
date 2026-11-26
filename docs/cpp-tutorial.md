# C++ 입문 튜토리얼

변수부터 클래스·표준 라이브러리·자원 관리까지 배우는 **C++17 실습**입니다. [C 튜토리얼](c-tutorial.md)을 먼저 배웠다면 문자열과 배열, 메모리 관리 방법을 비교하며 진행하세요. C를 반드시 먼저 배워야 하는 것은 아닙니다.

각 단계는 설명→소스 읽기→출력 예상→실행→수정 과제 순서입니다. Linux, macOS 또는 Windows의 WSL에서 C++17 컴파일러와 `make`를 사용합니다. 외부 C++ 패키지는 필요하지 않습니다.

## 준비와 전체 실행

저장소 루트에서 실행합니다.

```bash
c++ --version
make --version
make -C examples/cpp_tutorial
./examples/cpp_tutorial/build/01_hello
```

도구가 없다면 Ubuntu/WSL에서는 `sudo apt install build-essential`, macOS에서는 `xcode-select --install`로 준비할 수 있습니다. 빌드 결과는 `examples/cpp_tutorial/build/`에 생성됩니다. 소스를 수정했으면 `make`를 다시 실행합니다.

| 단계 | 주제 | 소스 |
|---|---|---|
| 1 | 프로그램 구조와 출력 | [01_hello.cpp](../examples/cpp_tutorial/01_hello.cpp) |
| 2 | 자료형·조건·반복·참조 | [02_basics.cpp](../examples/cpp_tutorial/02_basics.cpp) |
| 3 | 문자열·vector·함수 | [03_strings_vectors.cpp](../examples/cpp_tutorial/03_strings_vectors.cpp) |
| 4 | 클래스와 생성자 | [04_classes.cpp](../examples/cpp_tutorial/04_classes.cpp) |
| 5 | 알고리즘·람다·템플릿 | [05_algorithms.cpp](../examples/cpp_tutorial/05_algorithms.cpp) |
| 6 | RAII·소유권·이동 | [06_raii.cpp](../examples/cpp_tutorial/06_raii.cpp) |
| 7 | 입력·optional·변환 | [07_input.cpp](../examples/cpp_tutorial/07_input.cpp) |
| 8 | 명령행 인자·파일 저장 | [08_score_report.cpp](../examples/cpp_tutorial/08_score_report.cpp) |

## 1. 첫 프로그램과 컴파일

```cpp
#include <iostream>

int main() {
    std::cout << "Hello, C++!\n";
    return 0;
}
```

`main`은 시작 함수, `std::cout`은 표준 출력 스트림입니다. `<<`로 값을 스트림에 보내고 `\n`으로 줄을 바꿉니다. `std::`는 표준 라이브러리 이름이 속한 네임스페이스를 지정합니다. `return 0`은 정상 종료입니다. `main`의 끝에 도달해도 0을 반환합니다.

예제 하나를 직접 컴파일할 수도 있습니다.

```bash
c++ -std=c++17 -Wall -Wextra -Wpedantic -g \
  examples/cpp_tutorial/01_hello.cpp \
  -o examples/cpp_tutorial/build/01_hello
./examples/cpp_tutorial/build/01_hello
```

출력은 `Hello, C++!`입니다. `c++` 드라이버로 빌드하면 C++ 표준 라이브러리 연결도 처리합니다. `.cpp`가 소스, `-o` 뒤가 실행 파일입니다. `-std=c++17`은 언어 규칙, `-Wall -Wextra -Wpedantic`은 경고, `-g`는 디버깅 정보를 지정합니다.

**수정 과제:** 정수 42와 문자열을 한 문장으로 출력합니다. 소스를 고친 후 다시 컴파일하지 않으면 어떤 프로그램이 실행되는지도 확인합니다.

## 2. 변수·조건·반복·참조

```cpp
int score{85};
const int pass_mark{60};
const auto passed = score >= pass_mark;
```

`int`는 정수, `double`은 실수의 근삿값, `char`는 문자 코드 한 단위, `bool`은 참·거짓입니다. `const` 객체는 초기화 후 그 이름을 통해 값을 바꿀 수 없습니다. `auto`는 초기값으로부터 **컴파일 시점에** 자료형을 추론합니다. 위의 `passed`는 `bool`입니다.

중괄호 초기화는 `int value{3.5};` 같은 좁히기 변환을 거부합니다. 값을 넣기 전에 지역 변수를 읽지 않도록 초기값을 지정합니다. `=`는 대입, `==`는 비교입니다. 조건은 `if`와 `else`, 반복은 `for`나 `while`로 작성합니다.

```cpp
int total{0};
for (int number = 1; number <= 5; ++number) {
    total += number;
}
```

`for`의 세 부분은 초기화·계속할 조건·반복 후 갱신입니다. `++number`는 1 증가, `total += number`는 누적 덧셈입니다. `&&`, `||`, `!`는 논리 연산입니다. 정수 `5 / 2`는 2이고 `5.0 / 2.0`은 2.5입니다. 0으로 나누거나 signed 정수의 표현 범위를 벗어나는 연산을 하지 않습니다.

함수는 입력을 받아 동작을 수행합니다. 반환할 값이 없으면 반환형으로 `void`를 사용합니다.

```cpp
void add_one(int& value) {
    ++value;
}
```

`int&`는 기존 정수에 대한 **참조**입니다. `add_one(score)`는 원본을 수정합니다. `int value`로 받으면 정숫값의 복사본을 수정합니다. 참조는 선언 시 대상을 지정하며 다른 객체로 다시 연결할 수 없습니다. 참조도 대상의 수명이 끝나면 사용할 수 없습니다.

```bash
./examples/cpp_tutorial/build/02_basics
```

```text
passed=true
sum 1..5=15
score=86 pass
```

`std::boolalpha`가 `bool`을 `true`·`false`로 출력하도록 설정합니다.

**수정 과제:** 시작 점수를 59로 바꾸고 함수 호출 전후의 합격 여부를 비교합니다. 두 정수를 참조로 받아 교환하는 함수도 만듭니다.

## 3. `std::string`과 `std::vector`

```cpp
std::string name{"Alice"};
name += " Lee";
std::vector<int> scores{70, 80, 90};
scores.push_back(100);
```

`std::string`은 문자열의 저장 공간을 관리하고, `std::vector<int>`는 정수 원소를 가진 크기 조절 가능한 컨테이너입니다. `push_back`은 끝에 원소를 추가합니다. `size()`는 문자열의 `char` 원소 수나 벡터의 원소 수를 반환합니다. UTF-8 문자열에서는 `size()`가 글자 수와 다를 수 있습니다.

```cpp
double average(const std::vector<int>& scores);
```

이 선언은 정수 벡터를 읽어 평균을 반환하는 함수입니다. `const ...&`로 받으면 벡터 전체를 복사하지 않고 읽습니다. 반환형·함수 이름·매개변수의 순서로 읽습니다.

범위 기반 반복문 `for (const int score : scores)`는 각 원소를 순서대로 방문합니다. `static_cast<double>(total)`은 합계를 실수로 변환합니다. 나눗셈 전에 실수로 변환해야 소수 부분을 얻습니다.

예제의 평균 함수는 빈 벡터에 대해 `std::invalid_argument` 예외를 던집니다. 값이 없는 입력을 처리하는 방법을 먼저 정하는 습관을 들입니다. 이 함수는 작은 점수 목록용이며 임의의 큰 정수 합계에 대한 오버플로 검사는 생략했습니다.

```bash
./examples/cpp_tutorial/build/03_strings_vectors
```

```text
name=Alice Lee bytes=9
count=4 average=85.00
first=70
```

`scores.at(0)`은 범위를 검사하며 잘못된 위치면 예외를 던집니다. `scores[0]`은 범위 검사를 보장하지 않습니다. 벡터를 확장해 재할당이 일어나면 기존 원소의 주소·참조·이터레이터는 무효가 될 수 있습니다.

**수정 과제:** 점수를 하나 더 추가하고 평균을 예상합니다. 빈 벡터로 호출한 예외를 다음 단계의 `try`·`catch`로 처리해 봅니다.

## 4. 클래스·생성자·예외

클래스는 데이터와 그 데이터를 다루는 함수를 묶습니다.

```cpp
class Student {
public:
    Student(std::string name, int score);
    int score() const;
private:
    std::string name_;
    int score_;
};
```

`public`은 외부에 공개하는 인터페이스, `private`은 외부에서 직접 접근하지 못하게 하는 부분입니다. 클래스 이름과 같은 **생성자**는 객체를 만들 때 호출합니다. 예제의 `: name_{std::move(name)}, score_{score}`는 멤버 초기화 목록입니다.

생성자는 점수가 0~100인지 검사해 항상 유효한 상태의 객체를 만들도록 합니다. `score() const`의 끝에 있는 `const`는 이 멤버 함수가 객체를 읽는 용도임을 나타냅니다. `const std::string& name() const`는 이름을 복사하지 않고 읽게 하지만, 반환된 참조는 학생 객체보다 오래 사용할 수 없습니다.

```cpp
try {
    const Student invalid{"Bob", 101};
} catch (const std::invalid_argument& error) {
    std::cout << error.what() << '\n';
}
```

`throw`는 예외를 발생시키고, 대응하는 `catch`가 처리합니다. 예외는 `const` 참조로 받아 복사를 피합니다. 예상 가능한 실패를 모두 예외로 표현해야 하는 것은 아닙니다. 7단계에서는 값이 없음을 반환하는 방법도 배웁니다.

```bash
./examples/cpp_tutorial/build/04_classes
```

```text
Alice: 85 (pass)
rejected: score must be from 0 to 100
```

**수정 과제:** 점수 변경 메서드를 추가하되 같은 범위 검사를 적용합니다. 잘못된 변경 후에도 이전 점수가 유지되는지 확인합니다.

## 5. 알고리즘·람다·템플릿

```cpp
std::sort(scores.begin(), scores.end());
const auto passed = std::count_if(scores.begin(), scores.end(), [](int score) {
    return score >= 60;
});
```

`begin()`과 `end()`는 컨테이너의 범위를 표현하는 이터레이터입니다. 범위는 `[begin, end)`이고 `end` 자체는 원소가 아니므로 역참조하지 않습니다. `sort`는 정렬하고 `count_if`는 조건에 맞는 원소를 셉니다.

`[](int score) { ... }`는 이름 없는 함수인 **람다**입니다. `[]`는 주변 변수의 캡처 목록이며, 이 예제는 외부 변수를 캡처하지 않습니다. 기준값을 변수로 둔다면 `[pass_mark](int score) { return score >= pass_mark; }`처럼 값으로 캡처할 수 있습니다.

예제의 `template <typename Container>`는 여러 컨테이너 자료형에서 사용할 수 있는 함수 템플릿입니다. 실제 자료형을 넣어 컴파일할 때 그 자료형이 지원하지 않는 연산은 오류가 됩니다.

```bash
./examples/cpp_tutorial/build/05_algorithms
```

```text
50 60 80 90
passed=3
```

**수정 과제:** 비교 람다를 `sort`의 세 번째 인자로 전달해 내림차순으로 정렬합니다. `count_if`의 합격 기준을 80으로 바꿉니다.

## 6. RAII와 소유권 이동

RAII는 자원의 수명을 객체의 수명에 연결하는 방식입니다. 객체가 범위를 벗어나면 소멸자가 실행되어 자원을 정리합니다. `std::string`과 `std::vector`도 내부 저장 공간을 이 방식으로 관리합니다. 예외로 범위를 빠져나갈 때도 해당 지역 객체들의 정리가 이루어집니다.

```cpp
auto owner = std::make_unique<std::string>("owned resource");
auto next_owner = std::move(owner);
```

`std::unique_ptr<T>`는 동적으로 만든 객체를 단독 소유합니다. `*owner`로 객체에 접근하고, 소유 포인터가 파괴될 때 객체도 삭제됩니다. 보통 소유 객체를 만들 때는 직접 `new`·`delete`를 작성하기보다 `make_unique`를 사용합니다. 일반 문자열·벡터 값만으로 해결된다면 스마트 포인터도 필요하지 않습니다.

`std::move` 자체가 데이터를 옮기지는 않습니다. 이동 가능한 표현식으로 바꾸며, 위 코드에서는 `unique_ptr`의 이동 생성자가 소유권을 전달합니다. 이동 후 `owner`는 빈 포인터가 되므로 역참조하면 안 됩니다. 일반 `std::string`의 이동 후 상태까지 항상 빈 문자열이라고 가정하지 않습니다.

```bash
./examples/cpp_tutorial/build/06_raii
```

```text
owned resource
old owner empty=true
new owner=owned resource
```

C++의 원시 포인터 `T*`와 참조 `T&`는 그 자체로 자원 해제를 수행하지 않습니다. 객체가 유효한 동안만 빌려 쓰는 용도로 사용하고, 누가 소유하고 언제 파괴하는지 정합니다. C++ 컴파일러가 Rust처럼 모든 빌림 관계를 검사해 주지는 않습니다.

**수정 과제:** `unique_ptr`를 복사하려 하면 컴파일이 실패하는지 확인합니다. 원본 예제를 되돌린 뒤 소유권을 함수에 이동시켜 함수 종료 때 정리되도록 바꿉니다.

## 7. 입력 검증과 `std::optional`

```bash
printf '85\n' | ./examples/cpp_tutorial/build/07_input
printf '85abc\n' | ./examples/cpp_tutorial/build/07_input
printf '101\n' | ./examples/cpp_tutorial/build/07_input
```

첫 입력만 `accepted=85`로 성공합니다. 소스는 `std::getline`으로 한 줄을 읽고, 공용 헤더 [score.hpp](../examples/cpp_tutorial/score.hpp)의 `parse_score`로 변환합니다. `#include "score.hpp"`는 이 프로젝트의 헤더를 가져옵니다. 헤더 가드가 중복 포함을 막고, 헤더의 `inline` 함수는 여러 소스에서 정의를 공유할 수 있게 합니다.

```cpp
std::optional<int> parse_score(std::string_view text);
```

`std::optional<int>`는 정수가 있거나 값이 없는 상태입니다. 실패는 `std::nullopt`로 반환합니다. `if (score)`로 값의 존재를 확인한 다음 `*score`로 읽습니다. **점수 0도 값이 있는 성공 상태**이므로 `if (*score)`로 성공을 판별하지 않습니다.

`std::string_view`는 문자열을 소유하지 않는 읽기 전용 뷰입니다. 원본 문자열이 유효한 동안만 사용할 수 있습니다. `std::from_chars`는 정수 변환의 오류 코드와 변환이 끝난 위치를 반환합니다. 두 결과를 모두 확인해 큰 수와 `85abc` 같은 입력을 거부합니다.

입력 규칙은 다음과 같습니다.

- ASCII 숫자로 쓴 0~100만 허용하며 `001`은 1로 해석합니다.
- 공백, 부호, 소수, 빈 줄, 숫자 뒤 문자, 널 문자를 거부합니다.
- 줄바꿈을 제외한 길이는 최대 62바이트입니다. 짧은 숫자 뒤의 줄바꿈 없는 EOF도 허용합니다.
- `getline`은 읽는 동안 문자열을 늘립니다. 길이 검사는 **읽은 뒤의 검증**이며 메모리 할당 상한이 아닙니다. 신뢰할 수 없는 대용량 스트림에는 별도의 제한된 읽기를 구현해야 합니다.

**수정 과제:** `0`, `100`, `-1`, `+85`, `85 90`, 큰 정수를 넣고 결과를 기록합니다. 실패 이유도 필요하다면 `optional` 대신 오류 종류를 담은 반환형을 설계합니다.

## 8. 종합 실습: 성적 CSV 저장

```bash
report_dir=$(mktemp -d)
./examples/cpp_tutorial/build/08_score_report "$report_dir/scores.csv" 70 80 90
cat "$report_dir/scores.csv"
```

프로그램은 `report saved`를 출력하고 다음 파일을 만듭니다.

```csv
count,total,average
3,240,80.00
```

`argc`는 프로그램 이름을 포함한 인자 개수, `argv[1]`은 파일 경로, `argv[2]`부터는 점수 문자열입니다. 점수를 1~100개로 제한하고 각 점수를 검증한 뒤 벡터에 저장합니다. `std::accumulate`는 초기값 0부터 합산하며 합계는 최대 10,000입니다. 입력 검증이 끝나기 전에는 파일을 생성하지 않습니다.

이 예제는 기존 파일을 보존하기 위해 C 라이브러리의 `fopen(path, "wx")`를 사용합니다. C++17의 기본 `ofstream` 열기에는 독점 생성 옵션이 없어, `FILE*`를 `unique_ptr`로 감싸 자원을 관리하는 방식을 배웁니다. 일반 `std::ofstream(path)`는 기존 내용을 지울 수 있습니다.

`FileCloser`는 `operator()`로 호출할 수 있는 객체이며, 소유 포인터가 파괴될 때 `fclose`를 수행합니다. `report.get()`은 소유권을 유지한 채 포인터를 빌립니다. 마지막의 `report.release()`는 소유권을 넘기므로 즉시 `fclose`해 닫기 결과를 확인합니다. 이 부분을 지우거나 중복해서 닫지 않습니다.

같은 파일 경로로 다시 실행하면 실패하며 기존 내용이 유지됩니다. `101` 같은 잘못된 점수는 실패하고 새 파일도 만들지 않습니다. 생성 후 쓰기나 닫기가 실패하면 불완전한 새 파일이 남을 수 있습니다.

**확장 과제:** 최솟값·최댓값을 추가합니다. 별도 기능으로 `std::ifstream`과 `getline`을 사용해 CSV를 다시 읽되, 잘못된 숫자와 누락된 행을 처리합니다.

## 검증과 다음 단계

Python 3가 있으면 정상 출력, 입력 경계, 파일 보존을 자동 검사할 수 있습니다. 컴파일러가 없으면 해당 언어 테스트를 건너뜁니다.

```bash
python3 -m unittest tests.test_cpp_rust_tutorials.CppTutorialTests -v
```

모든 C++ 예제는 경고를 오류로 처리해 빌드합니다. 포인터·참조의 수명 오류는 경고만으로 모두 검출되지 않습니다. GCC/Clang에서 지원한다면 C 튜토리얼의 Sanitizer 실행 방법에 `c++ -std=c++17`과 C++ 파일을 적용해 추가로 점검합니다.

마쳤다면 함수 인자를 값·참조·`const` 참조 중 무엇으로 받을지 설명하고, 객체의 소유자와 파괴 시점을 코드에서 짚어 보세요. 이어서 [Rust 튜토리얼](rust-tutorial.md)에서 소유권을 컴파일러가 검사하는 방식을 비교하거나 [역엔지니어링 과정](reverse-engineering/curriculum.md)으로 연결할 수 있습니다.
