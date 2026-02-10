import os, socket, sys, time

def wait(host: str, port: int, timeout_s: float) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    timeout_s = float(sys.argv[3]) if len(sys.argv) > 3 else float(os.getenv("TIMEOUT_S", "20"))
    wait(host, port, timeout_s)
