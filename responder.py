import subprocess
import threading
import time
from utils import is_valid_ip, sanitize_ip
from database import conn, lock  # ✅ use DB lock (NOT local lock)

# ---------------- BLOCK IP ---------------- #

def block_ip(ip, duration=30):
    ip = sanitize_ip(ip)

    if not is_valid_ip(ip):
        print(f"[WARNING] Invalid IP attempt blocked: {ip}")
        return

    unblock_time = int(time.time()) + duration

    # ✅ DB check with lock + new cursor
    with lock:
        cursor = conn.cursor()
        existing = cursor.execute(
            "SELECT ip FROM blocked_ips WHERE ip=?",
            (ip,)
        ).fetchone()

    # ❌ FIX: do NOT create new timer again
    if existing:
        print(f"[INFO] IP already blocked: {ip}")
        return

    try:
        # Remove old rule (ignore failure)
        subprocess.run([
            "netsh", "advfirewall", "firewall", "delete", "rule",
            f"name=Block_{ip}"
        ], capture_output=True, text=True)

        # Add new block rule
        command = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name=Block_{ip}",
            "dir=in",
            "action=block",
            f"remoteip={ip}"
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            with lock:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO blocked_ips (ip, unblock_time)
                    VALUES (?, ?)
                """, (ip, unblock_time))
                conn.commit()

            print(f"[ACTION] Successfully blocked IP: {ip} for {duration} seconds")

            # ✅ ONLY ONE TIMER
            threading.Timer(duration, unblock_ip, args=[ip]).start()

        else:
            print(f"[ERROR] Firewall rule failed: {result.stderr}")

    except Exception as e:
        print(f"[ERROR] Failed to block IP: {e}")


# ---------------- UNBLOCK IP ---------------- #

def unblock_ip(ip):
    ip = sanitize_ip(ip)

    if not is_valid_ip(ip):
        return

    command = [
        "netsh", "advfirewall", "firewall", "delete", "rule",
        f"name=Block_{ip}"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )

        # ✅ Ignore if rule doesn't exist
        if "No rules match" in result.stderr:
            pass

        elif result.returncode == 0:
            print(f"[ACTION] Unblocked IP: {ip}")

        else:
            print(f"[ERROR] Unblock failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print(f"[WARNING] Unblock timeout for IP: {ip}")

    # ✅ ALWAYS clean DB (even if firewall fails)
    with lock:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blocked_ips WHERE ip=?", (ip,))
        conn.commit()


# ---------------- RESTORE BLOCKS ---------------- #

def restore_blocks():
    now = int(time.time())

    with lock:
        cursor = conn.cursor()
        rows = cursor.execute(
            "SELECT ip, unblock_time FROM blocked_ips"
        ).fetchall()

    for ip, unblock_time in rows:
        remaining = unblock_time - now

        if remaining > 0:
            print(f"[INFO] Restoring block for {ip}, remaining {remaining}s")
            threading.Timer(remaining, unblock_ip, args=[ip]).start()
        else:
            unblock_ip(ip)


# Run on startup
restore_blocks()