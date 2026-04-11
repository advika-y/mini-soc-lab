import matplotlib.pyplot as plt
from collections import defaultdict
import time

ip_counter = defaultdict(int)
alert_count = []

def update_dashboard(ip):
    ip_counter[ip] += 1

def log_alert_event():
    alert_count.append(time.time())

def show_dashboard():
    plt.figure(figsize=(10, 6))  # 👈 better size

    while True:
        plt.clf()

        # 🔹 Top IPs (limit to top 5)
        sorted_ips = sorted(ip_counter.items(), key=lambda x: x[1], reverse=True)[:5]

        ips = [ip for ip, _ in sorted_ips]
        counts = [count for _, count in sorted_ips]

        plt.subplot(2, 1, 1)
        plt.title("Top Active IPs")
        plt.bar(ips, counts)
        plt.xticks(rotation=30)

        # 🔹 Alerts over time (last 20)
        recent_alerts = alert_count[-20:]

        plt.subplot(2, 1, 2)
        plt.title("Recent Alert Activity")
        plt.plot(recent_alerts)

        plt.tight_layout()
        plt.pause(1)