from colorama import Fore, Style, init
from datetime import datetime
from database import conn, lock

init(autoreset=True)

def log_alert(alert):
    readable_time = datetime.fromtimestamp(alert["timestamp"])

    message = f"{alert['action']} | {alert['type']} | {alert['ip']} | Score: {alert['score']} | {alert['country']}"

    if alert["action"] == "BLOCKED":
        color = Fore.RED
    elif alert["action"] == "ALERT":
        color = Fore.YELLOW
    else:
        color = Fore.GREEN

    print(color + f"{readable_time} | {message}" + Style.RESET_ALL)

    with lock:
        cursor = conn.cursor()
        cursor.execute("""
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
        if alert["action"] == "BLOCKED":
            cursor.execute(
                "INSERT OR IGNORE INTO blocked_ips (ip) VALUES (?)",
                (alert["ip"],)
            )
        conn.commit()