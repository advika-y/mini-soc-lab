from colorama import Fore, Style, init
from datetime import datetime
from database import db_execute
from soc_types import Alert

init(autoreset=True)

def log_alert(alert: Alert) -> None:
    readable_time = datetime.fromtimestamp(alert["timestamp"])

    message = f"{alert['action']} | {alert['type']} | {alert['ip']} | Score: {alert['score']} | {alert['country']}"

    if alert["action"] == "BLOCKED":
        color = Fore.RED
    elif alert["action"] == "ALERT":
        color = Fore.YELLOW
    else:
        color = Fore.GREEN

    print(color + f"{readable_time} | {message}" + Style.RESET_ALL)

    db_execute("""
            INSERT INTO alerts (ip, type, score, country, action, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            alert["ip"],
            alert["type"],
            alert["score"],
            alert["country"],
            alert["action"],
            alert["timestamp"]
        ))