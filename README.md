# 보안 취약점 분석과 방어 실습

입문자를 위한 **주 6~8시간, 12주** 커리큘럼입니다. Linux·네트워크 기초부터 시작해 웹·API 취약점을 재현하고, 소스 코드에서 원인을 찾아 수정·재검증합니다.

- [12주 커리큘럼](docs/curriculum.md): 주차별 목표, 실습, 제출물, 완료 기준
- [Bandit 시작하기](docs/bandit.md): 첫 SSH 접속, 단계 진행, 기본 명령, 오류 해결
- [Linux·네트워크 기초 실습](docs/foundations.md): 1~4주차 실행 안내
- [취약점별 실습 안내](docs/labs.md): 5~11주차 요청과 예상 결과
- [최종 프로젝트·보고서 양식](docs/report-template.md): 12주차 제출물
- [C 언어 입문 튜토리얼](docs/c-tutorial.md): 컴파일부터 배열·포인터·메모리·입력 검증·파일 저장까지, 실행 예제 8개
- [C++ 입문 튜토리얼](docs/cpp-tutorial.md): 참조·문자열·vector·클래스·알고리즘·RAII·입력 검증, 실행 예제 8개
- [Rust 입문 튜토리얼](docs/rust-tutorial.md): 소유권·빌림·구조체·enum·컬렉션·Result·파일 저장, 실행 예제 8개
- [역엔지니어링 12주 커리큘럼](docs/reverse-engineering.md): C·메모리부터 ELF 분석, GDB·Ghidra, 파일 형식 복원과 패치까지
- [네트워크 보안 12주 커리큘럼](docs/network-security.md): TCP·DNS·TLS·메시지 인증·접근 정책·로그 탐지
- [네트워크 보안 실습 코드와 실행 안내](docs/network-labs.md): 로컬 통신과 오프라인 모델로 구성한 여섯 실습

## 첫 학습: Bandit

먼저 [Bandit 시작하기](docs/bandit.md)를 따라 `bandit0`에 접속하고 `bandit1`로 넘어갑니다. 이 단계에는 Python 설치나 웹 앱 실행이 필요 없습니다.

```bash
ssh -p 2220 bandit0@bandit.labs.overthewire.org
```

