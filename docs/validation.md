# 검증 기록

## 2026-11-18 역엔지니어링 5~8주차 학습자료 추가, 1~4주차 보강

Linux x86-64(WSL2)에서 GCC 13.3.0, GNU Binutils 2.42, GDB 15.1, Python 3.12.3으로 검증했습니다. 이 환경에는 GDB가 설치돼 있지 않아 Ubuntu 24.04의 `gdb` 패키지와 의존 라이브러리를 시스템 설치 없이 임시 디렉터리에 풀어 실행했습니다. 새 C17 예제 3개(`05_lookup`, `07_validate`, `08_transform`)와 strip 사본 2개를 추가했습니다.

```bash
make -C examples/reverse_engineering clean
make -C examples/reverse_engineering
python3 -m unittest tests.test_reverse_engineering -v
```

결과: **역엔지니어링 테스트 12개 통과**(기존 8개 + 신규 4개), skip 없음. 테스트는 경고를 오류로 처리해 다시 빌드합니다.

- 5주차: 디버그·strip 빌드의 다섯 이름·빈 문자열·대소문자 입력과 사용법 오류의 출력·종료 코드 일치, strip 파일의 로컬 심볼 부재, `.data.rel.ro` 16바이트 레코드 4개의 `R_X86_64_RELATIVE` Addend가 `.rodata`의 이름 문자열을 가리키고 level·flags가 파일 바이트와 일치.
- 7주차: 하네스로 링크한 `check_key`의 길이·문자 범위·앞부분·가중 합 단계별 반환값 14개 입력, 문서의 생성기 방식으로 계산한 수락 키 1,689개 중 표본을 디버그·strip 빌드가 모두 수락.
- 8주차: 기준 재구현이 비교 도구에서 `21/21 matched`, 내림 나눗셈·부호 해석 누락 재구현은 `DIFF`와 종료 코드 1, NUL 포함 4바이트·빈 입력의 정확한 출력, 64바이트 수락·65바이트 거부.

GDB 배치 실행으로 문서의 절차를 확인했습니다.

- 6주차: `find_account` 반환값(`nobody` 0, `analyst` 원소 1), `is_allowed` 첫 명령의 `rdi`·`esi`와 세 입력의 반환값, 워치포인트 변화 횟수(`guest` 1, `root`·`nobody` 4), strip 파일의 `info proc mappings` 로드 베이스 + 정적 주소 중단점, NULL 역참조 오류 메시지.
- 7주차: 단계별 `$eax`(1·2·3·4·0), `wrongkey`의 레지스터 변경 후 `accepted` 출력. 문서의 생성기와 하네스 코드를 상수만 채워 그대로 실행.
- 8주차: `dprintf` 반복 추적 4줄이 문서의 기대 출력과 일치.
- 1~4주차 보강: 2·3·4주차 GDB 블록을 문서 그대로 재실행해 기대값을 확인했습니다. 3주차에 `cmp` 직후 `eflags 0x286`과 `jg`/`ja` 결과, 2주차에 `char *` 주소 표시, 4주차에 첫 명령의 인자 표시 설명을 추가했고 1주차에 환경 준비·보고서 양식·문제 해결 절을 추가했습니다.

문서의 로컬 링크·앵커·코드 펜스와 공백 오류를 검사했습니다. **Ghidra 조작(5주차 GUI 절차)은 이 환경에 Ghidra가 없어 실행하지 않았습니다.** 같은 근거는 `objdump`·`readelf` 절차와 자동 테스트로 확인했습니다. 수정 과제 전체, `-O2` 비교, 기존 웹·네트워크 테스트 전체 재실행은 이번 범위에 포함하지 않았습니다.

## 2026-11-15 역엔지니어링 1~4주차 학습자료 추가

Linux x86-64에서 GCC 13.3.0, GNU Binutils 2.42, GDB 15.1, Python 3.12.3으로 검증했습니다. C17 소스 5개와 어셈블리 소스 1개로 실행 파일 6종(PIE 5종, non-PIE 비교본 1종)을 빌드했습니다. 1주차의 전처리·어셈블리·오브젝트 산출물도 생성했습니다.

```bash
make -C examples/reverse_engineering
python3 -m unittest tests.test_reverse_engineering -v
```

결과: **신규 자동 테스트 8개 통과**, skip 없음. 테스트는 임시 디렉터리에서 경고를 오류로 처리해 다시 빌드했습니다.

- 문자열 수락, 내용·대소문자·길이 0·4·5·6·4096·비 ASCII 입력 거부, 사용법 오류와 판정 실패의 종료 코드 구분.
- 빌드 중간 산출물 생성, `.o`의 `REL` 타입, `.o` 직접 링크 후 동일 동작.
- 배열·포인터 크기, 구조체 필드 오프셋, 동적 배열 값, 비트 연산·부분 레지스터 예제 출력.
- signed/unsigned 비교의 -1·9·10·11 경계, 루프 입력 0·1·4·5, 비트 변환 입력 0·`0x23`·`0xff`.
- PIE/non-PIE의 `DYN`/`EXEC` 타입과 동일 출력, `.bss`의 `NOBITS`, `message` 심볼의 정적 주소에서 `PT_LOAD`를 통해 계산한 실제 파일 바이트.

GDB 동적 검증은 별도로 배치 실행했습니다. 처음에는 샌드박스의 `ptrace` 제한으로 실패했으며, 제한 밖에서 직접 만든 실습 실행 파일만 대상으로 다시 실행해 확인했습니다.

