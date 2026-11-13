"""한 연결을 처리한 뒤 종료하는 loopback TCP 에코 서버."""
import argparse
import socket


def serve_once(listener):
    connection, _ = listener.accept()
    with connection:
        connection.settimeout(10)
        while data := connection.recv(4096):
            connection.sendall(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    with socket.socket() as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", args.port))
        listener.listen(1)
        print(f"127.0.0.1:{args.port}에서 한 연결을 기다립니다.", flush=True)
        serve_once(listener)
