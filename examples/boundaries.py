"""Chapter 8~9: 고정 입력·임시 파일·가상 서비스로 신뢰 경계를 비교한다."""
from pathlib import Path
import secrets
import subprocess
import tempfile


def command_demo():
    # 고정된 무해한 입력만 사용하며 HTTP 엔드포인트로 노출하지 않는다.
    value = "hello; printf LAB_MARKER"
    vulnerable = subprocess.run(f"printf '%s' {value}", shell=True,
                                check=True, capture_output=True, text=True).stdout
    safe = subprocess.run(["printf", "%s", value], shell=False,
                         check=True, capture_output=True, text=True).stdout
    return vulnerable, safe


def read_file(root, name, *, safe):
    root = Path(root).resolve()
    public = root / "public"
    target = (public / name).resolve()
    # 실습 울타리: 취약 버전도 임시 fixture 바깥의 실제 파일은 읽지 못한다.
    if not target.is_relative_to(root):
        raise PermissionError("실습 디렉터리 밖입니다")
    if safe and not target.is_relative_to(public):
        raise PermissionError("공개 디렉터리 밖입니다")
    return target.read_text(encoding="utf-8")


def save_text_upload(directory, client_filename, data):
    """텍스트 첨부 전용 예제. 이미지·압축 파일·문서 검증으로 일반화하지 않는다."""
    if Path(client_filename).suffix.lower() != ".txt":
        raise ValueError("txt만 허용합니다")
    if len(data) > 1024:
        raise ValueError("1 KiB 이하만 허용합니다")
    data.decode("utf-8")  # 확장자만 확인하는 대신 실제 텍스트 디코딩도 검사한다.
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{secrets.token_hex(16)}.txt"
    with target.open("xb") as stream:
        stream.write(data)
    return target


# 실제 DNS 조회나 HTTP 요청을 하지 않는 SSRF 모델이다.
FAKE_SERVICES = {
    "https://catalog.lab/items": "public catalog",
    "http://internal.lab/config": "FAKE_INTERNAL_SECRET",
}
PUBLIC_URL = "https://catalog.lab/items"


def fetch_fixture(url, *, safe):
    if safe and url != PUBLIC_URL:
        raise PermissionError("허용한 목적지가 아닙니다")
    return FAKE_SERVICES[url]


def main():
    print("명령어: 취약 / 방어 =", command_demo())
    with tempfile.TemporaryDirectory(prefix="secure-coding-") as directory:
        root = Path(directory)
        (root / "public").mkdir()
        (root / "public/readme.txt").write_text("public", encoding="utf-8")
        (root / "secret.txt").write_text("FAKE_FILE_SECRET", encoding="utf-8")
        print("경로 취약:", read_file(root, "../secret.txt", safe=False))
        try:
            read_file(root, "../secret.txt", safe=True)
        except PermissionError as error:
            print("경로 방어:", error)
        saved = save_text_upload(root / "uploads", "../../memo.txt", b"hello")
        print("업로드: 클라이언트 경로 대신 서버 생성 이름 사용:", saved.name)
    print("SSRF 취약:", fetch_fixture("http://internal.lab/config", safe=False))
    try:
        fetch_fixture("http://internal.lab/config", safe=True)
    except PermissionError as error:
        print("SSRF 방어:", error)


if __name__ == "__main__":
    main()
