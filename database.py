import sqlite3
import threading
# SQLite connection is shared across threads.
# All DB operations must acquire `lock` before using `conn`.
conn = sqlite3.connect("soc.db", check_same_thread=False)
lock = threading.Lock()

with lock:
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS blocked_ips (
        ip TEXT PRIMARY KEY,
        unblock_time INTEGER
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        type TEXT,
        score INTEGER,
        country TEXT,
        action TEXT,
        timestamp INTEGER
    )""")

    conn.commit()