"""데모 서버의 수명과 대기 시간을 제한하는 공통 코드."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import socket

HOST = "127.0.0.1"
TIMEOUT = 3


@contextmanager
def tcp_server(handler, connections=1):
    """이미 listen한 임시 포트를 전달하고 정해진 연결만 처리한다."""
    if not 1 <= connections <= 16:
        raise ValueError("데모는 1~16개 연결만 처리합니다")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind((HOST, 0))
        listener.listen(connections)
        listener.settimeout(TIMEOUT)

        def serve():
            for _ in range(connections):
                connection, _ = listener.accept()
                with connection:
                    connection.settimeout(TIMEOUT)
                    handler(connection)

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(serve)
            try:
                yield listener.getsockname()[1]
            finally:
                # 서버 예외를 숨기지 않는다. accept/recv도 자체 timeout이 있다.
                future.result(timeout=TIMEOUT * connections + 1)
