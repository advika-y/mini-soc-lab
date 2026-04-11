def generate_report():
    try:
        with open("alerts.log", "r") as f:
            lines = f.readlines()

        print("\n===== INCIDENT REPORT =====")
        print(f"Total Alerts: {len(lines)}")

        ddos = sum("DDOS" in l for l in lines)
        scans = sum("PORT_SCAN" in l for l in lines)

        print(f"DDoS Attacks: {ddos}")
        print(f"Port Scans: {scans}")

    except FileNotFoundError:
        print("No logs found.")