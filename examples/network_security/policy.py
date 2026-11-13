"""오프라인 L3/L4 접근 정책 모델. OS 방화벽을 변경하지 않는다."""
from dataclasses import dataclass
import ipaddress


@dataclass(frozen=True)
class Flow:
    source: str
    destination: str
    protocol: str
    port: int


@dataclass(frozen=True)
class Rule:
    source: str
    destination: str
    protocol: str
    port: int


ALLOW_RULES = (
    Rule("192.0.2.0/24", "198.51.100.10/32", "tcp", 443),
    Rule("198.51.100.10/32", "203.0.113.20/32", "tcp", 5432),
)


def allowed(flow, rules=ALLOW_RULES):
    try:
        source = ipaddress.ip_address(flow.source)
        destination = ipaddress.ip_address(flow.destination)
    except ValueError:
        return False
    if flow.protocol not in {"tcp", "udp"} or type(flow.port) is not int or not 1 <= flow.port <= 65535:
        return False
    return any(source in ipaddress.ip_network(rule.source)
               and destination in ipaddress.ip_network(rule.destination)
               and flow.protocol == rule.protocol and flow.port == rule.port
               for rule in rules)


def demo():
    scenarios = (
        ("client -> web HTTPS", Flow("192.0.2.25", "198.51.100.10", "tcp", 443)),
        ("web -> database", Flow("198.51.100.10", "203.0.113.20", "tcp", 5432)),
        ("client -> database", Flow("192.0.2.25", "203.0.113.20", "tcp", 5432)),
        ("client -> web SSH", Flow("192.0.2.25", "198.51.100.10", "tcp", 22)),
        ("client -> web UDP/443", Flow("192.0.2.25", "198.51.100.10", "udp", 443)),
    )
    for label, flow in scenarios:
        print(f"POLICY (model): {label} -> {'ALLOW' if allowed(flow) else 'DENY'}")


if __name__ == "__main__":
    demo()
