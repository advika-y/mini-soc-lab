from database import conn, lock

def generate_report():
    with lock:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM alerts").fetchall()

    print("\n===== INCIDENT REPORT =====")
    print(f"Total Alerts: {len(rows)}")

    ddos = sum(1 for r in rows if r[2] == "DDOS")
    scans = sum(1 for r in rows if r[2] == "PORT_SCAN")

    print(f"DDoS Attacks: {ddos}")
    print(f"Port Scans: {scans}")