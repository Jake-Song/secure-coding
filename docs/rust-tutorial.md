# Rust 입문 튜토리얼

기본 문법부터 **소유권·빌림·오류 처리·파일 저장**까지 배우는 실습입니다. [C 튜토리얼](c-tutorial.md)이나 [C++ 튜토리얼](cpp-tutorial.md)을 배웠다면 메모리 관리 방법을 비교해 보세요. 다른 언어를 먼저 배울 필요는 없습니다.

Linux, macOS 또는 Windows의 WSL 터미널을 기준으로 합니다. 이 예제는 **Rust 2021 edition**을 사용하며 외부 크레이트가 없습니다. 최신 edition을 설명하는 과정은 아니며, edition은 컴파일러 버전과 별도의 언어 규칙 선택입니다.

## 준비와 전체 실행

Rust 도구 설치 후 저장소 루트에서 실행합니다.

```bash
rustc --version
cargo --version
cargo build --offline --manifest-path examples/rust_tutorial/Cargo.toml
cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin hello
```

`rustc`는 컴파일러, Cargo는 프로젝트 빌드·실행·의존성을 관리하는 도구입니다. Rust 도구가 없다면 [공식 설치 안내](https://rust-lang.org/tools/install/)에 따라 rustup으로 설치하고 터미널을 다시 열어 위 두 버전을 확인합니다. `command not found`는 도구가 없거나 실행 파일 경로가 `PATH`에 없다는 뜻입니다. rustup의 일반 설치 경로는 `~/.cargo/bin`입니다.

이 저장소는 [Cargo.toml](../examples/rust_tutorial/Cargo.toml)의 `[[bin]]`으로 예제별 실행 대상을 지정합니다. 결과물은 `examples/rust_tutorial/target/`에 생성됩니다. `--bin` 뒤의 이름으로 원하는 예제만 실행할 수 있습니다.

| 단계 | 주제 | 소스 | `--bin` 이름 |
|---|---|---|---|
| 1 | 함수·출력·컴파일 | [01_hello.rs](../examples/rust_tutorial/01_hello.rs) | `hello` |
| 2 | 변수·자료형·조건·반복 | [02_basics.rs](../examples/rust_tutorial/02_basics.rs) | `basics` |
| 3 | 소유권·이동·빌림 | [03_ownership.rs](../examples/rust_tutorial/03_ownership.rs) | `ownership` |
| 4 | 구조체·메서드·enum | [04_structs.rs](../examples/rust_tutorial/04_structs.rs) | `structs` |
| 5 | Vec·맵·이터레이터·Option | [05_collections.rs](../examples/rust_tutorial/05_collections.rs) | `collections` |
| 6 | Result·match·`?` | [06_errors.rs](../examples/rust_tutorial/06_errors.rs) | `errors` |
| 7 | 입력 검증 | [07_input.rs](../examples/rust_tutorial/07_input.rs) | `input` |
| 8 | 명령행 인자·파일 저장 | [08_score_report.rs](../examples/rust_tutorial/08_score_report.rs) | `score_report` |

이후 예제는 먼저 출력을 예상한 뒤 실행합니다. `cargo run`의 빌드 안내 메시지와 프로그램의 실제 출력을 구별하세요.

## 1. 첫 프로그램

```rust
fn main() {
    println!("Hello, Rust!");
}
```

`fn`은 함수 정의, `main`은 시작 함수, 중괄호는 실행 범위입니다. `println!`은 줄바꿈을 포함해 출력하는 매크로입니다. `!`로 매크로 호출임을 구별합니다. `;`는 문장을 끝냅니다.

`cargo run ... --bin hello`의 프로그램 출력은 `Hello, Rust!`입니다. Cargo 없이 컴파일러를 직접 사용할 수도 있습니다.

```bash
mkdir -p examples/rust_tutorial/target/manual
rustc --edition=2021 --crate-name tutorial_hello \
  examples/rust_tutorial/01_hello.rs \
  -o examples/rust_tutorial/target/manual/hello
./examples/rust_tutorial/target/manual/hello
```

소스를 고치면 다시 빌드해야 합니다. Cargo의 `run`은 변경된 소스를 먼저 빌드하고 실행합니다.

**수정 과제:** 두 번째 줄에 정수 42를 출력합니다. `println!("answer={}", 42)`와 이름 있는 변수 출력 `println!("{answer}")`를 비교합니다.

## 2. 변수·조건·반복·함수

```rust
let mut score: i32 = 85;
let pass_mark = 60;
let passed = score >= pass_mark;
```

변수는 기본적으로 변경할 수 없습니다. 다시 대입하려면 `mut`를 붙입니다. `i32`는 32비트 signed 정수이고, `u32`는 32비트 unsigned 정수입니다. `bool`은 참·거짓, `f64`는 64비트 부동소수점, `usize`는 크기와 인덱스에 사용합니다. Rust의 `char`는 유니코드 스칼라 값이며 UTF-8 한 바이트와 다릅니다.

`let passed = ...`의 자료형은 컴파일 시 추론되어 `bool`이 됩니다. `let score = ...`로 이름을 다시 선언하는 섀도잉과 `mut` 변수에 재대입하는 것은 서로 다른 동작입니다.

```rust
let outcome = if score >= pass_mark { "pass" } else { "retry" };
let mut total = 0;
for number in 1..=5 {
    total += number;
}
```

`if`는 값을 만드는 표현식이며 두 분기의 자료형을 맞춰야 합니다. `1..=5`는 1~5, `1..5`는 1~4 범위입니다. `while`은 조건 반복, `loop`는 `break` 전까지 반복합니다. `=`는 대입, `==`는 비교이며 `&&`, `||`, `!`는 논리 연산입니다.

```rust
fn add_one(value: &mut i32) {
    *value += 1;
}
```

함수 인자는 `이름: 자료형`으로 선언합니다. `&mut i32`는 정수를 수정할 수 있도록 빌린 참조입니다. 호출은 `add_one(&mut score)`입니다. 값을 반환한다면 `fn double(value: i32) -> i32 { value * 2 }`처럼 작성합니다. 마지막 표현식의 세미콜론을 생략하면 그 값이 반환됩니다.

```bash
cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin basics
```

```text
passed=true
sum 1..5=15
score=86 pass
first=70 count=3
```

`[70, 80, 90]`은 길이가 고정된 배열입니다. 첫 인덱스는 0이며 범위 밖 인덱싱은 오류를 일으킵니다. Rust가 모든 산술 오류를 컴파일 때 막는 것은 아닙니다. 기본 개발 빌드의 정수 오버플로 검사는 패닉을 발생시키며, 기본 릴리스 빌드는 동작이 다를 수 있습니다. 입력에 따라 범위를 넘을 수 있다면 `checked_add` 등의 연산으로 처리 방법을 정합니다.

**수정 과제:** 합계를 1~10으로 바꾸어 55를 확인합니다. `mut`를 지운 뒤 점수를 바꾸려 하면 어떤 오류가 나오는지도 읽어 봅니다.

## 3. 소유권·이동·빌림

```rust
let original = String::from("Alice");
let mut owner = original;
```

`String`은 소유한 UTF-8 문자열입니다. 위 대입은 문자열의 소유권을 `owner`로 **이동**합니다. 이제 `original`을 다시 사용할 수 없습니다. 소유자가 수명을 마치면 문자열의 저장 공간도 정리됩니다.

아래 코드는 규칙을 확인하기 위한 **컴파일 실패 예시**입니다. 실행 예제 파일에는 넣지 않았습니다.

```rust
let name = String::from("Alice");
let next = name;
println!("{name} {next}"); // 이동한 name 사용: 오류
```

`i32`처럼 `Copy`를 구현한 자료형은 대입해도 원본을 계속 사용할 수 있습니다. `String::clone()`은 별도의 문자열 데이터를 복사합니다. 컴파일 오류를 피하려고 무조건 `clone`하기보다, 읽기만 필요하면 빌림을 사용합니다.

```rust
fn byte_count(text: &str) -> usize {
    text.len()
}

fn add_suffix(text: &mut String) {
    text.push_str(" Lee");
}
```

`&str`는 문자열 데이터를 읽도록 빌린 슬라이스입니다. `&mut String`은 소유권을 넘기지 않고 문자열을 수정하도록 빌립니다. 참조는 대상보다 오래 사용할 수 없습니다.

같은 데이터에 대해 사용하는 동안에는 여러 공유 참조 또는 하나의 배타적 가변 참조를 허용합니다. 다음처럼 공유 참조를 나중에 사용할 상황에서 원본을 수정할 수 없습니다.

```rust
let mut name = String::from("Alice");
let view = &name;
name.push('!');             // view가 아래에서 사용되므로 오류
println!("{view}");
```

컴파일러는 참조가 실제로 사용되는 구간을 고려합니다. `view`의 마지막 사용이 수정 전이면 코드가 허용될 수도 있으므로 단순히 중괄호 범위만으로 판단하지 않습니다.

```bash
cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin ownership
```

```text
name=Alice bytes=5
owner=Alice Lee copy=Alice Lee
first word=Alice
```

`len()`은 바이트 수입니다. 예제의 `&owner[..5]`는 ASCII 문자열의 유효한 바이트 경계입니다. UTF-8 문자 중간을 자르면 패닉이 발생합니다. 한글을 처리할 때는 `chars()` 등으로 문자 단위 순회를 고려합니다.

**수정 과제:** 원본을 읽는 함수와 수정하는 함수를 각각 작성합니다. 위 두 실패 예시를 별도 임시 파일에 넣어 오류를 확인한 뒤 빌림 순서로 해결해 봅니다.

## 4. 구조체·메서드·enum

```rust
struct Student {
    name: String,
    score: u32,
}

enum Assessment {
    Passed,
    Retry,
}
```

구조체는 관련 데이터를 묶습니다. `impl Student { ... }` 안에 연관 함수와 메서드를 정의합니다. `Student::new(...)`는 생성 용도로 이름 붙인 연관 함수이며 언어가 특별 취급하는 생성자는 아닙니다. `&self`를 받는 메서드는 객체를 빌려 읽습니다.

```rust
let outcome = match student.assessment() {
    Assessment::Passed => "pass",
    Assessment::Retry => "retry",
};
```

`enum`은 여러 경우 중 하나를 표현하고 `match`는 각 경우를 처리합니다. 모든 가능한 경우를 다뤄야 하므로 새로운 종류를 추가하면 누락된 처리를 컴파일러가 알려줄 수 있습니다. Rust의 enum은 각 경우에 다른 데이터를 담을 수도 있습니다.

생성 함수는 잘못된 점수를 `Result`로 반환합니다. 이는 성공값 또는 오류를 표현하며 6단계에서 더 자세히 봅니다. 필드 접근은 Rust의 모듈별 공개 범위를 따릅니다. 같은 모듈 안의 모든 필드 수정을 생성 함수가 자동으로 막아 주는 것은 아닙니다.

```bash
cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin structs
```

```text
Alice: 85 (pass)
rejected: score must be from 0 to 100
```

고정된 유효 값에만 사용한 `expect`는 실패하면 패닉을 발생시킵니다. 사용자 입력의 실패를 처리하는 일반 수단으로 쓰지 않습니다.

**수정 과제:** `Assessment`에 우수 성적을 추가하고 `match`를 보완합니다. 점수 수정 메서드를 추가할 때도 0~100 규칙을 유지합니다.

## 5. 컬렉션·이터레이터·`Option`

```rust
let mut scores = vec![90_u32, 50, 80];
scores.push(60);
scores.sort_unstable();
let passed = scores.iter().filter(|&&score| score >= 60).count();
```

`Vec<T>`는 크기를 조절할 수 있는 원소 목록, `vec![]`는 벡터 생성 매크로입니다. `.iter()`는 원소를 빌리는 이터레이터이고, `.filter(...)`는 조건에 맞는 원소만 남기는 어댑터입니다. 마지막 `.count()`가 순회하며 개수를 셉니다.

`|&&score| score >= 60`은 클로저입니다. `iter`가 원소의 참조를 만들고 `filter`가 그 항목을 참조로 받으므로 여기서는 두 겹의 참조를 패턴으로 풀었습니다. `sum()`의 반환 자료형은 `let total: u32`처럼 지정할 수 있습니다.

```rust
fn first<T>(values: &[T]) -> Option<&T> {
    values.first()
}
```

`<T>`는 여러 자료형에 적용하는 제네릭 매개변수, `&[T]`는 원소 목록을 빌린 슬라이스입니다. `Option<&T>`는 `Some(참조)` 또는 `None`입니다. 빈 목록도 유효한 입력이므로 값이 없음을 명시적으로 표현합니다. 반환 참조는 입력 데이터보다 오래 사용할 수 없습니다. 이 간단한 함수에서는 그 관계를 컴파일러가 수명 생략 규칙으로 처리합니다.

예제는 키별 횟수를 세기 위해 `BTreeMap`도 사용합니다. 키 순서로 순회하므로 출력 순서가 일정합니다. `entry(name).or_insert(0)`은 키가 없으면 0을 넣고 저장된 값에 대한 가변 참조를 반환합니다.

```bash
cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin collections
```

```text
[50, 60, 80, 90]
count=4 total=280 passed=3
first=50
Alice=2
Bob=1
```

`{:?}`는 디버그 형식 출력입니다. 이 합산은 고정된 작은 점수용입니다.

**수정 과제:** 빈 벡터에 `first`를 호출해 `None`을 처리합니다. 합격 기준을 80으로 바꾸고 이름을 추가해 횟수 집계를 확인합니다.

## 6. `Result`와 `?`로 오류 전달하기

공용 모듈 [score.rs](../examples/rust_tutorial/score.rs)는 `Result<u32, &'static str>`를 반환합니다. `Ok(score)`는 성공한 점수이고 `Err(message)`는 실패 이유입니다. `&'static str`는 프로그램 실행 동안 유효한 문자열 슬라이스이며, 여기서는 고정된 오류 메시지를 가리킵니다.

```rust
fn doubled_score(text: &str) -> Result<u32, &'static str> {
    let score = score::parse_score(text)?;
    Ok(score * 2)
}
```

`?`는 성공값을 꺼내고, 오류면 현재 함수에서 오류를 반환합니다. 가능한 오류 변환이 있으면 호출 함수의 오류형으로 변환합니다. `map_err`는 성공값을 유지하고 오류만 다른 형태로 바꿉니다. `match`로 성공과 실패를 직접 나눠 처리할 수도 있습니다.

`mod score;`는 이 소스에서 같은 디렉터리의 `score.rs`를 모듈로 포함합니다. 해당 모듈의 공개 함수는 `score::parse_score`로 호출합니다.

```bash
cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin errors
```

```text
85: doubled=170
101: rejected: score must be from 0 to 100
bad: rejected: expected ASCII digits representing a score from 0 to 100
```

`Option`은 값이 없음을, `Result`는 실패 이유까지 표현합니다. `unwrap`·`expect`는 실패를 패닉으로 바꾸므로 예상 가능한 입력 오류에는 보통 `match`나 `?`를 사용합니다.

**수정 과제:** 입력 파싱 오류를 숫자 형식 오류와 점수 범위 오류로 나눈 enum으로 바꿔 봅니다. 오류의 종류마다 다른 메시지를 출력합니다.

## 7. 표준 입력과 검증

```bash
printf '85\n' | cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin input
printf '101\n' | cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml --bin input
```

첫 입력은 `accepted=85`, 두 번째는 오류를 출력하고 실패 종료합니다. 직접 실행한 뒤 숫자와 Enter를 입력해도 됩니다.

`read_line(&mut line)`은 문자열에 입력을 추가합니다. 예제는 매번 빈 `String`을 만들고 한 줄만 읽습니다. 입력 끝의 LF와 선택적인 CR을 제거해 Windows식 CRLF도 처리합니다. `run() -> Result<(), String>`에서 `()`는 성공 때 별도 반환값이 없음을 나타냅니다.

입력 규칙:

- ASCII 숫자로 표현한 0~100, 최대 62바이트를 허용합니다. `001`은 1입니다.
- 공백·부호·소수·문자가 섞인 숫자·널 문자는 거부합니다.
- 짧은 숫자 뒤 줄바꿈 없는 EOF는 허용합니다. 입력 자체가 없는 EOF와 빈 줄은 실패합니다.
- `read_line`은 UTF-8 문자열을 읽고, 잘못된 UTF-8은 읽기 오류로 처리합니다.
- 길이 검사는 읽은 뒤 수행합니다. 메모리 할당 상한은 아니므로 신뢰할 수 없는 대용량 입력에는 제한된 읽기를 별도로 구현합니다.

`main`은 성공을 `ExitCode::SUCCESS`, 오류를 `ExitCode::FAILURE`로 반환하고 `eprintln!`으로 표준 오류에 메시지를 출력합니다. `?`로 오류를 전달하면 오류 경로에서도 소유한 문자열·벡터가 정리됩니다.

**수정 과제:** `0`, `100`, `-1`, `+85`, 빈 줄, 아주 큰 수를 검사합니다. 입력 반복 기능을 추가하면 `read_line` 호출 전에 기존 문자열을 비우는 이유도 확인합니다.

## 8. 종합 실습: 성적 CSV 저장

Cargo가 실행할 프로그램에 인자를 전달할 때는 **`--` 뒤**에 넣습니다.

```bash
report_dir=$(mktemp -d)
cargo run --offline --manifest-path examples/rust_tutorial/Cargo.toml \
  --bin score_report -- "$report_dir/scores.csv" 70 80 90
cat "$report_dir/scores.csv"
```

프로그램 출력은 `report saved`이며, 파일 내용은 다음과 같습니다.

```csv
count,total,average
3,240,80.00
```

소스는 다음 순서로 읽습니다.

1. `env::args_os().skip(1)`로 프로그램 이름을 제외한 인자를 받습니다. 파일 경로는 운영체제 문자열 그대로 유지하고, 점수 인자만 문자열로 변환합니다.
2. 점수 1~100개를 검증해 벡터에 저장합니다. 최대 합계는 10,000입니다. 형식 오류·범위 초과·점수 개수 초과 시 파일을 만들기 전에 실패합니다.
3. `f64::from(total)`과 개수 변환으로 실수 평균을 계산합니다. 개수가 최대 100이므로 이 예제의 변환은 정확합니다.
4. `OpenOptions`의 `create_new(true)`로 새 파일만 생성합니다. 기존 경로가 있으면 실패하며 파일 존재 검사 후 생성 사이의 틈에 의존하지 않습니다.
5. `writeln!`으로 데이터를 쓰고 `sync_all` 결과까지 검사합니다. 파일 객체는 범위를 벗어날 때 자동으로 닫힙니다.

같은 파일 경로로 재실행하면 실패하며 기존 내용은 유지됩니다. `101`을 점수로 넣으면 실패하고 새 파일을 만들지 않습니다. 생성 후 쓰기·동기화가 실패하면 불완전한 새 파일이 남을 수 있습니다.

**확장 과제:** 최솟값·최댓값을 추가합니다. `std::fs::read_to_string`으로 보고서를 다시 읽는 기능을 만들되, 잘못된 UTF-8·숫자·빈 파일·누락된 행을 처리합니다.

## 검증과 다음 단계

Python 3와 `rustc`가 있으면 실행 결과·입력 경계·파일 보존을 검사합니다. 컴파일러가 없으면 Rust 테스트를 건너뜁니다.

```bash
python3 -m unittest tests.test_cpp_rust_tutorials.RustTutorialTests -v
```

테스트는 예제를 경고를 오류로 처리해 컴파일하며, 소유권 이동 뒤 사용과 충돌하는 빌림이 컴파일에 실패하는지도 확인합니다. 다른 위치의 컴파일러를 사용하려면 `RUSTC=/실제/경로/rustc` 환경 변수로 지정할 수 있습니다. Cargo 실행 시에도 같은 변수를 사용할 수 있습니다.

마쳤다면 함수가 소유권을 받는지, 공유 참조를 받는지, 가변 참조를 받는지 설명해 보세요. 이어서 trait·수명 매개변수·모듈 공개 범위·단위 테스트·스레드를 학습할 수 있습니다. 안전한 Rust도 논리 오류·자원 고갈·패닉까지 모두 막지는 않습니다. `unsafe` 코드는 별도의 계약을 지켜야 하므로 이 입문 예제에서는 사용하지 않습니다.
