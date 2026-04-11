import sqlite3
from database import conn, lock

conn = sqlite3.connect("soc.db")
with lock:
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM alerts").fetchall()

print("\n--- ALERTS ---\n")
for row in rows:
    print(row)