# 1주차 Linux 기초

[12주 커리큘럼](curriculum.md) · [다음 2주차](week-02.md)

SSH로 접속하면 명령은 원격 컴퓨터에서 실행됩니다. `pwd`는 현재 디렉터리, `id`는 현재 사용자를 보여 줍니다. 같은 `cat` 명령도 실행하는 호스트, 파일 경로, 사용자 권한에 따라 결과가 달라집니다.

먼저 [Bandit 시작하기](../bandit.md)에서 첫 SSH 접속과 파일 읽기를 연습하세요. 첫날은 `bandit1` 진입, 주차 목표는 `bandit10` 진입입니다. 다음 명령은 SSH에서 나온 뒤 **로컬 WSL 터미널**에서 실행합니다.

```bash
id
pwd
ps -o pid,ppid,user,comm -p $$
lab_dir=$(mktemp -d)
printf 'hello\n' > "$lab_dir/message.txt"
chmod 600 "$lab_dir/message.txt"
ls -l "$lab_dir/message.txt"
cat "$lab_dir/message.txt" | wc -c
```

`ls -l`의 맨 앞에는 `-rw-------`가, `wc -c`에는 `6`이 나옵니다. `hello` 다섯 바이트와 줄바꿈 한 바이트를 센 값입니다. `ps`에서 PID는 현재 셸 프로세스, PPID는 그 부모 프로세스입니다. [기초 실습 1주차](../foundations.md#1주차-linux)에서 `strace`를 사용할 수 있다면 `cat`의 파일 열기와 읽기가 `openat`과 `read`로 운영체제에 전달되는 과정도 확인하세요.

**확인 문제.** `600`을 `644`로 바꾸면 누구에게 어떤 권한이 추가되나요? 본인 계정으로 읽는 것만으로는 어떤 접근 결과까지 확인할 수 있나요?

**제출물.** 파일 권한 표, PID·PPID 예시, Bandit에서 사용한 명령과 선택 이유를 기록하세요. 단계 비밀번호는 가립니다.
