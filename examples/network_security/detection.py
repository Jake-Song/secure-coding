"""합성 JSONL 로그에서 시간 창별 거부 포트·인증 실패를 탐지한다."""
import argparse
from collections import defaultdict, deque
import ipaddress
import json
from pathlib import Path

SAMPLE = Path(__file__).with_name("events.jsonl")
MAX_EVENTS = 10000


def validate_event(event):
    required = {"time", "source", "destination", "port", "event"}
    if not isinstance(event, dict) or set(event) != required:
        raise ValueError("invalid event fields")
    if (type(event["time"]) not in (int, float) or not 0 <= event["time"] <= 10**12
            or type(event["port"]) is not int or not 1 <= event["port"] <= 65535
            or event["event"] not in ("allow", "deny", "auth_failure")
            or not isinstance(event["source"], str) or not isinstance(event["destination"], str)):
        raise ValueError("invalid event values")
    ipaddress.ip_address(event["source"])
    ipaddress.ip_address(event["destination"])


def load_events(path):
    events = []
    with Path(path).open(encoding="utf-8") as stream:
        for number in range(1, MAX_EVENTS + 2):
            line = stream.readline(4097)
            if not line:
                break
            if len(line) > 4096 or number > MAX_EVENTS:
                raise ValueError("log limit exceeded")
            event = json.loads(line)
            validate_event(event)
            if events and event["time"] < events[-1]["time"]:
                raise ValueError("events must be ordered by time")
            events.append(event)
    return events


def detect(events, window=10, port_threshold=4, auth_threshold=3):
    if window <= 0 or port_threshold < 1 or auth_threshold < 1:
        raise ValueError("positive window and thresholds required")
    history = defaultdict(deque)
    previous, alerts = float("-inf"), []
    active = set()
    for number, event in enumerate(events, 1):
        if number > MAX_EVENTS:
            raise ValueError("log limit exceeded")
        validate_event(event)
        now = event["time"]
        if now < previous:
            raise ValueError("events must be ordered by time")
        previous = now
        # 호스트 쌍별 창. 집계 키의 수와 입력량은 교육용 한도로 제한된다.
        key = event["source"], event["destination"]
        bucket = history[key]
        while bucket and bucket[0]["time"] < now - window:
            bucket.popleft()
        bucket.append(event)
        ports = {item["port"] for item in bucket if item["event"] == "deny"}
        auth_failures = sum(item["event"] == "auth_failure" for item in bucket)
        conditions = {"many_denied_ports": len(ports) >= port_threshold,
                      "repeated_auth_failures": auth_failures >= auth_threshold}
        for kind, triggered in conditions.items():
            identity = key, kind
            if triggered and identity not in active:
                alerts.append({"time": now, "source": key[0], "destination": key[1], "kind": kind})
            if triggered:
                active.add(identity)
            else:
                active.discard(identity)
    return alerts


def demo(path=SAMPLE):
    events = load_events(path)
    alerts = detect(events)
    print(f"DETECTION: synthetic/local input, {len(events)} events, {len(alerts)} alerts")
    for alert in alerts:
        print(json.dumps(alert, ensure_ascii=False, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=SAMPLE)
    demo(parser.parse_args().events)


if __name__ == "__main__":
    main()
