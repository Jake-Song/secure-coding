"""작은 입력을 에코 서버에 전송하고 EOF까지 수신한다."""
import argparse
import socket


def exchange(data, port=9000):
    # 교육용 작은 메시지: sendall 후 수신하는 방식은 무제한 스트림용이 아니다.
    if len(data) > 64 * 1024:
        raise ValueError("실습 메시지는 64 KiB 이하로 제한합니다")
    with socket.create_connection(("127.0.0.1", port), timeout=10) as connection:
        connection.sendall(data)
        connection.shutdown(socket.SHUT_WR)
        chunks = []
        while chunk := connection.recv(4096):
            chunks.append(chunk)
        return b"".join(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="?", default="안녕하세요")
    parser.add_argument("--port", type=int, default=9000)
    args = parser.parse_args()
    print(exchange(args.message.encode(), args.port).decode())
