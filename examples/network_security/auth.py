"""HMAC 인증, 재전송 차단, 객체별 인가를 각각 비교한다."""
import hashlib
import hmac
import json
import secrets
import socket
import threading
import time

from .common import HOST, TIMEOUT, tcp_server
from .framing import ProtocolError, recv_json, send_json

FIELDS = {"user", "timestamp", "nonce", "action", "note"}
NOTES = {1: ("alice", "Alice lab note"), 2: ("bob", "Bob lab note")}


def canonical(message):
    return json.dumps(message, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def sign(key, user="alice", note=1, timestamp=None, nonce=None):
    body = {"user": user, "timestamp": int(time.time()) if timestamp is None else timestamp,
            "nonce": secrets.token_hex(16) if nonce is None else nonce,
            "action": "read", "note": note}
    signature = hmac.new(key, canonical(body), hashlib.sha256).hexdigest()
    return {**body, "mac": signature}


class Verifier:
    def __init__(self, keys, freshness=True, clock=time.time, window=30, max_nonces=128):
        self.keys = dict(keys)
        self.freshness = freshness
        self.clock = clock
        self.window = window
        self.max_nonces = max_nonces
        self.seen = {}
        self.lock = threading.Lock()

    def handle(self, request):
        if not isinstance(request, dict) or set(request) != FIELDS | {"mac"}:
            return {"ok": False, "reason": "schema"}
        user, stamp, nonce, action, note, mac = (
            request[name] for name in ("user", "timestamp", "nonce", "action", "note", "mac"))
        if (not isinstance(user, str) or len(user) > 32
                or type(stamp) is not int or not 0 <= stamp <= 2**53
                or type(note) is not int
                or not isinstance(nonce, str) or len(nonce) != 32
                or any(c not in "0123456789abcdef" for c in nonce)
                or action != "read" or not isinstance(mac, str) or len(mac) != 64
                or any(c not in "0123456789abcdef" for c in mac)):
            return {"ok": False, "reason": "schema"}
        key = self.keys.get(user)
        body = {name: request[name] for name in FIELDS}
        expected = hmac.new(key or b"unknown-user", canonical(body), hashlib.sha256).hexdigest()
        if key is None or not hmac.compare_digest(mac, expected):
            return {"ok": False, "reason": "authentication"}
        if self.freshness:
            now = self.clock()
            if abs(now - stamp) > self.window:
                return {"ok": False, "reason": "expired"}
            with self.lock:
                self.seen = {item: expiry for item, expiry in self.seen.items() if expiry >= now}
                identity = (user, nonce)
                if identity in self.seen:
                    return {"ok": False, "reason": "replay"}
                if len(self.seen) >= self.max_nonces:
                    return {"ok": False, "reason": "nonce_capacity"}
                # 미래 timestamp를 허용한 경우에도 유효 구간 전체를 보존한다.
                self.seen[identity] = stamp + self.window
        record = NOTES.get(note)
        if record is None or record[0] != user:
            return {"ok": False, "reason": "forbidden"}
        return {"ok": True, "note": record[1]}


def exchange(verifier, requests):
    if not 1 <= len(requests) <= 16:
        raise ValueError("1~16개 요청이 필요합니다")

    def handle(connection):
        try:
            response = verifier.handle(recv_json(connection))
        except ProtocolError:
            response = {"ok": False, "reason": "protocol"}
        send_json(connection, response)

    responses = []
    with tcp_server(handle, len(requests)) as port:
        for request in requests:
            with socket.create_connection((HOST, port), TIMEOUT) as connection:
                send_json(connection, request)
                responses.append(recv_json(connection))
    return responses


def demo():
    # 매번 새 실습 키를 생성하고 출력하거나 저장하지 않는다.
    key = secrets.token_bytes(32)
    keys = {"alice": key}
    original = sign(key)
    vulnerable = exchange(Verifier(keys, freshness=False), [original, original])
    safe = exchange(Verifier(keys), [original, original])
    tampered = {**sign(key), "note": 2}
    denied = exchange(Verifier(keys), [tampered, sign(key, note=2),
                                     sign(key, timestamp=int(time.time()) - 60)])
    print(f"AUTH: MAC-only replay -> {[r['ok'] for r in vulnerable]}")
    print(f"AUTH: MAC + freshness -> {[r.get('reason', 'accepted') for r in safe]}")
    print(f"AUTH: tampered / other owner's note / stale -> {[r['reason'] for r in denied]}")


if __name__ == "__main__":
    demo()
