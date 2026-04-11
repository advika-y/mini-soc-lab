from report import generate_report
from responder import unblock_ip
from utils import is_valid_ip, sanitize_ip

def start_cli():
    while True:
        cmd = input("SOC> ")

        if cmd == "report":
            generate_report()

        elif cmd.startswith("unblock"):
            parts = cmd.split()

            if len(parts) != 2:
                print("[ERROR] Usage: unblock <ip>")
                continue

            ip = sanitize_ip(parts[1])

            if not is_valid_ip(ip):
                print("[ERROR] Invalid IP address")
                continue

            unblock_ip(ip)

        elif cmd == "exit":
            break