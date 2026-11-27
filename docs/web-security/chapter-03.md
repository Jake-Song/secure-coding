# Chapter 3 개발자 도구와 Burp

[이전 Chapter 2](chapter-02.md) · [웹 보안 커리큘럼](curriculum.md) · [다음 Chapter 4](chapter-04.md)

개발자 도구는 해당 브라우저의 요청을 보여 줍니다. Burp Proxy는 브라우저와 서버 사이에서 요청과 응답을 기록하고, Repeater는 선택한 요청을 별도로 다시 보냅니다.

## 1. 로컬 앱을 띄우고 Burp에 첫 요청 기록하기

WSL의 저장소 루트에서 아래 명령을 실행하세요. 이미 `http://127.0.0.1:5000/`에 **로컬 보안 실습**이 열리면 그 서버를 사용합니다. [Chapter 2 실행 안내](chapter-02.md#1-flask-앱-실행하기)

```bash
source .venv/bin/activate
python app.py
```

1. Burp에서 **Proxy → Intercept → Open browser**를 누르세요. 버튼에 `Intercept is off`가 보이는 상태에서, 열린 Burp 내장 브라우저로 `http://127.0.0.1:5000/`에 접속하세요. [Burp 내장 브라우저](https://portswigger.net/burp/documentation/desktop/tools/burps-browser)
2. Burp의 **Proxy → HTTP history**에서 호스트가 `127.0.0.1:5000`이고 URL이 `/`인 `GET` 행을 선택하세요. **Request**에서 메서드와 경로, **Response**에서 상태 `200`과 시작 화면의 HTML을 확인합니다. `Intercept is off` 상태에서도 이 기록이 남습니다. [Burp HTTP history](https://portswigger.net/burp/documentation/desktop/tools/proxy/http-history)

기본 연결은 `브라우저 → Burp Proxy(8080) → Flask 앱(5000)`입니다. `8080`은 브라우저 요청을 받는 Burp의 기본 포트입니다. 주소창에는 목적지인 Flask 앱의 `5000`번 포트를 입력합니다. [Burp 프록시 설정](https://portswigger.net/burp/documentation/desktop/settings/tools/proxy)

## 2. 검색 요청을 중간에 멈추고 전달하기

1. Burp의 **Proxy → Intercept**에서 버튼을 눌러 `Intercept is on`으로 바꾸세요.
2. 내장 브라우저의 주소창에 `http://127.0.0.1:5000/safe/search?q=Note`를 입력하세요. 요청이 Burp에서 멈춰 있는 동안 브라우저는 응답을 기다립니다.
3. **Intercept** 화면에서 `/safe/search?q=Note` 요청을 찾아 `GET`, 목적지 `127.0.0.1:5000`, 검색어 `q=Note`를 확인하세요. **Forward**를 눌러 서버로 전달합니다. 이후 `Intercept is off`로 돌리고 브라우저에 `Notebook` 검색 결과가 표시되는지 보세요. [Burp Proxy의 Intercept와 Forward](https://portswigger.net/burp/documentation/desktop/tools/proxy/intercept-messages)

이 단계에서 본 것은 브라우저가 서버로 **보내려던 요청**입니다. 전달한 뒤 **HTTP history**에서 그 요청과 **서버가 돌려준 응답**을 함께 비교할 수 있습니다.

## 3. Repeater에서 검색어 하나만 바꿔 보기

1. **Proxy → HTTP history**에서 방금 보낸 `GET /safe/search?q=Note` 행을 우클릭하고 **Send to Repeater**를 누르세요.
2. **Repeater** 탭에서 복사된 요청을 보고 **Send**를 누르세요. 요청 첫 줄은 `GET /safe/search?q=Note HTTP/1.1`과 같은 형태입니다. **Response**의 `200`과 `Notebook`이 기준 결과입니다. [Burp Repeater에서 HTTP 요청 보내기](https://portswigger.net/burp/documentation/desktop/tools/repeater/http-messages)
3. **Request** 첫 줄의 `q=Note`를 `q=Pencil`로 바꾸고 다시 **Send**를 누르세요. 같은 자리를 `q=Zebra`로 바꿔 한 번 더 실행합니다. 검색어만 바꿔야 응답 차이를 해당 입력과 연결할 수 있습니다.

| 첫 줄에서 보낼 검색어 | 예상 상태 | 예상 응답 본문 |
|---|---:|---|
| `q=Note` | `200` | `[{"id":1,"name":"Notebook"}]` |
| `q=Pencil` | `200` | `[{"id":2,"name":"Pencil"}]` |
| `q=Zebra` | `200` | `[]` |

`200`은 서버가 검색 요청을 처리했다는 뜻입니다. 검색에 맞는 상품이 있는지는 JSON 본문을 보고 판단합니다. `safe_search()`가 `request.args`에서 `q`를 읽어 SQLite에 검색값으로 넘기는 부분도 찾아보세요. [검색 코드](../../app.py)

## 4. 브라우저의 로그인 상태가 요청에 담기는 위치 확인하기

Burp 내장 브라우저에서 [Chapter 2 정상 로그인](chapter-02.md#2-로그인-요청과-리다이렉트-관찰하기)을 하고 `http://127.0.0.1:5000/safe/notes/1`에서 Alice의 본인 메모를 여세요. **HTTP history**에서 해당 행을 선택해 다음 세 값을 비교합니다.

| 확인 대상 | 어디에서 보나요? | 의미 |
|---|---|---|
| 메모 ID `1` | **Request** 첫 줄의 `/safe/notes/1` | 브라우저가 요청한 객체 번호 |
| 세션 쿠키 | **Request**의 `Cookie` 헤더 | 서버가 로그인 상태를 확인하는 데 사용하는 값 |
| `id`와 `owner_id` | **Response**의 JSON | 서버가 반환한 메모 번호와 소유자 번호 |

서버는 URL에서 메모 ID를 읽고, 세션을 확인한 뒤 로그인 사용자의 ID를 얻습니다. 이 두 값을 소유권 조회의 조건으로 사용합니다.

## 5. Burp 기록과 코드로 취약점 근거 확인하기

1. Burp 내장 브라우저에서 [Chapter 2의 링크 비교](chapter-02.md#4-시작-화면의-취약한-링크와-방어한-링크-비교하기)를 진행하세요. Bob의 본인 메모, `Note` 검색, `Alice` 인사를 열고 **HTTP history**에서 취약한 링크와 방어한 링크의 정상 요청을 찾습니다.
2. 각 요청의 **Request**에서 `/notes/2`의 경로 변수 `2`, 검색의 `q`, 인사의 `name`을 찾으세요. **Response**에서 상태 코드와 응답 형식을 적습니다. 이 기록은 어떤 값이 서버에 들어가는지 보여 주는 출발점입니다.
3. [app.py](../../app.py)에서 해당 요청을 처리하는 함수로 이동해 그 값이 어디까지 전달되는지 따라가세요. 두 구현에서 아래 조건을 확인하면 각 취약점의 코드 근거를 찾을 수 있습니다.

| 화면의 링크 | 코드에서 확인할 근거 | 판정 |
|---|---|---|
| Bob 메모 조회 | `vulnerable_note()`의 `@login_required`는 로그인 여부를 확인합니다. 이어지는 쿼리에는 메모 `id`만 들어갑니다. `safe_note()`는 인증된 사용자의 ID를 `owner_id` 조건에도 전달합니다. | **IDOR.** 메모 조회 시 객체 소유권 검사가 빠져 있습니다. |
| 검색 | `vulnerable_search()`에서는 `request.args`의 `q`가 SQL 문자열에 합쳐진 뒤 `db.execute()`로 전달됩니다. `safe_search()`에는 고정된 `LIKE ?`와 별도로 전달하는 검색값이 있습니다. | **SQL 인젝션 위험.** 검색값이 SQL 문법에 영향을 줄 수 있습니다. |
| 인사 | `vulnerable_greet()`는 `name`을 응답 HTML 문자열에 바로 연결합니다. `safe_greet()`는 `{{ name }}`에 값을 넘겨 HTML 텍스트 문맥에서 이스케이프합니다. | **반사형 XSS 위험.** 요청 파라미터가 브라우저에서 해석할 HTML의 일부가 될 수 있습니다. |

예를 들어 검색 링크의 기록은 `q=Note → 200 → Notebook`으로 적으세요. 이어서 `vulnerable_search()`에서 `q`가 쿼리 문자열에 들어가는 줄, `safe_search()`에서 `q`가 바인딩 값으로 전달되는 줄을 나란히 적으세요. 상태 코드가 같아도 두 코드가 입력을 다루는 방식은 다릅니다.

### 방어 경로의 결과 확인하기

- **메모 소유권.** 저장소 루트의 가상환경에서 아래 테스트를 실행하세요. `OK`이면 본인 메모는 조회되고 타인 메모는 `404`로 거부되는 조건을 확인한 것입니다. [소유권 회귀 테스트](../../tests/test_app.py)

  ```bash
  python -m unittest tests.test_app.WebLabTests.test_safe_idor_allows_owner_and_blocks_other_user -v
  ```

- **검색값 처리.** 3절에서 캡처한 `/safe/search` 요청을 Repeater에서 열고 쿼리를 `q=O%27Reilly`로 바꿔 보내세요. `%27`은 따옴표 한 글자입니다. `O'Reilly`라는 검색어에 맞는 상품이 없으므로 예상 결과는 `200`과 `[]`입니다.
- **HTML 이스케이프.** Burp 브라우저에서 `http://127.0.0.1:5000/safe/greet?name=R%26D`를 여세요. `%26`은 `&` 한 글자입니다. 화면의 `Hello, R&D`와 **HTTP history → Response** 원본의 `<p>Hello, R&amp;D</p>`를 비교하세요.

**확인 문제.** `q=Note`와 `q=Zebra`가 모두 `200`일 때 검색 결과의 차이는 어디에서 보나요? `/safe/notes/1`에 대한 `200`과 함께 요청한 계정과 응답의 메모 ID를 기록하면 무엇을 확인할 수 있나요?

**제출물.** Repeater에서 검색어 세 개를 넣어 얻은 상태 코드와 응답 본문을 기록하세요. 메모 조회는 메서드·경로·입력·인증·인가를 열로 둔 표를 준비합니다. 링크 세 개에 대해 Burp에서 본 입력, 취약점의 근거가 되는 코드 줄, 방어 경로의 예상과 실제 결과도 적으세요. 쿠키, 비밀번호, 토큰은 가립니다.
