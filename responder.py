import subprocess
import threading
import time
from utils import is_valid_ip, sanitize_ip
from database import conn, lock


def block_ip(ip: str, duration: int = 30) -> None:
    ip = sanitize_ip(ip)

    if not is_valid_ip(ip):
        print(f"[WARNING] Invalid IP attempt blocked: {ip}")
        return

    unblock_time = int(time.time()) + duration

    with lock:
        cursor = conn.cursor()
        existing = cursor.execute(
            "SELECT ip FROM blocked_ips WHERE ip=?", (ip,)
        ).fetchone()

    # Skip if already tracked — avoids stacking multiple unblock timers for the same IP.
    if existing:
        print(f"[INFO] IP already blocked: {ip}")
        return

    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", f"name=Block_{ip}"],
            capture_output=True, text=True,
        )

        result = subprocess.run(
            [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=Block_{ip}", "dir=in", "action=block", f"remoteip={ip}",
            ],
            capture_output=True, text=True, timeout=5,
        )
  
    except (subprocess.SubprocessError, OSError) as e:
        print(f"[ERROR] Firewall command failed: {e}")
        return
    with lock:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO blocked_ips (ip, unblock_time) VALUES (?, ?)",
            (ip, unblock_time),
        )
        conn.commit()
    threading.Timer(duration, unblock_ip, args=[ip]).start()
    if result.returncode != 0:
        print(f"[WARNING] Firewall rule failed (no admin?): {result.stderr}")
        print(f"[INFO] IP {ip} logged as blocked in DB anyway")
    else:
        print(f"[ACTION] Successfully blocked IP: {ip} for {duration} seconds")

def unblock_ip(ip: str) -> None:
    ip = sanitize_ip(ip)

    if not is_valid_ip(ip):
        return

    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", f"name=Block_{ip}"],
            capture_output=True, text=True, timeout=5,
        )

        # netsh outputs "No rules match" to stdout, not stderr.
        if "No rules match" in result.stdout:
            print(f"[INFO] No firewall rule found for {ip}, already clean")
        elif result.returncode == 0:
            print(f"[ACTION] Unblocked IP: {ip}")
        else:
            print(f"[ERROR] Unblock failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print(f"[WARNING] Unblock timeout for IP: {ip}")

    # Always remove from DB even if the firewall command failed,
    # so the IP does not remain permanently stuck in the blocked list.
    with lock:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blocked_ips WHERE ip=?", (ip,))
        conn.commit()


def restore_blocks() -> None:
    """Re-schedule unblock timers for IPs that were blocked before the process restarted."""
    now = int(time.time())

    with lock:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT ip, unblock_time FROM blocked_ips").fetchall()

    for ip, unblock_time in rows:
        if unblock_time is None:
            unblock_ip(ip)
            continue
        remaining = unblock_time - now
        if remaining > 0:
            print(f"[INFO] Restoring block for {ip}, remaining {remaining}s")
            threading.Timer(remaining, unblock_ip, args=[ip]).start()
        else:
            unblock_ip(ip)


restore_blocks()