최초 비밀번호는 `bandit0`입니다. 입력 중 글자가 보이지 않는 것이 정상입니다. 접속 정보는 [공식 Level 0 안내](https://overthewire.org/wargames/bandit/bandit0.html)를 기준으로 합니다.

## 웹 실습 앱 실행

Python 3.10 이상과 Linux/macOS 터미널을 기준으로 작성했습니다. Windows에서는 WSL을 사용할 수 있습니다. TCP·명령어 예제는 Linux/macOS를 대상으로 합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

브라우저에서 <http://127.0.0.1:5000>에 접속합니다.

| 사용자 | 비밀번호 | 소유 메모 |
|---|---|---|
| alice | alice-lab | 1 |
| bob | bob-lab | 2 |

가상환경 생성 시 `ensurepip` 오류가 나고 `uv`가 설치되어 있다면 다음 방법을 사용할 수 있습니다.

```bash
UV_CACHE_DIR=/tmp/secure-coding-uv-cache uv venv .venv
UV_CACHE_DIR=/tmp/secure-coding-uv-cache uv pip install --python .venv/bin/python -r requirements.txt
source .venv/bin/activate
python app.py
```

`/vuln/`은 의도적으로 취약한 구현, `/safe/`는 해당 취약점에 대한 방어 구현입니다. 앱은 loopback에만 바인딩합니다. 본인 소유 로컬 환경이나 명시적으로 허용된 교육 환경에서 실습하며, 공개 서버에 배포하지 않습니다.

## 예제 실행

아래 명령은 모두 저장소 루트에서 실행합니다. 가상환경을 활성화한 별도 터미널에서:

```bash
# 앱 실행 중: 실제 HTTP 요청으로 다섯 취약/방어 경로 비교
python examples/http_demo.py

# 앱 없이 실행 가능: 고정 명령어, 임시 파일, 가상 SSRF 비교
python examples/boundaries.py

# 브라우저 CSRF 실습용 별도 origin
python examples/csrf_server.py
```

`http_demo.py`는 Alice의 표시 이름과 관리자 상태를 변경합니다. 앱을 `Ctrl+C`로 종료한 뒤 다시 실행하면 초기화됩니다. SQLite DB, 사용자 상태, 세션은 모두 메모리에만 있습니다.

TCP 실습은 두 터미널에서 진행합니다.

```bash
# 터미널 A: 한 연결을 처리하고 종료
python examples/tcp_server.py
```

```bash
# 터미널 B
python examples/tcp_client.py '안녕하세요'
```

## 네트워크 보안 실습

저장소 루트에서 실행합니다. Python 표준 라이브러리를 사용하며 TLS 예제에는 설치된 OpenSSL CLI가 필요합니다. 웹 앱 실행이나 추가 Python 패키지 설치는 필요하지 않습니다.

```bash
python3 -m examples.network_security all
```

`framing`, `dns`, `pcap`, `tls`, `auth`, `policy`, `detection`을 개별 명령으로도 실행할 수 있습니다. 실제 TCP·UDP·TLS는 `127.0.0.1`의 임시 포트에서 통신합니다. PCAP과 로그는 합성 데이터이며 접근 정책은 오프라인 모델입니다. 상세한 예상 결과와 수정 과제는 [실습 안내](docs/network-labs.md)에 있습니다.

```bash
python3 -m unittest tests.test_network_protocols tests.test_network_auth tests.test_network_tls tests.test_network_policy -v
```

## 테스트

```bash
python -m unittest discover -s tests -v
```

테스트는 취약한 동작이 재현되는지, 방어 구현이 공격을 차단하는지, 정상 기능이 유지되는지를 함께 확인합니다. TCP 테스트는 실제 loopback 소켓을 사용합니다. 네트워크가 제한된 환경에서는 웹·경계 예제만 먼저 검사할 수 있습니다.

네트워크 보안 실습 추가 후 전체 **65개 테스트**가 통과했습니다. 초기 웹·경계·TCP·HTTP 예제는 29개, 신규 네트워크 보안은 36개입니다. 실행 환경과 확인 범위는 [검증 기록](docs/validation.md)에 있습니다.

```bash
python -m unittest tests.test_app tests.test_boundaries -v
```

`/vuln/` 코드를 직접 수정하면 취약 동작을 기대하는 테스트가 실패하는 것이 자연스럽습니다. 해당 테스트를 수정 후 회귀 테스트로 바꾸되, 원래 재현 절차는 보고서에 보존합니다.

## 구현 범위

| 내용 | 제공하는 예제 | 검증 범위 |
|---|---|---|
| 로그인·인가·SQLi·반사형 XSS·CSRF·속성별 인가 | 실행 가능한 Flask 앱 | 테스트 클라이언트 및 HTTP 비교 스크립트 |
| XSS 실행·브라우저 쿠키 전송 | 브라우저 수동 실습 절차 | 자동 테스트는 HTML 이스케이프와 서버 응답을 검사하며 브라우저 실행은 검사하지 않음 |
| 명령어 인젝션 | 고정된 무해한 입력을 셸/인자 목록에 전달 | 로컬 subprocess 비교 |
| 경로 순회·텍스트 업로드 | 임시 디렉터리에서 읽기·저장 | 경로 이탈·심볼릭 링크·크기·인코딩 검사 |
| SSRF | 외부 접속 없는 가상 서비스 모델 | 목적지 선택과 고정 허용 목록만 검사 |
| 저장형·DOM XSS, 실제 네트워크 SSRF, 운영 배포 | 확장 과제와 참고 자료 | 이 저장소에서 구현·검증하지 않음 |

이 앱의 `/safe/`는 각 실습의 방어 원리를 설명합니다. 운영용 전체 보안 구현은 아닙니다. 예를 들어 HTTP 실습을 위해 Secure 쿠키를 끄고 XSS 관찰을 위해 전역 CSP를 생략했습니다. 단일 프로세스·단일 스레드로 실행하며, DB와 세션 정리도 교육용으로 단순화했습니다.

## 코드 위치

```text
app.py                       웹 실습 앱
examples/tcp_server.py        TCP 에코 서버
examples/tcp_client.py        EOF까지 수신하는 클라이언트
examples/http_demo.py         실제 HTTP 비교
examples/csrf_server.py       다른 origin의 CSRF 폼
examples/boundaries.py        명령어·파일·업로드·가상 SSRF
examples/c_tutorial/          C 입문 예제 8개와 Makefile
examples/cpp_tutorial/        C++17 입문 예제 8개와 Makefile
examples/rust_tutorial/       Rust 입문 예제 8개와 Cargo 프로젝트
examples/network_security/   TCP·DNS·PCAP·TLS·HMAC·정책·탐지 실습
tests/                       공격 재현·방어·정상 동작 테스트
docs/                        커리큘럼·실습·보고서
```
