# 검증 기록

검증일: 2026-11-13. Python 3.13.7, Flask 3.1.3, Werkzeug 3.1.9 환경에서 수행했습니다. Python 3.10~3.12는 별도로 실행하지 않았습니다.

```bash
python -m unittest discover -s tests -v
```

결과: **29개 테스트 통과**.

- 웹: 로그인·세션 회전·로그아웃 무효화, IDOR, SQLi, XSS HTML 이스케이프, CSRF, API 속성별 인가, 정상 입력, 로그, 요청 크기 제한.
- 경계 예제: 실제 고정 subprocess 명령, 임시 디렉터리 경로·심볼릭 링크, 텍스트 업로드, 가상 SSRF.
- TCP: 실제 loopback에서 빈 입력, ASCII, UTF-8, 20 KiB 바이너리 왕복 및 초과 입력 제한.
- HTTP: 실제 loopback에서 쿠키 로그인과 다섯 취약/방어 경로 비교, CSRF 데모 페이지 제공.

첫 실행은 샌드박스의 소켓 생성 제한 때문에 TCP 테스트가 실패했습니다. 소켓을 사용할 수 있는 실행 환경에서 전체 테스트를 다시 실행해 통과했습니다. 테스트 실패를 건너뛰거나 성공으로 취급하지 않았습니다.

추가 확인:

- `python examples/boundaries.py` 실행 결과 확인.
- Markdown 로컬 링크·코드 펜스 검사.
- 의존성 호환성 검사.

검증하지 않은 내용:

- 실제 브라우저의 JavaScript 실행과 SameSite 쿠키 정책. 수동 절차는 [실습 안내](labs.md)에 있습니다.
- 실제 외부 네트워크 SSRF, DNS·리다이렉트 우회. 제공 예제는 가상 서비스 모델입니다.
- 선택 과제인 의존성 취약점 감사, Bandit·PortSwigger 문제 풀이, 운영 배포 보안성.
