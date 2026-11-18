"""Compare 08_transform with a Python reimplementation on boundary inputs.

Usage: python3 compare_transform.py BINARY IMPLEMENTATION.py

IMPLEMENTATION.py must define transform(data: bytes) -> tuple[bytes, int].
"""

import importlib.util
from pathlib import Path
import random
import subprocess
import sys

MAX_INPUT = 64


def load_transform(path):
    spec = importlib.util.spec_from_file_location("student_transform", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "transform", None)):
        raise SystemExit(f"{path} must define transform(data)")
    return module.transform


def run_original(binary, data):
    result = subprocess.run([binary], input=data, capture_output=True, timeout=10, check=False)
    if result.returncode != 0:
        raise SystemExit(f"original failed ({result.returncode}): {result.stderr!r}")
    fields = dict(line.split("=", 1) for line in result.stdout.decode("ascii").splitlines())
    if int(fields["length"]) != len(data):
        raise SystemExit(f"length mismatch for {data.hex()}")
    return bytes.fromhex(fields["out"]), int(fields["acc"], 16)


def cases():
    generator = random.Random(8)
    fixed = [
        ("empty", b""),
        ("one NUL", b"\x00"),
        ("0x7f", b"\x7f"),
        ("0x80", b"\x80"),
        ("0xff", b"\xff"),
        ("ascii", b"trace"),
        ("negative /4 edge", bytes([0x80, 0x81, 0xfc, 0xfd, 0xfe, 0xff])),
        ("positive /4 edge", bytes([0x00, 0x01, 0x03, 0x04, 0x7c, 0x7f])),
        ("key rotation 9", bytes(9)),
        ("0..63", bytes(range(MAX_INPUT))),
        ("max 0xff", b"\xff" * MAX_INPUT),
    ]
    randomized = [(f"random {n}", generator.randbytes(generator.randint(1, MAX_INPUT)))
                  for n in range(10)]
    return fixed + randomized


def first_difference(left, right):
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right))


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    binary, transform = Path(argv[1]).resolve(), load_transform(argv[2])
    failures = 0
    all_cases = cases()
    print(f"{'case':<18} {'len':>3}  {'out':<6} {'acc':<6} detail")
    for name, data in all_cases:
        expected_out, expected_acc = run_original(binary, data)
        actual_out, actual_acc = transform(data)
        out_ok = bytes(actual_out) == expected_out
        acc_ok = actual_acc == expected_acc
        detail = ""
        if not out_ok:
            detail += f"out differs at byte {first_difference(bytes(actual_out), expected_out)} "
        if not acc_ok:
            detail += f"acc expected {expected_acc:08x} got {actual_acc:#x}"
        failures += not (out_ok and acc_ok)
        print(f"{name:<18} {len(data):>3}  {'ok' if out_ok else 'DIFF':<6} "
              f"{'ok' if acc_ok else 'DIFF':<6} {detail}")
    print(f"{len(all_cases) - failures}/{len(all_cases)} matched")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
