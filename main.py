from sniffer import start_sniffing
from dashboard import show_dashboard
from cli import start_cli
import threading

if __name__ == "__main__":
    threading.Thread(target=show_dashboard, daemon=True).start()
    threading.Thread(target=start_cli, daemon=True).start()
    start_sniffing()