- 2주차: `0x12345678`의 `78 56 34 12` 바이트 순서, 구조체, 동적 배열, 호출자 배열과 매개변수 포인터의 크기 차이.
- 3주차: `rax`·`eax`·`al` 쓰기 직후 값, `lea`의 주소 차이 4, 메모리 읽기 값, signed/unsigned 함수의 반환값.
- 4주차: 첫 명령에서 인자 1~6의 레지스터와 일곱 번째 스택 인자 7, 진입 스택 정렬, 반환 주소와 복귀 PC 일치, `rsp` 변화, 반환값 28·35.
- PIE/non-PIE에서 초기 `.bss` 값 0, 문자열, 메모리 매핑을 확인했습니다. 각각 두 번의 새 실행에서 PIE의 주소 변화와 non-PIE 주 실행 파일의 주소 유지를 관찰했고, `main`과 `message`로 계산한 로드 바이어스가 일치했습니다.

추가 문서의 로컬 링크·코드 펜스와 변경 파일의 공백 오류도 검사했습니다. 수정 과제 전체, GUI 분석기, ARM·Windows 네이티브 실행은 이번 검증 범위에 포함하지 않았습니다. 기존 웹·네트워크 테스트 전체를 다시 실행한 기록은 아닙니다.

## 2026-11-15 C++·Rust 입문 튜토리얼 추가

Linux x86-64에서 C++ 예제 8개와 Rust 예제 8개를 빌드했습니다. C++ 컴파일러는 GCC 13.3.0, Rust 도구는 rustc·Cargo 1.91.1입니다. C++는 C++17, Rust는 2021 edition이며 외부 패키지를 추가하지 않았습니다.

이 환경의 Rust 도구 디렉터리는 PATH에 포함되지 않아, 설치된 컴파일러 경로를 명시했습니다. 일반적인 PATH 설치 환경에서는 `RUSTC` 지정 없이 `cargo`·`rustc`를 사용할 수 있습니다.

```bash
make -C examples/cpp_tutorial
RUSTC=/home/jake/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc \
  /home/jake/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo \
  build --offline --manifest-path examples/rust_tutorial/Cargo.toml
RUSTC=/home/jake/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc \
  python3 -m unittest tests.test_cpp_rust_tutorials -v
```

결과: **신규 테스트 20개 통과**, skip 없음. C++ 9개와 Rust 11개입니다. 테스트에서는 경고를 오류로 처리하여 다시 컴파일했습니다.

- 두 언어의 고정 예제 출력, 숫자 0·100, 선행 0, 잘못된 형식·큰 정수·널 문자·비 ASCII 숫자 거부.
- 한 줄 입력의 62·63바이트 경계, 줄바꿈 없는 짧은 숫자와 빈 EOF 구분.
- 점수 1개·100개·101개, 오류 입력 후 파일 미생성, 기존 파일 보존, 없는 출력 디렉터리 처리.
- Rust의 CRLF 입력, 이동한 값의 재사용과 충돌하는 빌림에 대한 컴파일 오류.

문서의 로컬 링크와 코드 블록 구분도 검사했습니다. Windows·macOS 실행과 최종 확장 과제, C++ Sanitizer 실행은 이번 추가에서 검증하지 않았습니다. 기존 웹·네트워크 테스트 전체를 다시 실행한 결과는 아닙니다.

## 2026-11-14 네트워크 보안 실습 추가

전체 검증 환경: Linux x86-64, Python 3.13.7, Python SSL의 OpenSSL 3.5.3, 인증서 생성 CLI의 OpenSSL 3.0.13, Flask 3.1.3, Werkzeug 3.1.9.

```bash
.venv/bin/python -m unittest discover -s tests -v
```

결과: **전체 65개 테스트 통과**, skip 없음. 기존 29개에 네트워크 보안 36개를 추가했습니다.

- 실제 TCP: 빈·UTF-8·바이너리·4096바이트·다중 프레임 왕복, 분할 쓰기, 잘린 본문 거부.
- 실제 UDP: 로컬 단일 A 질의 성공과 NXDOMAIN 응답.
- 실제 TLS: 임시 CA와 서버 인증서 생성, 신뢰 CA+정상 호스트명 성공, 미신뢰 CA·호스트명 불일치 거부, TLS 1.2 및 빈·바이너리 프레임 왕복.
- HMAC: 실제 TCP 요청에서 정상·재전송·변조·타인 메모·만료 거부, 고정 시계로 미래 시각 경계·nonce 보존 기간·동시 재전송·저장 상한 검사.
- 오프라인: 부분 읽기·프레임 상한·JSON 오류, DNS 불일치·잘림·순환 포인터·길이 제한, PCAP 헤더·IP/UDP 체크섬·DNS 내용·기존 파일 보호, 정책 기본 거부, 탐지 시간 창·집계 키·중복 억제·로그 한도.

별도로 시스템 Python 3.12.3에서 `python3 -m examples.network_security all`을 실행해 모든 데모의 출력과 정상 종료를 확인했습니다. 시스템 Python으로 소켓이 필요 없는 신규 테스트 27개도 통과했습니다. Python 3.10~3.11의 실행은 확인하지 않았습니다.

샌드박스 안에서는 소켓 생성이 `PermissionError`로 차단됐습니다. 실제 통신 데모와 전체 테스트는 loopback 소켓이 허용된 실행 환경에서 다시 실행했습니다. 소켓 제한을 테스트 성공으로 취급하지 않았습니다.

확인하지 않은 내용: Wireshark GUI에서 PCAP 열기, 실제 인터페이스 패킷 캡처, OS 방화벽·라우팅·네임스페이스 변경, 외부 DNS·DNSSEC, mTLS, 분산·재시작 후 nonce 보존, 운영 IDS·부하 방어, 최종 프로젝트 통합 서비스. PCAP·정책·로그는 각각 합성 데이터 또는 오프라인 모델입니다.

## 2026-11-13 초기 웹 보안 실습

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
