# Chapter 2 웹 앱 구조

[이전 Chapter 1](chapter-01.md) · [웹 보안 커리큘럼](curriculum.md) · [다음 Chapter 3](chapter-03.md)

라우팅은 HTTP 메서드와 경로에 맞는 Python 함수를 고르는 일입니다. 이번 실습에서는 브라우저의 로그인 요청을 Flask가 받아 처리하는 과정과, 이어진 메모 요청이 SQLite 조회를 거쳐 JSON 응답이 되는 과정을 따라갑니다. 마지막에는 HTML을 반환하는 읽기 전용 화면을 직접 추가합니다.

## 1. Flask 앱 실행하기

WSL 터미널을 열고 `app.py`가 있는 저장소 루트에서 아래 명령을 실행하세요. 처음 실행하는 경우에는 가상환경과 Flask를 먼저 준비합니다. [공통 준비](curriculum.md#공통-준비)

```bash
source .venv/bin/activate
python app.py
```

터미널에 `Running on http://127.0.0.1:5000`이 보이면 서버가 요청을 기다리는 중입니다. 터미널은 켜 둔 채, 브라우저에서 `http://127.0.0.1:5000/`을 여세요. **로컬 보안 실습** 제목과 로그인 폼이 보입니다. 새 터미널에서도 시작 화면의 응답을 확인할 수 있습니다.

```bash
curl --noproxy '*' -i http://127.0.0.1:5000/
```

`-i`는 응답 헤더를 본문과 함께 보여 줍니다. 첫 줄에서 `HTTP/1.0 200 OK`처럼 상태 코드 `200`을 확인하고, 본문에서 로그인 폼 HTML을 찾으세요. 브라우저는 HTML을 읽고 화면에 폼을 그립니다. 서버를 종료하려면 실행한 터미널에서 `Ctrl+C`를 누르세요.

실행할 때 `Port 5000 is in use`가 나오면 먼저 위 주소를 열어 이미 **로컬 보안 실습** 화면이 떠 있는지 확인하세요. 같은 앱이라면 그 서버에서 실습을 이어갈 수 있습니다. 다른 프로그램이 사용 중이라면 WSL에서 `ss -ltnp 'sport = :5000'`으로 포트를 쓰는 프로세스를 확인하세요.

## 2. 로그인 요청과 리다이렉트 관찰하기

1. 브라우저에서 `F12`를 눌러 개발자 도구를 열고 **Network** 탭을 선택하세요. **Preserve log**를 켜 두면 다음 페이지로 이동한 뒤에도 로그인 요청이 목록에 남습니다. [Chrome DevTools Network 안내](https://developer.chrome.com/docs/devtools/network/reference/)
2. 시작 화면을 새로 고치고 **로그인**을 누르세요. 예제 폼에는 계정 `alice`와 비밀번호 `alice-lab`이 채워져 있습니다. 이미 로그인한 상태라면 로그아웃하고 다시 시작하세요.
3. Network 목록에서 `login` 행을 열고 **Headers → General**에서 메서드 `POST`와 상태 코드 `302`를 확인하세요. **Payload → Form Data**에서 `username`, `password`, `csrf` 필드를 찾으세요. `csrf`는 시작 화면의 숨은 폼 필드에서 함께 전송됩니다.
4. 같은 행의 **Response Headers**에서 `Location: /`와 `Set-Cookie`를 찾으세요. `Location: /`를 받은 브라우저가 `GET /`를 다시 보내면 `200 OK` 응답에 `로그인: alice`가 표시됩니다. 비밀번호, 쿠키 값, 토큰은 화면이나 요청을 공유할 때 가립니다.

| 순서 | 요청 | 응답 | 의미 |
|---:|---|---|---|
| 1 | `GET /` | `200` | 로그인 폼 HTML을 받습니다. |
| 2 | `POST /login` | `302` | 로그인 처리를 마친 서버가 쿠키를 설정하고 `/`로 다시 이동하라고 응답합니다. |
| 3 | `GET /` | `200` | 새 쿠키를 보낸 브라우저가 로그인 상태의 HTML을 받습니다. |

## 3. 본인 메모를 조회하고 코드에서 요청 따라가기

Alice로 로그인한 **같은 브라우저**에서 `http://127.0.0.1:5000/safe/notes/1`을 여세요. Network의 새 요청 행을 클릭하면 `GET`, `200`, `Content-Type: application/json`을 확인할 수 있습니다. **Response**에는 다음 JSON이 표시됩니다.

```json
{"body":"Alice private memo","id":1,"owner_id":1}
```

`id`는 메모 번호, `owner_id`는 소유자의 사용자 번호, `body`는 본문입니다. 새 터미널에서 아래 명령을 실행하면 브라우저 세션 쿠키 없이 같은 메모를 요청하므로 `401 UNAUTHORIZED`가 반환됩니다. 이 차이로 로그인 상태가 요청에 어떻게 전달되는지 확인할 수 있습니다.

```bash
curl --noproxy '*' -i http://127.0.0.1:5000/safe/notes/1
```

[app.py](../../app.py)에서 아래 함수를 찾아, 개발자 도구에서 본 동작과 연결하세요.

| 함수 | 코드에서 찾아볼 부분 |
|---|---|
| `create_app()` | Flask 앱을 만들고 메모리 SQLite에 `users`, `notes`와 실습 데이터를 넣습니다. |
| `login()` | `request.form`의 사용자 이름으로 사용자 행을 찾고 비밀번호를 검사합니다. 성공하면 새 세션 식별자 `sid`를 만들고 `active_sessions[sid]`에 사용자 ID를 저장한 뒤 `redirect("/")`를 반환합니다. |
| `current_user()` | Flask가 서명된 세션 쿠키에서 읽은 `sid`로 `active_sessions`를 조회합니다. 그 사용자 ID로 SQLite에서 사용자 행을 찾습니다. |
| `safe_note(note_id)` | `@login_required` 검사를 거쳐, 경로의 메모 ID와 로그인한 사용자의 ID를 SQLite 쿼리의 `id`와 `owner_id` 조건에 각각 넣습니다. 일치하는 행을 `jsonify`로 반환합니다. |

로그아웃하면 서버가 `active_sessions`에서 해당 `sid`를 지웁니다. 확인하려면 시작 화면으로 돌아가 **로그아웃**한 뒤 `http://127.0.0.1:5000/session`을 여세요. 응답에서 `username`이 `null`로 돌아옵니다.

## 4. 시작 화면의 취약한 링크와 방어한 링크 비교하기

시작 화면의 링크는 **정상 동작이 두 구현에서 유지되는지** 확인하기 위한 예제입니다. Bob의 본인 메모, 검색어 `Note`, 이름 `Alice`를 사용하면 두 구현 모두 `200`을 반환하고 화면에 표시되는 내용도 같습니다. 이 결과를 기준으로 삼고, 아래에서 입력을 하나씩 바꿔 검색 상태 코드와 인사 화면을 비교합니다.

1. `http://127.0.0.1:5000/`에서 **Network** 탭과 **Preserve log**를 켜세요. Alice로 로그인한 상태라면 로그아웃하고, `bob` / `bob-lab`으로 로그인하세요. 화면의 `로그인: bob`을 확인하면 메모 2를 소유한 계정으로 실습 중입니다.
2. **취약한 Bob 메모 조회**를 누르세요. `GET /vuln/notes/2`의 **Response**에서 `id: 2`, `owner_id: 2`, `body: Bob private memo`를 확인하세요. 브라우저의 뒤로 가기로 시작 화면에 돌아와 **방어한 Bob 메모 조회**를 누르면 `GET /safe/notes/2`에서도 같은 본인 메모가 나옵니다.
3. 시작 화면으로 돌아올 때마다 아래 표의 검색과 인사 링크를 쌍으로 열어 보세요. Network에서 **Headers**의 요청 경로·상태 코드와 **Response**의 본문을 확인합니다.

| 시작 화면의 링크 쌍 | 요청 경로와 쿼리 | 정상 결과 |
|---|---|---|
| 취약한 / 방어한 Bob 메모 조회 | `/vuln/notes/2`, `/safe/notes/2` | `200`, Bob의 메모 2를 담은 JSON |
| 취약한 / 방어한 검색 | `/vuln/search?q=Note`, `/safe/search?q=Note` | `200`, `[{"id":1,"name":"Notebook"}]` JSON |
| 취약한 / 방어한 인사 | `/vuln/greet?name=Alice`, `/safe/greet?name=Alice` | `200`, 화면에 `Hello, Alice`가 표시되는 HTML |

`/notes/2`의 `2`는 **경로 변수**이고, `q=Note`와 `name=Alice`는 `?` 뒤에 오는 **쿼리 파라미터**입니다.

### 검색어에 작은따옴표가 있을 때

같은 검색어 `O'Reilly`를 두 구현에 보내 보세요. `%27`은 작은따옴표 한 글자를 URL로 보내는 표현입니다. 주소를 하나씩 열고 **Network → Headers → Status Code**를 확인합니다.

| 주소 | 상태 | 화면 |
|---|---:|---|
| `http://127.0.0.1:5000/vuln/search?q=O%27Reilly` | `400` | `Bad Request` 오류 페이지 |
| `http://127.0.0.1:5000/safe/search?q=O%27Reilly` | `200` | 빈 결과 `[]` |

취약한 검색은 검색어를 SQL 문자열에 붙이므로 이름 속 작은따옴표에서 SQL 문자열이 끊기고 조회가 실패합니다. 방어한 검색은 `O'Reilly` 전체를 하나의 검색값으로 전달합니다. 일치하는 상품이 없어서 결과는 빈 배열입니다.

### 인사말에 HTML 문자 참조가 있을 때

두 인사 주소는 모두 이름 칸에 `A &copy; B`라는 글자를 전달합니다. 주소를 하나씩 열고 브라우저 화면을 비교하세요. 이어서 **Network → 해당 요청 → Response**에서 원본 HTML의 `<p>` 부분을 확인합니다.

| 주소 | 화면 | 응답 HTML의 `<p>` 부분 |
|---|---|---|
| `http://127.0.0.1:5000/vuln/greet?name=A%20%26copy%3B%20B` | `Hello, A © B` | `<p>Hello, A &copy; B</p>` |
| `http://127.0.0.1:5000/safe/greet?name=A%20%26copy%3B%20B` | `Hello, A &copy; B` | `<p>Hello, A &amp;copy; B</p>` |

취약한 인사에선 브라우저가 원본 HTML의 `&copy;`를 읽어 `©`로 표시합니다. 방어한 인사는 템플릿이 입력의 `&`를 `&amp;`로 바꿔 보냅니다. 브라우저는 그 부분을 `&`로 표시하고 뒤의 `copy;`는 그대로 보이므로 화면에 입력한 글자가 보존됩니다.

저장소 루트에서 아래 명령으로 메모 조회·검색·인사의 처리 함수 위치를 찾고, [app.py](../../app.py)의 코드를 비교하세요.

```bash
rg -n 'def (vulnerable|safe)_(note|search|greet)\(' app.py
```

| 기능 | 취약한 구현의 처리 | 방어한 구현의 처리 |
|---|---|---|
| 메모 조회 | 로그인은 확인하지만 조회 조건에는 메모 `id`만 들어갑니다. | 로그인 사용자의 `owner_id`도 조회 조건에 넣습니다. [Chapter 4 객체 접근 제어](chapter-04.md) |
| 검색 | 검색어 `q`를 SQL 문자열에 직접 붙여, 입력이 SQL 문법에 영향을 줄 수 있습니다. | SQL에 `LIKE ?`를 두고 검색어를 별도 값으로 바인딩합니다. [Chapter 5 파라미터 바인딩](chapter-05.md) |
| 인사 | `name`을 응답 HTML에 직접 붙여, 브라우저가 입력을 HTML 구조로 해석할 수 있습니다. | `{{ name }}` 템플릿 변수에 넣어 HTML 텍스트 문맥에서 이스케이프합니다. [Chapter 6 XSS와 출력 문맥](chapter-06.md) |

## 5. 읽기 전용 `/about` 만들기

1. [app.py](../../app.py)에서 `@app.get("/session")`을 찾으세요. 그 줄 **바로 위에** 아래 코드를 넣습니다. 기존 라우트와 같은 깊이인 공백 네 칸으로 시작해야 `create_app()` 안에서 등록됩니다. `render_template_string`은 파일 상단에서 이미 가져옵니다.

   ```python
       @app.get("/about")
       def about():
           return render_template_string(
               """<!doctype html>
               <html lang="ko">
               <head><meta charset="utf-8"><title>실습 안내</title></head>
               <body><h1>{{ title }}</h1></body>
               </html>""",
               title="메모 & 검색 <연습>",
           )
   ```

2. 파일을 저장하세요. 서버를 띄운 터미널에서 `Ctrl+C`를 누르고 `python app.py`로 다시 실행합니다. 브라우저에서 `http://127.0.0.1:5000/about`을 열면 화면에 **메모 & 검색 <연습>**이 표시됩니다.
3. 별도 터미널에서 아래 명령으로 원본 응답을 확인하세요.

   ```bash
   curl --noproxy '*' -i http://127.0.0.1:5000/about
   ```

   예상 상태는 `200 OK`이고, 본문의 제목은 `<h1>메모 &amp; 검색 &lt;연습&gt;</h1>`입니다. Flask는 템플릿 변수의 특수문자를 HTML에서 텍스트로 읽히는 표현으로 바꿉니다. 브라우저는 `&amp;`를 `&`로, `&lt;`와 `&gt;`를 `<`와 `>`로 화면에 표시합니다. [Flask 템플릿 안내](https://flask.palletsprojects.com/en/stable/templating/#jinja-setup)

`/about`이 `404`를 반환하면 라우트의 들여쓰기와 서버를 재시작했는지 확인하세요. 서버를 재시작하면 메모리 데이터베이스와 세션이 초기화되므로, 메모 조회를 다시 실습할 때는 로그인부터 진행합니다.

**확인 문제.** `/safe/notes/1`의 `1`과 SQL의 `owner_id`에 들어가는 사용자 ID는 각각 어디에서 오나요? 검색 링크의 `q`는 두 구현에서 SQLite에 어떻게 전달되나요? `/about`의 화면과 응답 HTML에서 같은 문자가 다르게 보이는 이유는 무엇인가요?

**제출물.** 로그인과 메모 조회의 요청·응답 흐름을 `브라우저 → Flask 라우트 → SQLite → 응답` 순서로 그리세요. `/about`은 상태 코드, 응답 HTML의 `<h1>` 한 줄, 화면에 표시된 제목을 함께 기록하세요.
