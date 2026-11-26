# 4주차 개발자 도구와 Burp

[이전 3주차](week-03.md) · [웹 보안 커리큘럼](curriculum.md) · [다음 5주차](week-05.md)

개발자 도구는 해당 브라우저의 요청을 보여 줍니다. Burp Proxy는 브라우저와 서버 사이에서 요청과 응답을 기록하고, Repeater는 선택한 요청을 별도로 다시 보냅니다.

1. WSL에서 `python app.py`를 실행합니다. Burp에서 **Proxy → Intercept → Open browser**를 누르고, `Intercept is off` 상태에서 내장 브라우저로 `http://127.0.0.1:5000/`에 접속합니다. [Burp 내장 브라우저](https://portswigger.net/burp/documentation/desktop/tools/burps-browser)
2. **Proxy → HTTP history**에서 `GET /`를 선택합니다. **Request**에서 메서드와 경로, **Response**에서 `200 OK`와 HTML을 봅니다. Intercept가 꺼져 있어도 요청은 기록됩니다. [Burp HTTP history](https://portswigger.net/burp/documentation/desktop/tools/proxy/http-history)
3. 같은 행을 우클릭해 **Send to Repeater**를 선택하고, **Repeater → Send**를 눌러 정상 요청을 한 번 더 보냅니다. 상태 코드와 페이지 제목을 처음 기록과 대조합니다. [Burp Repeater 요청 재전송](https://portswigger.net/burp/documentation/desktop/getting-started/reissuing-http-requests)
4. Burp 내장 브라우저에서 3주차의 로그인과 본인 메모 조회도 진행합니다. URL의 메모 ID, 요청의 세션 쿠키, 서버가 조회에 사용한 사용자 ID의 출처를 표로 정리하세요.

기본 연결은 `브라우저 → Burp Proxy(8080) → Flask 앱(5000)`입니다. 브라우저 주소창에는 앱의 `5000`번 포트가 들어갑니다. [Burp 프록시 설정](https://portswigger.net/burp/documentation/desktop/settings/tools/proxy)

**확인 문제.** 왜 `/safe/notes/1`을 분석할 때 `200`이라는 숫자와 함께 요청한 계정, 응답의 메모 ID도 적어야 하나요?

**제출물.** 메서드·경로·입력·인증·인가를 열로 둔 표와 정상 요청의 Repeater 결과를 준비하세요. 쿠키, 비밀번호, 토큰은 가립니다.
