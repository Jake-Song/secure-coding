# 1~4주차 기초 실습

명령은 Linux 기준입니다. `strace`, `ss`, `getent` 등은 OS에 따라 없을 수 있습니다. 해당 도구가 없으면 같은 정보를 제공하는 도구를 사용합니다. 아래 파일 조작은 `mktemp`로 만든 임시 디렉터리에서 수행합니다.

## 1주차: Linux

먼저 [Bandit 시작하기](bandit.md)를 따라 SSH 접속과 첫 문제를 진행합니다. `bandit10` 진입까지 학습한 뒤 아래 로컬 실습으로 권한·프로세스·시스템 콜을 보완합니다. 아래 명령은 Bandit 서버가 아닌 **내 컴퓨터의 터미널**에서 실행합니다.

```bash
id
pwd
ps -o pid,ppid,user,stat,comm -p $$
lab_dir=$(mktemp -d)
printf 'public\n' > "$lab_dir/public.txt"
printf 'fake-secret\n' > "$lab_dir/private.txt"
chmod 644 "$lab_dir/public.txt"
chmod 600 "$lab_dir/private.txt"
ls -l "$lab_dir"
cat "$lab_dir/public.txt" | wc -c
```

관찰할 점:

1. `644`와 `600`을 소유자·그룹·기타 사용자 권한으로 풀어서 적습니다.
2. 본인은 두 파일을 모두 읽을 수 있습니다. 같은 계정으로 `cat`한 결과만으로 타 사용자 차단을 검증했다고 판단하지 않습니다.
3. 파일 읽기·디렉터리 탐색 권한의 차이를 조사합니다.
4. `strace cat "$lab_dir/public.txt"`로 `openat`, `read`, `write` 시스템 콜을 찾아 봅니다.

도구를 사용할 수 있다면 `rg`, `find`, `file`, `sort`, `uniq`, `strings`를 조사합니다. Bandit에서 사용한 명령과 비교하고, 비밀번호를 제외한 풀이 기록을 정리합니다.

제출물: 권한 해석 표, 프로세스·시스템 콜 관찰, Bandit 풀이 이유.

## 2주차: 네트워크

두 터미널에서 순서대로 실행합니다.

```bash
# 터미널 A: 저장소 루트
python examples/tcp_server.py
```

```bash
# 터미널 B
python examples/tcp_client.py '안녕하세요'
```

서버는 한 연결 후 종료합니다. 다시 실습하려면 서버를 재실행합니다.

확인할 점:

- 서버는 `127.0.0.1:9000`에 바인딩합니다. `ss -ltn`으로 대기 중인 소켓을 관찰합니다.
- TCP는 바이트 스트림이므로 `sendall()` 한 번과 `recv()` 한 번이 대응한다고 가정할 수 없습니다.
- 클라이언트의 `shutdown(SHUT_WR)`는 송신 종료를 알립니다. 서버가 EOF를 보고 연결을 닫으면 클라이언트도 수신 EOF를 확인합니다.
- 예제는 EOF를 메시지 종료로 사용합니다. 지속 연결이라면 길이 접두사·구분자 등 별도 프레이밍이 필요합니다.
- 예제 클라이언트는 작은 메시지용입니다. 큰 양방향 스트림에서는 송수신을 교차하거나 병행해야 하며 버퍼 크기에 의존하면 안 됩니다.
- TLS는 TCP 위에서 통신 기밀성과 무결성 등을 제공합니다. 취약한 서버 코드를 자동으로 수정하지는 않습니다.

공식 사이트 DNS 조회 예:

```bash
getent hosts overthewire.org
```

HTTP 관찰은 앱을 실행한 뒤 진행합니다.

```bash
curl --noproxy '*' -i http://127.0.0.1:5000/session
```

메서드, 경로, 상태 코드, `Content-Type`, `Set-Cookie`, 본문을 구분해 적습니다. 이 응답의 토큰과 쿠키는 실습 보고서 공개 시 가립니다.

제출물: DNS→연결→HTTP 요청·응답 그림, TCP 종료 과정, 관찰한 헤더.

## 3주차: 웹 애플리케이션

1. [웹 보안 과정의 공통 준비](web-security/curriculum.md#공통-준비)에 따라 Flask 앱을 실행합니다.
2. Alice로 로그인합니다. 개발자 도구 Network에서 `/login`의 POST와 리다이렉트를 관찰합니다.
3. `/safe/notes/1`에서 본인의 메모를 읽습니다.
4. [app.py](../app.py)의 `create_app`, `login`, `current_user`, `safe_note`를 따라갑니다.
5. 로그인은 사용자 확인, 메모 소유권 검사는 인가임을 코드에서 표시합니다.

추가 구현 과제: `create_app()` 안에서 `return app`보다 앞에 아래 라우트를 추가해 라우팅과 템플릿을 연습합니다.

```python
@app.get('/about')
def about():
    return render_template_string('<p>{{ message }}</p>', message='보안 실습 <시작>')
```

브라우저에 `<시작>`이 텍스트로 보이고 HTML 소스에서는 이스케이프되는지 확인합니다. SQL은 SQLite의 테이블 생성·조회·조건·조인을 별도로 연습합니다.

제출물: 로그인과 메모 조회의 데이터 흐름, 추가 라우트 코드, SQL 조회 예.

## 4주차: 도구와 신뢰 경계

브라우저 개발자 도구로 시작하고 Burp의 내장 브라우저와 Proxy/Repeater로 확장합니다. 프록시 대상은 로컬 실습 앱으로 한정합니다.

| 엔드포인트 | 입력 | 인증 | 인가 또는 주요 검사 |
|---|---|---|---|
| `/login` | 사용자명·비밀번호·CSRF 토큰 | 로그인 전 | 비밀번호·CSRF 검사 |
| `/safe/notes/<id>` | URL의 객체 ID | 필요 | 소유권 검사 |
| `/safe/search` | 검색어 | 불필요 | SQL 파라미터 바인딩 |
| `/safe/status` | 표시 이름·토큰 | 필요 | CSRF·길이 검사 |
| `/safe/profile` | JSON 속성·토큰 | 필요 | 허용 속성·타입·CSRF 검사 |

1. 정상 요청을 Repeater로 보내 같은 결과를 확인합니다.
2. 쿠키를 제거해 인증 경계를 확인합니다.
3. ID·검색어·JSON 필드를 하나씩 바꾸고 결과를 기록합니다.
4. HTTP 200만으로 취약하다고 판단하지 말고 실제 데이터 조회·변경 여부를 확인합니다.

제출물: 전체 엔드포인트 표, 신뢰 경계 그림, 재전송한 정상 요청 한 건.
