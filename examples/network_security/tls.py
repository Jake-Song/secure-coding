"""임시 CA와 localhost 인증서로 실제 TLS 인증 성공/실패를 비교한다."""
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import tempfile

from .common import HOST, TIMEOUT, tcp_server
from .framing import encode_frame, recv_frame


def create_certificates(parent):
    if shutil.which("openssl") is None:
        raise RuntimeError("TLS 실습에는 openssl 실행 파일이 필요합니다")
    directory = Path(parent) / "pki"
    directory.mkdir(mode=0o700)  # 기존 파일을 덮어쓰지 않는다.

    def run(*args):
        result = subprocess.run(["openssl", *args], cwd=directory, capture_output=True,
                                text=True, timeout=20)
        if result.returncode:
            raise RuntimeError(f"OpenSSL certificate generation failed: {result.stderr}")

    run("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-sha256", "-days", "2",
        "-subj", "/CN=Network Lab Temporary CA", "-keyout", "ca.key", "-out", "ca.crt",
        "-addext", "basicConstraints=critical,CA:TRUE",
        "-addext", "keyUsage=critical,keyCertSign,cRLSign")
    run("req", "-new", "-newkey", "rsa:2048", "-nodes", "-sha256", "-subj", "/CN=localhost",
        "-keyout", "server.key", "-out", "server.csr")
    (directory / "extensions.cnf").write_text(
        "basicConstraints=critical,CA:FALSE\n"
        "keyUsage=critical,digitalSignature,keyEncipherment\n"
        "extendedKeyUsage=serverAuth\n"
        "subjectAltName=DNS:localhost\n"
        "subjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n")
    run("x509", "-req", "-in", "server.csr", "-CA", "ca.crt", "-CAkey", "ca.key",
        "-set_serial", "2", "-days", "2", "-sha256", "-extfile", "extensions.cnf",
        "-out", "server.crt")
    for name in ("ca.key", "server.key"):
        (directory / name).chmod(0o600)
    return directory


def server_context(directory):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(Path(directory) / "server.crt", Path(directory) / "server.key")
    return context


def client_context(cafile=None):
    context = ssl.create_default_context(cafile=cafile)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    # 교육용 키가 환경 변수에 의해 별도 파일로 기록되지 않게 한다.
    context.keylog_filename = None
    return context


def exchange(server, client, hostname="localhost", payload=b"hello over TLS"):
    def echo(connection):
        try:
            with server.wrap_socket(connection, server_side=True) as secure:
                secure.sendall(encode_frame(recv_frame(secure)))
        except ssl.SSLError:
            # 클라이언트가 인증서를 거절하는 경우의 TLS alert는 예상된 결과다.
            # 클라이언트 측 검증 예외는 아래 호출자에게 그대로 전달한다.
            pass

    with tcp_server(echo) as port:
        with socket.create_connection((HOST, port), TIMEOUT) as connection:
            with client.wrap_socket(connection, server_hostname=hostname) as secure:
                secure.sendall(encode_frame(payload))
                return recv_frame(secure), secure.version()


def demo():
    with tempfile.TemporaryDirectory(prefix="network-tls-") as parent:
        directory = create_certificates(parent)
        server = server_context(directory)
        trusted = client_context(directory / "ca.crt")
        result, version = exchange(server, trusted)
        if result != b"hello over TLS":
            raise RuntimeError("TLS round trip mismatch")
        print(f"TLS: trusted CA + localhost -> accepted ({version})")
        for label, client, hostname in (
            ("untrusted CA", client_context(), "localhost"),
            ("hostname mismatch", trusted, "wrong.test"),
        ):
            try:
                exchange(server, client, hostname)
            except ssl.SSLCertVerificationError:
                print(f"TLS: {label} -> certificate rejected")
            else:
                raise RuntimeError(f"TLS: {label} unexpectedly accepted")


if __name__ == "__main__":
    demo()
