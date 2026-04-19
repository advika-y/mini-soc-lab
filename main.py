from sniffer import start_sniffing
from dashboard import show_dashboard
from cli import start_cli
from responder import restore_blocks
import threading
# NOTE: This matplotlib dashboard is for local debugging only.
# The primary production dashboard is the React frontend.
if __name__ == "__main__":
    restore_blocks()
    threading.Thread(target=show_dashboard, daemon=True).start()
    threading.Thread(target=start_cli, daemon=True).start()
    start_sniffing()