# Bandit 시작하기

첫 목표는 **SSH로 Bandit에 접속하고, 파일에서 다음 계정의 비밀번호를 찾아 `bandit10`까지 진행하는 것**입니다. 오늘은 `bandit0` 접속과 `bandit1` 진입부터 해봅니다.

Bandit은 초보자를 위한 Linux 명령줄 워게임입니다. 로컬 터미널에서 SSH로 교육 서버에 접속해 단계별 문제를 풉니다. Flask 앱, Python 가상환경, Docker 설치는 필요 없습니다. [공식 소개](https://overthewire.org/wargames/bandit/)

## 1. 준비

Linux·macOS에서는 터미널, Windows에서는 PowerShell 또는 WSL을 엽니다. 다음 명령으로 SSH 클라이언트를 확인합니다.

```bash
ssh -V
```

OpenSSH 등의 버전이 출력되면 준비된 상태입니다. `command not found`가 나오면 OS의 OpenSSH 클라이언트를 설치합니다. Ubuntu·Debian에서는 다음과 같습니다.

```bash
sudo apt update
sudo apt install openssh-client
```

이후 명령은 **내 컴퓨터에서 실행하는 명령**과 **SSH 접속 후 원격 서버에서 실행하는 명령**을 구분합니다. 로컬 저장소에 파일을 작성하려면 SSH에서 먼저 빠져나와야 합니다.

## 2. bandit0 접속

**내 컴퓨터의 터미널**에서 실행합니다.

```bash
ssh -p 2220 bandit0@bandit.labs.overthewire.org
```

| 항목 | 값 | 의미 |
|---|---|---|
| 명령 | `ssh` | 원격 컴퓨터의 셸에 암호화된 연결로 접속 |
| 포트 | `-p 2220` | Bandit SSH 포트 지정 |
| 사용자 | `bandit0` | 현재 단계의 계정 |
| 호스트 | `bandit.labs.overthewire.org` | 교육 서버 주소 |
| 최초 비밀번호 | `bandit0` | Level 0 공개 접속 비밀번호 |

주소·포트·최초 계정·비밀번호는 [공식 Level 0 안내](https://overthewire.org/wargames/bandit/bandit0.html) 기준입니다. 확인일: 2026-11-13.

처음 접속하면 서버 키를 신뢰할지 묻는 메시지가 나올 수 있습니다. 입력한 서버 주소를 확인하고, 표시된 키를 신뢰할 수 있는 경로로 확인한 뒤 `yes`를 입력해 등록합니다. 이미 저장된 서버 키와 다르다는 경고는 첫 접속 확인과 구분합니다.

이어서 비밀번호를 입력합니다. **입력 중 글자나 별표가 보이지 않는 것이 정상**입니다. `bandit0`를 입력하고 Enter를 누릅니다.

접속 후 다음 명령으로 현재 계정과 위치를 확인합니다.

```bash
whoami
pwd
ls -la
```

`whoami`가 `bandit0`를 출력하면 첫 접속에 성공한 것입니다. 셸 프롬프트 끝의 `$` 등은 화면 표시이므로 명령에 포함하지 않습니다.

## 3. 첫 문제: bandit0 → bandit1

[공식 문제](https://overthewire.org/wargames/bandit/bandit1.html)를 읽습니다. 현재 계정의 홈 디렉터리에 있는 `readme`에 다음 단계의 비밀번호가 있습니다.

**Bandit에 접속된 터미널**에서 실행합니다.

```bash
ls
cat readme
```

- `ls`: 현재 디렉터리의 파일 목록을 봅니다.
- `cat readme`: `readme`의 내용을 출력합니다.
- 출력된 문자열: **다음 계정인 `bandit1`의 비밀번호**입니다. 현재 계정의 비밀번호와 구분하세요.

찾은 비밀번호는 개인 비밀번호 관리 도구 등 저장소 밖의 비공개 위치에 보관합니다. 풀이 문서에는 명령과 이유를 기록합니다. 공식 안내에 따르면 단계 비밀번호가 바뀔 수 있으므로 재현 방법도 남겨야 합니다.

원격 접속을 종료합니다.

```bash
exit
```

**내 컴퓨터의 터미널로 돌아온 뒤** 다음 계정에 접속합니다.

```bash
ssh -p 2220 bandit1@bandit.labs.overthewire.org
```

비밀번호에는 방금 `readme`에서 찾은 값을 입력합니다. 접속 후 `whoami`가 `bandit1`이면 첫 문제를 완료했습니다.

## 4. 이후 진행 방법

매 단계마다 다음 과정을 반복합니다.

1. 현재 계정에서 풀어야 할 공식 문제를 읽습니다.
2. 현재 위치와 파일을 조사합니다.
3. 필요한 명령의 도움말을 확인하고 조건에 맞는 파일·문자열을 찾습니다.
4. 다음 계정의 비밀번호를 개인적으로 보관합니다.
5. `exit`로 종료한 뒤 **내 컴퓨터에서** 다음 계정으로 SSH 접속합니다.
6. 사용한 명령과 이유를 풀이 기록에 남깁니다.

웹 페이지의 `Level 0 → Level 1`은 **bandit0에서 풀고 bandit1로 넘어가는 문제**입니다. 이 문서의 첫 목표인 `bandit10` 진입까지는 `Level 9 → Level 10`을 완료하면 됩니다.

| 현재 계정 → 다음 계정 | 배울 내용 | 조사할 명령·개념 | 공식 문제 |
|---|---|---|---|
| 최초 접속 → bandit0 | SSH 주소·포트·계정 | `ssh -p` | [Level 0](https://overthewire.org/wargames/bandit/bandit0.html) |
| bandit0 → bandit1 | 파일 목록·내용 읽기 | `ls`, `cat` | [0 → 1](https://overthewire.org/wargames/bandit/bandit1.html) |
| bandit1 → bandit2 | 이름이 `-`인 파일 | 표준 입력과 파일명, `./` 경로 | [1 → 2](https://overthewire.org/wargames/bandit/bandit2.html) |
| bandit2 → bandit3 | 공백과 선행 하이픈이 있는 파일명 | 따옴표, `./`, 옵션 종료 `--` | [2 → 3](https://overthewire.org/wargames/bandit/bandit3.html) |
| bandit3 → bandit4 | 숨김 파일 | `cd`, `ls -la` | [3 → 4](https://overthewire.org/wargames/bandit/bandit4.html) |
| bandit4 → bandit5 | 여러 파일 중 텍스트 파일 찾기 | `file`, 와일드카드 | [4 → 5](https://overthewire.org/wargames/bandit/bandit5.html) |
| bandit5 → bandit6 | 크기·형식·실행 권한 조건 | `find`, `file`, `wc -c` | [5 → 6](https://overthewire.org/wargames/bandit/bandit6.html) |
| bandit6 → bandit7 | 소유자·그룹·크기로 검색 | `find`, 표준 오류 | [6 → 7](https://overthewire.org/wargames/bandit/bandit7.html) |
| bandit7 → bandit8 | 특정 단어가 있는 줄 검색 | `grep` | [7 → 8](https://overthewire.org/wargames/bandit/bandit8.html) |
| bandit8 → bandit9 | 한 번만 나오는 줄 찾기 | `sort`, `uniq`, 파이프 `\|` | [8 → 9](https://overthewire.org/wargames/bandit/bandit9.html) |
| bandit9 → bandit10 | 바이너리 안의 읽을 수 있는 문자열 | `strings`, `grep` | [9 → 10](https://overthewire.org/wargames/bandit/bandit10.html) |

문제 조건과 파일명은 공식 페이지를 우선합니다. 예를 들어 현재 2 → 3 문제의 파일명은 `--spaces in this filename--`이므로 공백 처리와 선행 하이픈 처리를 함께 생각해야 합니다.

## 5. 기본 명령과 도움말

```bash
pwd          # 현재 디렉터리
whoami       # 현재 사용자
ls -la       # 숨김 파일과 권한을 포함한 목록
cd ~         # 현재 사용자의 홈 디렉터리로 이동
file ./readme  # 파일 형식 추정: readme가 있는 단계에서 실행
man ls       # ls 매뉴얼
help cd      # Bash 내장 명령 도움말
```

`man`에서는 `/검색어`로 검색하고 `n`으로 다음 결과, `q`로 종료합니다. `cd` 같은 셸 내장 명령은 `help`도 활용합니다. 위 명령들은 같은 기능이 아닙니다. 파일 이름을 찾는 것, 파일 형식을 확인하는 것, 내용을 읽는 것을 나누어 생각하세요.

추가 개념:

- **따옴표:** 공백이 있는 경로를 하나의 인자로 전달합니다.
- **`./`:** 현재 디렉터리의 경로를 명시합니다. 파일명이 옵션·표준 입력 표기로 해석되는 상황을 구분할 때 유용합니다.
- **`--`:** 이를 지원하는 명령에서 이후 인자를 옵션으로 해석하지 않도록 합니다.
- **파이프 `|`:** 앞 명령의 표준 출력을 다음 명령의 표준 입력으로 연결합니다.
- **`2>/dev/null`:** 표준 오류를 숨깁니다. 원인을 조사할 때는 먼저 오류를 읽고, 예상한 권한 오류임을 확인한 뒤 필요에 따라 사용합니다.
- **`uniq`:** 연속해서 나타나는 중복 줄을 처리합니다. 파일 전체의 중복을 찾을 때 정렬이 필요한 이유를 설명해 봅니다.

Bandit 서버에 `rg` 등 개인 환경의 도구가 있다고 가정하지 말고 공식 페이지가 안내하는 기본 명령부터 사용합니다.

## 6. 막혔을 때

| 증상 | 확인할 내용 |
|---|---|
| 비밀번호를 입력해도 아무것도 안 보임 | 정상 동작입니다. 입력 후 Enter를 누릅니다. |
| `Permission denied`로 로그인 실패 | 현재 접속하려는 계정과 그 계정의 비밀번호가 맞는지 확인합니다. 이전 계정 비밀번호와 구분합니다. |
| `Connection timed out` 또는 `Connection refused` | 서버 주소·포트 2220, 현재 네트워크의 외부 SSH 허용 여부, 서비스 상태를 확인합니다. |
| `Could not resolve hostname` | 호스트 오타와 DNS 연결을 확인합니다. |
| `cat -` 뒤 멈춘 것처럼 보임 | 파일 대신 표준 입력을 기다리는 상황일 수 있습니다. `Ctrl+C`로 중단하고 파일 경로 표현을 조사합니다. |
| 바이너리 출력 뒤 터미널이 깨짐 | `reset`으로 복원하고 다음에는 `file`·`strings`로 먼저 조사합니다. |
| 서버 키 변경 경고 | 무조건 검사를 끄거나 기존 키를 삭제하지 말고 공식 안내와 키 변경 여부를 확인합니다. |

가상 머신의 NAT 환경에서 `broken pipe`가 발생한다면 공식 소개의 VM 안내를 확인합니다. 시스템 전체 설정을 바꾸기 전에 로컬에서 다음 연결 옵션을 적용해 볼 수 있습니다.

```bash
ssh -o IPQoS=throughput -p 2220 bandit0@bandit.labs.overthewire.org
```

접속 진단이 필요하면 `ssh -v -p 2220 bandit0@bandit.labs.overthewire.org`를 사용합니다. 로그를 공유할 때는 사용자 환경 경로·키 정보 등 불필요한 정보를 가립니다. [공식 VM 안내](https://overthewire.org/wargames/bandit/)

## 7. 풀이 기록

저장소에 남길 내용은 비밀번호를 제외한 과정입니다. 아래 양식을 단계마다 복사합니다.

```text
단계: bandit0 → bandit1
공식 문제 URL:
목표:
현재 계정과 위치:
사용한 명령:
명령·옵션을 선택한 이유:
실패한 시도와 원인:
관찰한 결과: 비밀번호 문자열은 제외
다음 계정 접속 확인:
방어 관점에서 배운 점:
```

예를 들어 숨김 파일은 보안 경계가 아니며, 파일 이름을 복잡하게 만드는 것과 권한으로 읽기를 제한하는 것은 다릅니다. 찾은 비밀번호도 저장 위치와 읽기 권한이 적절했는지 생각해 봅니다.

## 오늘의 완료 기준

- [ ] 로컬과 원격 터미널을 구분할 수 있다.
- [ ] `bandit0`로 접속하고 `whoami`를 확인했다.
- [ ] `ls`와 `cat`의 역할을 설명할 수 있다.
- [ ] 첫 비밀번호를 찾아 `bandit1`로 접속했다.
- [ ] 비밀번호를 제외한 풀이 기록을 남겼다.

다음에는 1 → 2와 2 → 3에서 파일명·인자·옵션의 차이를 연습합니다. `bandit10`에 도달한 뒤에는 [네트워크 구조와 관찰](network-security/ch-01.md)에서 로컬 연결과 프로세스를 관찰할 수 있습니다.
