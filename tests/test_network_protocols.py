import io
from pathlib import Path
import socket
import struct
import tempfile
import unittest

from examples.network_security import dns, framing, pcap
from examples.network_security.common import HOST, TIMEOUT, tcp_server


class FragmentedReader:
    def __init__(self, data, chunk=1):
        self.stream = io.BytesIO(data)
        self.chunk = chunk

    def recv(self, size):
        return self.stream.read(min(size, self.chunk))


class FramingUnitTests(unittest.TestCase):
    def test_split_header_body_empty_binary_and_limit(self):
        for payload in (b"", "한글".encode(), bytes(range(256)) * 16):
            with self.subTest(size=len(payload)):
                self.assertEqual(framing.recv_frame(FragmentedReader(framing.encode_frame(payload))), payload)

    def test_coalesced_frames_are_consumed_individually(self):
        reader = FragmentedReader(framing.encode_frame(b"first") + framing.encode_frame(b"second"), 100)
        self.assertEqual(framing.recv_frame(reader), b"first")
        self.assertEqual(framing.recv_frame(reader), b"second")

    def test_truncation_and_oversized_prefix(self):
        for wire in (b"", b"\0\0", struct.pack("!I", 5) + b"1234", struct.pack("!I", 0xffffffff)):
            with self.subTest(wire=wire), self.assertRaises(framing.ProtocolError):
                framing.recv_frame(FragmentedReader(wire))
        with self.assertRaises(framing.ProtocolError):
            framing.encode_frame(b"x" * (framing.MAX_FRAME + 1))

    def test_invalid_json_and_utf8_are_protocol_errors(self):
        for data in (b"{", b"\xff", b"[" * 1500):
            with self.subTest(data=data[:8]), self.assertRaises(framing.ProtocolError):
                framing.recv_json(FragmentedReader(framing.encode_frame(data)))


class FramingSocketTests(unittest.TestCase):
    def test_real_tcp_round_trip_and_multiple_frames(self):
        messages = [b"", "네트워크".encode(), bytes(range(256)) * 16]
        for split in (False, True):
            self.assertEqual(framing.exchange_frames(messages, split), messages)

    def test_real_tcp_truncated_body_is_rejected(self):
        observed = []

        def handler(connection):
            try:
                framing.recv_frame(connection)
            except framing.ProtocolError as error:
                observed.append(str(error))

        with tcp_server(handler) as port:
            with socket.create_connection((HOST, port), TIMEOUT) as client:
                client.sendall(struct.pack("!I", 8) + b"short")
                client.shutdown(socket.SHUT_WR)
        self.assertEqual(observed, ["truncated frame"])


class DNSUnitTests(unittest.TestCase):
    def test_query_compressed_answer_and_nxdomain(self):
        for name, expected in (("service.test", HOST), ("SERVICE.TEST.", HOST), ("missing.test", None)):
            with self.subTest(name=name):
                query = dns.make_query(name, ident=1234)
                self.assertEqual(dns.validate_response(dns.make_response(query), query), expected)

    def test_id_name_and_response_bit_must_match(self):
        query = dns.make_query(ident=1234)
        wrong_id = bytearray(dns.make_response(query))
        wrong_id[:2] = struct.pack("!H", 1235)
        wrong_name = dns.make_response(dns.make_query("other.test", ident=1234))
        for response in (bytes(wrong_id), wrong_name, query):
            with self.subTest(response=response), self.assertRaises(framing.ProtocolError):
                dns.validate_response(response, query)

    def test_truncated_cycle_pointer_trailing_and_unsupported(self):
        query = dns.make_query(ident=1)
        cycle = dns.HEADER.pack(1, 0, 1, 0, 0, 0) + b"\xc0\x0c\0\x01\0\x01"
        for packet in (b"", query[:-1], cycle, query + b"\0", dns.make_response(query)[:-1],
                       dns.HEADER.pack(1, 0, 2, 0, 0, 0) + query[12:],
                       query[:2] + b"\x03\x00" + query[4:]):
            with self.subTest(packet=packet), self.assertRaises(framing.ProtocolError):
                dns.parse(packet)
        for packet in (b"\xc0", b"\xc0\xff", b"\x40"):
            with self.subTest(packet=packet), self.assertRaises(framing.ProtocolError):
                dns.read_name(packet, 0)

    def test_label_and_expanded_name_limits(self):
        for name in ("a" * 64 + ".test", "a..test", "가.test", ".".join(["a" * 63] * 4)):
            with self.subTest(name=name), self.assertRaises(framing.ProtocolError):
                dns.make_query(name)
        with self.assertRaises(framing.ProtocolError):
            dns.read_name((b"\x3f" + b"a" * 63) * 4 + b"\0", 0)


class DNSSocketTests(unittest.TestCase):
    def test_local_udp_success_and_nxdomain(self):
        self.assertEqual(dns.lookup("service.test"), HOST)
        self.assertIsNone(dns.lookup("missing.test"))


class PcapTests(unittest.TestCase):
    def test_pcap_lengths_checksums_and_dns_pair(self):
        data = pcap.sample_capture()
        magic, major, minor, zone, sigfigs, snaplen, network = struct.unpack_from("<IHHIIII", data)
        self.assertEqual((magic, major, minor, network), (0xa1b2c3d4, 2, 4, 1))
        offset, payloads, endpoints = 24, [], []
        for index in range(2):
            seconds, micros, captured, original = struct.unpack_from("<IIII", data, offset)
            self.assertEqual(captured, original)
            offset += 16
            packet = data[offset:offset + captured]
            self.assertEqual(len(packet), captured)
            self.assertEqual(packet[12:14], b"\x08\x00")
            endpoints.append((packet[:6], packet[6:12]))
            header, udp = packet[14:34], packet[34:]
            self.assertEqual(pcap.checksum(header), 0)
            self.assertEqual(struct.unpack_from("!H", header, 2)[0], len(packet) - 14)
            udp_length = struct.unpack_from("!H", udp, 4)[0]
            self.assertEqual(udp_length, len(udp))
            pseudo = header[12:20] + struct.pack("!BBH", 0, 17, udp_length)
            self.assertEqual(pcap.checksum(pseudo + udp), 0)
            payloads.append(udp[8:])
            offset += captured
        self.assertEqual(offset, len(data))
        self.assertEqual(endpoints[0], tuple(reversed(endpoints[1])))
        self.assertEqual(dns.validate_response(payloads[1], payloads[0]), HOST)

    def test_export_does_not_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.pcap"
            pcap.write_capture(path)
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                pcap.write_capture(path)
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
