"""Wireshark에서 열 수 있는 합성 Ethernet/IPv4/UDP/DNS PCAP을 만든다."""
import argparse
import ipaddress
from pathlib import Path
import struct

from .dns import make_query, make_response


def checksum(data):
    if len(data) % 2:
        data += b"\0"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xffff) + (total >> 16)
    return (~total) & 0xffff


def udp_packet(payload, source, destination, sport, dport, source_mac, destination_mac):
    # 합성 패킷: Ethernet + IPv4(20바이트) + UDP(8바이트).
    source_ip = ipaddress.IPv4Address(source).packed
    destination_ip = ipaddress.IPv4Address(destination).packed
    udp = struct.pack("!HHHH", sport, dport, 8 + len(payload), 0)
    pseudo = source_ip + destination_ip + struct.pack("!BBH", 0, 17, 8 + len(payload))
    udp_sum = checksum(pseudo + udp + payload) or 0xffff
    udp = struct.pack("!HHHH", sport, dport, 8 + len(payload), udp_sum)
    header = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 28 + len(payload), 1, 0,
                         64, 17, 0, source_ip, destination_ip)
    header = header[:10] + struct.pack("!H", checksum(header)) + header[12:]
    ethernet = destination_mac + source_mac + b"\x08\x00"
    return ethernet + header + udp + payload


def sample_capture():
    query = make_query("service.test", ident=0x1234)
    response = make_response(query)
    # PCAP의 주소는 문서 전용 대역이며 실제 소켓의 주소와는 다르다.
    client_mac = bytes.fromhex("020000000001")
    server_mac = bytes.fromhex("020000000002")
    packets = [udp_packet(query, "192.0.2.10", "192.0.2.53", 53000, 53, client_mac, server_mac),
               udp_packet(response, "192.0.2.53", "192.0.2.10", 53, 53000, server_mac, client_mac)]
    wire = bytearray(struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
    for index, packet in enumerate(packets):
        wire.extend(struct.pack("<IIII", 1700000000, index * 1000, len(packet), len(packet)))
        wire.extend(packet)
    return bytes(wire)


def write_capture(path):
    path = Path(path)
    # 사용자가 가진 캡처를 실수로 덮어쓰지 않는다.
    with path.open("xb") as stream:
        stream.write(sample_capture())
    return path


def demo():
    data = sample_capture()
    print(f"PCAP: synthetic DNS query + response, 2 packets, {len(data)} bytes")
    print("PCAP: export with python3 -m examples.network_security pcap --output /tmp/network-lab.pcap")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="새로 만들 PCAP 파일 경로")
    args = parser.parse_args()
    if args.output:
        print(f"PCAP: wrote synthetic capture to {write_capture(args.output)}")
    else:
        demo()


if __name__ == "__main__":
    main()
