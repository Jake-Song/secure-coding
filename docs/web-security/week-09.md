# 9주차 명령어·파일·업로드 경계

[이전 8주차](week-08.md) · [12주 커리큘럼](curriculum.md) · [다음 10주차](week-10.md)

셸은 명령 문자열에서 인자와 제어 문법을 해석합니다. 고정 프로그램을 호출해야 한다면 실행 파일과 인자를 리스트로 넘겨 각각의 경계를 유지할 수 있습니다. 파일 접근은 경로를 실제 위치로 해석한 뒤 공개 디렉터리 아래에 있는지 검사합니다. 심볼릭 링크가 있으면 입력 이름과 최종 위치가 달라질 수 있습니다.

다음 예제는 공백이 있는 문장을 `printf`에 인자 하나로 전달합니다.

```bash
python - <<'PY'
import subprocess

subprocess.run(["printf", "%s\n", "hello world"], check=True)
PY
```

출력은 `hello world` 한 줄입니다. 다음으로 [경계 예제 코드](../../examples/boundaries.py)의 `read_file`과 `save_text_upload`를 읽으세요. 전자는 `resolve()`로 경로를 해석한 뒤 허용 디렉터리 아래인지 확인합니다. 후자는 `.txt`, 1 KiB 제한, UTF-8 디코딩을 검사하고 서버에서 생성한 파일명으로 저장합니다. 아래 예제는 정상 파일 읽기와 저장 결과의 이름을 확인합니다.

```bash
python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory

from examples.boundaries import read_file, save_text_upload

with TemporaryDirectory() as temporary:
    root = Path(temporary)
    (root / "public").mkdir()
    (root / "public" / "hello.txt").write_text("hello", encoding="utf-8")
    print(read_file(root, "hello.txt", safe=True))
    saved = save_text_upload(root / "uploads", "notes.txt", b"hello")
    print(saved.suffix, saved.name == "notes.txt", saved.read_text(encoding="utf-8"))
PY
```

예상 결과는 `hello`와 `.txt False hello`입니다. `False`는 저장 파일명이 클라이언트가 제공한 이름과 다르다는 뜻입니다.

**확인 문제.** 파일 이름, 파일 크기, 텍스트 디코딩은 각각 어느 위험을 줄이나요? 목록 방식으로 명령을 실행할 때 실행 파일과 옵션에는 어떤 값을 허용할지 왜 별도로 판단해야 하나요?

**제출물.** 명령 인자, 파일 경로, 업로드의 검사 위치를 표로 정리하고 정상 파일·공개 범위 밖 경로·심볼릭 링크·비 UTF-8·크기 초과에 대한 기대 동작을 적으세요.
