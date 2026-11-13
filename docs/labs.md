# 취약점별 실습 안내

모든 명령은 저장소 루트에서 가상환경을 활성화한 상태로 실행합니다. 먼저 `python app.py`를 실행하고 <http://127.0.0.1:5000>에서 Alice로 로그인합니다. 계정은 `alice / alice-lab`, `bob / bob-lab`입니다.

각 실습에서 **정상 동작 → 취약점 재현 → 원인 코드 → 방어 비교 → 회귀 테스트**를 기록합니다. 아래 HTTP 요청은 쿠키를 사용하는 동일한 브라우저 또는 Burp Repeater에서 보냅니다. `http_demo.py`로 다섯 웹 취약점을 자동 비교할 수도 있습니다.

```bash
python examples/http_demo.py
```

비교 스크립트는 응답을 출력하며 Alice의 상태를 변경합니다. 독립 실습 전에는 앱을 재시작하세요. 자동 비교 자체는 테스트 판정기가 아니며, 검증은 `python -m unittest discover -s tests -v`로 수행합니다.

## 실습 1: 접근 제어와 IDOR

### 정상 동작과 재현

Alice로 로그인한 상태에서 다음 URL을 엽니다.

```text
http://127.0.0.1:5000/vuln/notes/1
http://127.0.0.1:5000/vuln/notes/2
http://127.0.0.1:5000/safe/notes/1
http://127.0.0.1:5000/safe/notes/2
```

| 계정 | 요청 | 예상 결과 |
|---|---|---|
| Alice | `/vuln/notes/2` | 200, Bob의 비공개 메모 노출 |
| Alice | `/safe/notes/1` | 200, 본인 메모 |
| Alice | `/safe/notes/2` | 404, 메모 미노출 |
| Bob | `/safe/notes/2` | 200, 본인 메모 |
| 비로그인 | 두 버전의 메모 요청 | 401 |

### 원인과 수정

취약 코드는 `id`만으로 조회합니다. 방어 코드는 서버가 검증한 사용자 ID와 `owner_id`를 함께 비교합니다. 클라이언트가 보낸 `owner_id`로 검사하면 안 됩니다. 여기서는 존재 여부를 일관되게 숨기기 위해 타인 객체와 없는 객체 모두 404를 반환합니다.

과제: 테스트의 Alice/Bob 접근 행렬을 읽고 `/vuln/notes/`를 직접 수정합니다. UUID로 ID를 바꾸는 것만으로 인가가 완성되지 않는 이유를 적습니다.

## 실습 2: SQL 인젝션

정상 검색:

```bash
curl --noproxy '*' --get --data-urlencode 'q=Note' http://127.0.0.1:5000/safe/search
```

교육용 DB의 메모를 검색 결과에 섞는 요청:

```bash
curl --noproxy '*' --get \
  --data-urlencode "q=x' UNION SELECT id, body FROM notes -- " \
  http://127.0.0.1:5000/vuln/search
```

같은 입력을 `/safe/search`로 보내면 빈 목록이 반환됩니다. 이 예제는 단일 SELECT의 구조를 바꾸는 SQLi이며, 다중 SQL 문장 실행에 의존하지 않습니다.

취약 코드:

```python
sql = f"SELECT id, name FROM products WHERE name LIKE '%{q}%'"
```

방어 코드:

```python
db.execute("SELECT id, name FROM products WHERE name LIKE ?", (f"%{q}%",))
```

과제: 입력이 데이터에서 SQL 문법으로 바뀌는 위치를 표시합니다. 정상 검색, 따옴표 포함 입력, SQLi 입력을 테스트합니다. 바인딩 후에도 `%`와 `_`는 LIKE 패턴으로 동작합니다. 이를 문자 그대로 검색하려면 별도 이스케이프 정책이 필요하며 SQLi와 구분합니다.

## 실습 3: XSS

브라우저 콘솔에서 다음을 실행하면 고정된 무해한 스크립트를 담은 페이지로 이동합니다.

```javascript
location.href = '/vuln/greet?name=' + encodeURIComponent("<script>document.title='LAB_XSS'</script>");
```

취약 페이지에서는 탭 제목이 `LAB_XSS`로 바뀝니다. 이후 아래 방어 페이지와 비교합니다.

```javascript
location.href = '/safe/greet?name=' + encodeURIComponent("<script>document.title='LAB_XSS'</script>");
```

방어 페이지에서는 스크립트가 텍스트로 보입니다. 응답 소스의 `&lt;script&gt;`를 확인합니다.

