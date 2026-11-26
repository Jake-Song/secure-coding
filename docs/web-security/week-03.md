# 3주차 웹 앱 구조

[이전 2주차](week-02.md) · [12주 커리큘럼](curriculum.md) · [다음 4주차](week-04.md)

라우팅은 HTTP 메서드와 경로에 맞는 Python 함수를 고르는 일입니다. 함수는 쿠키와 폼, URL에서 필요한 데이터를 읽고 SQLite를 조회한 뒤 HTML이나 JSON을 돌려줍니다. 브라우저는 HTML을 화면으로 표시하고 JavaScript가 있는 페이지에서는 이벤트 처리와 화면 갱신도 수행합니다.

1. 개발자 도구의 **Network** 탭에서 로그 보존을 켜고 첫 화면에서 Alice로 로그인하세요. `POST /login`의 폼 필드, `302` 응답의 `Location`, 이어지는 `GET /`를 찾습니다.
2. 주소창에서 `/safe/notes/1`을 열고 JSON 응답의 `id`, `owner_id`, `body`를 확인하세요.
3. [app.py](../../app.py)에서 `create_app` → `login` → `current_user` → `safe_note` 순서로 읽으세요. 로그인 성공 시 쿠키의 `sid`가 서버의 `active_sessions`에 저장된 사용자 ID와 연결됩니다. 메모 조회에서는 그 사용자 ID와 URL의 메모 ID를 함께 검사합니다.
4. 복습 과제로 읽기 전용 `GET /about`을 추가하세요. `render_template_string`의 템플릿에 `{{ title }}`을 쓰고 `title` 값으로 `메모 & 검색 <연습>`을 전달하세요. 화면에 문자가 그대로 보이는지, 응답 HTML에는 `&amp;`와 `&lt;`가 들어 있는지 확인합니다.

Flask의 서명 쿠키는 값의 변조 여부를 확인합니다. 이 앱은 세션 식별자의 유효성도 서버의 `active_sessions`에서 확인하고, 로그아웃 때 그 항목을 지웁니다. 로컬 TCP와 HTTP를 복습하려면 [기초 실습 3주차](../foundations.md#3주차-웹-애플리케이션)를 함께 보세요.

**확인 문제.** `/safe/notes/1`의 `1`과 SQL 조건에 들어가는 사용자 ID는 각각 어디에서 오나요?

**제출물.** 로그인과 메모 조회의 요청·응답 흐름, `/about`의 응답 HTML과 화면을 기록하세요.
