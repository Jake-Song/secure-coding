"""단일 IN A 질의를 처리하는 loopback UDP DNS 교육 예제."""
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import secrets
import socket
import struct

from .common import HOST, TIMEOUT
from .framing import ProtocolError

HEADER = struct.Struct("!6H")
MAX_PACKET = 512


def encode_name(name):
    labels = name.rstrip(".").lower().split(".")
    try:
        parts = [label.encode("ascii") for label in labels]
    except UnicodeEncodeError as error:
        raise ProtocolError("ASCII names only") from error
    if any(not 1 <= len(part) <= 63 for part in parts):
        raise ProtocolError("invalid DNS label")
    wire = b"".join(bytes([len(part)]) + part for part in parts) + b"\0"
    if len(wire) > 255:
        raise ProtocolError("DNS name too long")
    return wire


def read_name(packet, offset):
    labels, visited, end = [], set(), None
    expanded_size = 1
    while True:
        if offset >= len(packet) or offset in visited:
            raise ProtocolError("truncated or cyclic DNS name")
        visited.add(offset)
        length = packet[offset]
        if length & 0xc0 == 0xc0:
            if offset + 1 >= len(packet):
                raise ProtocolError("truncated DNS pointer")
            if end is None:
                end = offset + 2
            offset = ((length & 0x3f) << 8) | packet[offset + 1]
            continue
        if length & 0xc0:
            raise ProtocolError("unsupported DNS label")
        offset += 1
        if length == 0:
            return ".".join(labels).lower(), end if end is not None else offset
        if offset + length > len(packet):
            raise ProtocolError("truncated DNS label")
        expanded_size += 1 + length
        if expanded_size > 255:
            raise ProtocolError("expanded DNS name too long")
        try:
            labels.append(packet[offset:offset + length].decode("ascii"))
        except UnicodeDecodeError as error:
            raise ProtocolError("ASCII names only") from error
        offset += length


def parse(packet):
    if not 12 <= len(packet) <= MAX_PACKET:
        raise ProtocolError("invalid DNS packet size")
    ident, flags, qd, an, ns, ar = HEADER.unpack_from(packet)
    # 단일 질의와 A 응답만 다룬다. EDNS/CNAME 등은 확장 과제다.
    if qd != 1 or an > 1 or ns or ar or flags & 0x7800 or flags & 0x0200:
        raise ProtocolError("unsupported DNS message")
    name, offset = read_name(packet, 12)
    if offset + 4 > len(packet):
        raise ProtocolError("truncated question")
    qtype, qclass = struct.unpack_from("!HH", packet, offset)
    if (qtype, qclass) != (1, 1):
        raise ProtocolError("only IN A questions supported")
    question_end = offset + 4
    offset = question_end
    address = None
    if an:
        owner, offset = read_name(packet, offset)
        if offset + 10 > len(packet):
            raise ProtocolError("truncated answer")
        rtype, rclass, ttl, size = struct.unpack_from("!HHIH", packet, offset)
        offset += 10
        if owner != name or (rtype, rclass, size) != (1, 1, 4):
            raise ProtocolError("unsupported answer")
        if offset + size > len(packet):
            raise ProtocolError("truncated address")
        address = str(ipaddress.IPv4Address(packet[offset:offset + size]))
        offset += size
    if offset != len(packet):
        raise ProtocolError("trailing DNS bytes")
    return {"id": ident, "flags": flags, "name": name, "address": address,
            "question_end": question_end}


def make_query(name="service.test", ident=None):
    if ident is None:
        ident = secrets.randbelow(65536)
    return HEADER.pack(ident, 0x0100, 1, 0, 0, 0) + encode_name(name) + struct.pack("!HH", 1, 1)


def make_response(query):
    request = parse(query)
    if request["flags"] & 0x8000 or request["address"] is not None:
        raise ProtocolError("expected query")
    known = request["name"] == "service.test"
    # 서비스가 하나뿐인 로컬 권한 응답 모델. 재귀 질의를 수행하지 않는다.
    flags = 0x8400 | (request["flags"] & 0x0100) | (0 if known else 3)
    response = HEADER.pack(request["id"], flags, 1, int(known), 0, 0)
    response += query[12:request["question_end"]]
    if known:
        response += b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 60, 4)
        response += ipaddress.IPv4Address(HOST).packed
    return response


def validate_response(response, query):
    request, answer = parse(query), parse(response)
    if not answer["flags"] & 0x8000:
        raise ProtocolError("not a response")
    if answer["id"] != request["id"] or answer["name"] != request["name"]:
        raise ProtocolError("response does not match query")
    rcode = answer["flags"] & 0xf
    if rcode == 3 and answer["address"] is None:
        return None
    if rcode != 0 or answer["address"] is None:
        raise ProtocolError("unsupported response status")
    return answer["address"]


def lookup(name):
    query = make_query(name)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((HOST, 0))
        server.settimeout(TIMEOUT)

        def respond():
            packet, peer = server.recvfrom(MAX_PACKET + 1)
            server.sendto(make_response(packet), peer)

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(respond)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
                client.settimeout(TIMEOUT)
                # 연결형 UDP로 지정한 loopback 서버의 주소/포트만 수신한다.
                client.connect(server.getsockname())
                client.send(query)
                response = client.recv(MAX_PACKET + 1)
            future.result(timeout=TIMEOUT + 1)
    return validate_response(response, query)


def demo():
    print(f"DNS: service.test -> {lookup('service.test')}")
    print(f"DNS: missing.test -> {lookup('missing.test')} (NXDOMAIN)")
    query = make_query(ident=100)
    wrong = bytearray(make_response(query))
    wrong[:2] = struct.pack("!H", 101)
    try:
        validate_response(bytes(wrong), query)
    except ProtocolError as error:
        print(f"DNS: mismatched transaction rejected ({error})")


if __name__ == "__main__":
    demo()
