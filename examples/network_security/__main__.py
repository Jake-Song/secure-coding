"""네트워크 보안 실습 CLI. 저장소 루트에서 -m으로 실행한다."""
import argparse
import importlib
from pathlib import Path

LABS = ("framing", "dns", "pcap", "tls", "auth", "policy", "detection")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab", choices=("all", *LABS))
    parser.add_argument("--output", type=Path, help="pcap 실습의 새 출력 파일")
    parser.add_argument("--events", type=Path, help="detection 실습의 JSONL 입력 파일")
    args = parser.parse_args()
    if args.output is not None and args.lab != "pcap":
        parser.error("--output은 pcap에서만 사용합니다")
    if args.events is not None and args.lab != "detection":
        parser.error("--events는 detection에서만 사용합니다")
    for name in LABS if args.lab == "all" else (args.lab,):
        module = importlib.import_module(f"{__package__}.{name}")
        if name == "pcap" and args.output is not None:
            print(f"PCAP: wrote synthetic capture to {module.write_capture(args.output)}")
        elif name == "detection" and args.events is not None:
            module.demo(args.events)
        else:
            module.demo()


if __name__ == "__main__":
    main()
