import sqlite3
import threading
# SQLite connection is shared across threads.
# All DB operations must acquire `lock` before using `conn`.
conn = sqlite3.connect("soc.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
lock = threading.Lock()

def db_execute(query: str, params: tuple = (), fetch: bool = False) -> list | None:
    with lock:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return None
    

db_execute("""CREATE TABLE IF NOT EXISTS blocked_ips (
        ip TEXT PRIMARY KEY,
        unblock_time INTEGER
    )""")

db_execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        type TEXT,
        score INTEGER,
        country TEXT,
        action TEXT,
        timestamp INTEGER
    )""")