- 취약 버전: 사용자 입력을 HTML 문자열에 연결합니다.
- 방어 버전: 고정 Jinja 템플릿의 HTML 텍스트 문맥에서 입력을 자동 이스케이프합니다.
- 서버가 템플릿 소스 자체를 사용자 입력으로 구성하는 SSTI와 구분합니다.
- 이 방어를 JavaScript·CSS·URL·HTML 속성 문맥에 그대로 일반화하지 않습니다.
- HttpOnly는 JavaScript의 쿠키 읽기를 제한하지만 XSS로 실행되는 인증 요청까지 막지 않습니다.
- CSP는 보조 방어이며 출력 문맥을 올바르게 처리해야 합니다.

자동 테스트는 HTML 구조와 이스케이프를 검사합니다. 브라우저에서 코드가 실제 실행됐는지는 위 절차로 별도 확인하고 보고서에 구분해 기록합니다. 저장형·DOM XSS는 [PortSwigger XSS 자료](https://portswigger.net/web-security/cross-site-scripting)로 확장합니다.

## 실습 4: CSRF와 세션

다른 터미널에서 실행합니다.

```bash
python examples/csrf_server.py
```

1. <http://127.0.0.1:5000>에서 Alice로 로그인합니다.
2. <http://127.0.0.1:8001>을 엽니다.
3. 취약 경로 전송 버튼을 누릅니다. 토큰 없이 200이 반환됩니다.
4. 앱 홈을 다시 열어 표시 이름이 `CSRF changed`로 변했는지 확인합니다.
5. 데모 페이지로 돌아가 방어 경로 전송 버튼을 누릅니다. 403이 반환됩니다.

**두 주소는 포트가 달라 cross-origin이지만 same-site입니다.** 같은 호스트와 스킴을 사용하므로 SameSite=Lax 쿠키가 폼 POST에 포함될 수 있습니다. 이 예제는 SameSite를 무력화하는 일반적인 cross-site 공격이라고 주장하지 않습니다. `localhost`와 `127.0.0.1`을 섞지 마세요.

CORS는 응답 읽기 권한을 제한하지만 단순 HTML 폼 전송 자체를 일반적으로 차단하지 않습니다. Network에서 요청의 쿠키 전송과 응답 상태를 직접 관찰합니다. Flask 테스트 클라이언트는 브라우저의 SameSite 정책을 구현하는 검증 도구가 아닙니다.

정상 토큰이 있는 변경은 앱 홈의 콘솔에서 실행할 수 있습니다.

```javascript
await fetch('/safe/status', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: new URLSearchParams({
    display_name: 'Alice normal',
    csrf: (await (await fetch('/session')).json()).csrf
  })
});
```

과제: 토큰 누락·오류·다른 세션의 토큰·정상 토큰을 비교합니다. 로그인 후 토큰이 바뀌고 로그아웃 후 기존 세션이 거부되는 테스트를 읽습니다. 서버 재시작 시 모든 세션과 계정 변경이 초기화됩니다.

## 실습 5: 명령어·파일·업로드

```bash
python examples/boundaries.py
python -m unittest tests.test_boundaries -v
```

### 명령어 인젝션

고정 입력 `hello; printf LAB_MARKER`를 사용합니다.

- `shell=True` 문자열: 셸이 `;`를 해석하여 `helloLAB_MARKER` 출력.
- `shell=False` 인자 목록: 입력을 하나의 인자로 전달하여 `hello; printf LAB_MARKER` 출력.

이 예제는 고정된 입력만 로컬에서 실행합니다. 실제 기능에서는 가능한 한 subprocess 대신 라이브러리 API를 사용합니다. 인자 목록을 쓰더라도 대상 프로그램의 옵션 주입 가능성은 별도로 분석해야 합니다.

### 경로 순회

임시 디렉터리 아래 `public/readme.txt`와 가짜 `secret.txt`를 생성합니다. 취약 버전에서 `../secret.txt`를 읽고, 방어 버전에서 공개 디렉터리 이탈을 차단합니다. 두 버전 모두 실습 fixture 바깥은 읽지 못하도록 별도 울타리를 둡니다.

`resolve()`로 정규화한 뒤 디렉터리 포함 여부를 검사합니다. 문자열 접두사 비교와의 차이를 설명하세요. 이 작은 예제는 심볼릭 링크를 고정된 상태에서 검사하며, 공격자가 동시에 디렉터리를 바꾸는 TOCTOU 경쟁까지 해결하는 운영용 파일 API는 아닙니다.

### 텍스트 업로드 저장

방어 저장 함수 `save_text_upload()`는 클라이언트 파일명의 경로를 저장 위치로 사용하지 않고 서버가 이름을 생성합니다. `.txt`, 1 KiB 이하, UTF-8 디코딩을 확인합니다. 원본 이름 `../../memo.txt`가 최종 저장 경로에 반영되지 않는지 테스트합니다.

확장 과제: 웹 업로드를 추가한다면 저장 위치를 정적 실행 경로와 분리하고, 다운로드 시 `text/plain`·첨부 응답을 사용합니다. UTF-8 텍스트에도 HTML이 들어갈 수 있으므로 인코딩 검사를 XSS 방어로 해석하지 않습니다. 이 저장소에는 웹 업로드·다운로드 라우트가 없습니다.

## 실습 6: SSRF와 API 속성별 인가

### SSRF 모델

`examples/boundaries.py`의 `fetch_fixture()`는 URL을 키로 하는 사전에서 데이터를 반환합니다. 실제 DNS 조회·네트워크 요청은 없습니다.

| 요청 목적지 | 취약 버전 | 방어 버전 |
|---|---|---|
| `https://catalog.lab/items` | 공개 목록 | 공개 목록 |
| `http://internal.lab/config` | 가짜 내부 비밀 | 거부 |

핵심 질문: 사용자가 서버의 네트워크 접근 권한을 이용해 목적지를 임의 선택할 수 있는가? 가능한 경우 사용자가 URL을 직접 주는 대신 서버가 관리하는 목적지 ID를 선택하게 설계합니다.

이 모델의 고정 문자열 허용 목록을 범용 HTTP fetcher의 완성된 방어라고 간주하지 않습니다. 실제 구현은 스킴, 호스트, 포트, DNS 해석 결과, 리다이렉트의 각 홉, IPv4/IPv6, 연결 시점 검증, 네트워크 egress 정책을 검토해야 합니다. 실네트워크 재현은 [PortSwigger SSRF 교육 환경](https://portswigger.net/web-security/ssrf)을 활용합니다.

### API mass assignment

앱을 재시작하고 Alice로 로그인한 뒤 앱 홈의 개발자 도구 콘솔에서 실행합니다.

```javascript
await fetch('/safe/profile', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': (await (await fetch('/session')).json()).csrf
  },
  body: JSON.stringify({is_admin: 1})
});
```

방어 경로는 400을 반환하고 `/admin`은 403입니다. 같은 요청의 경로를 `/vuln/profile`로 바꾸면 변경이 성공하여 `/admin`이 200을 반환합니다.

정상 변경은 `/safe/profile`에 `{"display_name":"Alicia"}`를 보내면 됩니다. `is_admin`은 일반 사용자가 수정할 수 없는 속성입니다. 입력 타입·속성 목록 검증과 속성별 권한 정책을 함께 생각합니다. 두 경로 모두 CSRF 토큰을 검사하므로 CSRF 방어와 인가 방어가 독립적임을 확인할 수 있습니다.

## 실습 7: 코드 리뷰와 탐지

검토 지점을 찾습니다. 검색 결과는 취약점 확정 판정이 아닙니다.

```bash
rg -n 'shell=True|execute\(|render_template_string|SECRET_KEY|SESSION_COOKIE|password|is_admin' app.py examples
python -m pip check
```

`uv venv`로 만든 환경에 pip가 없다면 마지막 명령 대신 다음을 사용합니다.

```bash
UV_CACHE_DIR=/tmp/secure-coding-uv-cache uv pip check --python .venv/bin/python
```

확인할 항목:

- `PASSWORDS`의 값은 평문인가, 전용 비밀번호 해시인가? 학습용 공개 비밀번호와 운영용 비밀정보를 구분했는가?
- 요청자가 보낸 사용자 ID·역할·파일명·목적지 URL을 어디서 신뢰하는가?
- `SECRET_KEY`가 시작 시 생성되는 것의 이점과 세션 유지·다중 프로세스 한계는 무엇인가?
- HTTP loopback 실습의 쿠키 설정을 HTTPS 운영 서비스로 옮길 때 무엇이 바뀌어야 하는가?
- 의도적 취약 버전이 배포 산출물에 포함되지 않게 하려면 어떻게 분리할 것인가?

의존성 취약점 검사는 선택적으로 수행합니다. 별도 도구 설치와 네트워크 접근이 필요합니다.

```bash
uvx pip-audit -r requirements.txt
```

`pip check`는 의존성 호환성을 확인하며 알려진 취약점 검사와 다릅니다. 감사 도구 결과에는 실행 날짜·해석된 패키지 버전·취약점 DB를 기록합니다. 결과가 없더라도 앱 전체가 안전하다는 의미는 아닙니다.

로그 실습:

1. `/safe/notes/2`를 Alice로 요청하고 `object_access_denied`를 확인합니다.
2. 토큰 없이 `/safe/status`에 POST하고 `csrf_denied`를 확인합니다.
3. 로그에 비밀번호·세션 쿠키·토큰이 없는지 확인합니다.
4. 정상 동작, 단순 입력 실수, 반복 공격을 로그만으로 얼마나 구분할 수 있는지 적습니다.

기본 이벤트 로그는 공격 전체를 자동 탐지하지 않습니다. 상태 코드·사용자·빈도·시간 등 필요한 관찰 항목과 개인정보 최소화를 함께 설계합니다.
