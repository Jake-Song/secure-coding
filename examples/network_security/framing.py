"""TCP 스트림에 4바이트 길이 접두사와 크기 제한을 적용한다."""
import json
import socket
import struct

from .common import HOST, TIMEOUT, tcp_server

MAX_FRAME = 4096


class ProtocolError(ValueError):
    pass


def recv_exact(connection, size):
    data = bytearray()
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            raise ProtocolError("truncated frame")
        data.extend(chunk)
    return bytes(data)


def encode_frame(payload):
    if len(payload) > MAX_FRAME:
        raise ProtocolError("frame too large")
    return struct.pack("!I", len(payload)) + payload


def recv_frame(connection):
    size = struct.unpack("!I", recv_exact(connection, 4))[0]
    if size > MAX_FRAME:
        raise ProtocolError("frame too large")
    return recv_exact(connection, size)


def send_json(connection, value):
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
    connection.sendall(encode_frame(payload))


def recv_json(connection):
    try:
        return json.loads(recv_frame(connection))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise ProtocolError("invalid JSON") from error


def exchange_frames(messages, fragmented=False):
    if not 1 <= len(messages) <= 16:
        raise ValueError("1~16개 메시지가 필요합니다")
    wire = b"".join(encode_frame(message) for message in messages)

    def echo(connection):
        for _ in messages:
            connection.sendall(encode_frame(recv_frame(connection)))

    with tcp_server(echo) as port:
        with socket.create_connection((HOST, port), TIMEOUT) as connection:
            if fragmented:
                # 애플리케이션의 쓰기를 나눈다. TCP 패킷 분할을 강제하지 않는다.
                for offset in range(0, len(wire), 3):
                    connection.sendall(wire[offset:offset + 3])
            else:
                connection.sendall(wire)
            return [recv_frame(connection) for _ in messages]


def demo():
    messages = [b"", b"hello", "안녕하세요".encode()]
    for fragmented in (False, True):
        received = exchange_frames(messages, fragmented)
        if received != messages:
            raise RuntimeError("TCP round trip mismatch")
        print(f"TCP: fragmented_writes={fragmented}, {len(received)} frames OK")
    try:
        encode_frame(b"x" * (MAX_FRAME + 1))
    except ProtocolError as error:
        print(f"TCP: oversized payload rejected ({error})")


if __name__ == "__main__":
    demo()
