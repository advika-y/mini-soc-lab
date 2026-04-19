from database import db_execute

def generate_report():
    rows = db_execute("SELECT type FROM alerts", fetch=True)

    print("\n===== INCIDENT REPORT =====")
    print(f"Total Alerts: {len(rows)}")

    ddos = sum(1 for r in rows if r[0] == "DDOS")
    scans = sum(1 for r in rows if r[0] == "PORT_SCAN")

    print(f"DDoS Attacks: {ddos}")
    print(f"Port Scans: {scans}")