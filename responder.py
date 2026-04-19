import subprocess
import threading
import time
from utils import is_valid_ip, sanitize_ip
from database import db_execute


def block_ip(ip: str, duration: int = 30) -> None:
    ip = sanitize_ip(ip)

    if not is_valid_ip(ip):
        print(f"[WARNING] Invalid IP attempt blocked: {ip}")
        return

    unblock_time = int(time.time()) + duration

    
    existing = db_execute("SELECT ip FROM blocked_ips WHERE ip=?", params=(ip,), fetch=True)

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
        if result.returncode == 0:
            print(f"[ACTION] Successfully blocked IP: {ip} for {duration} seconds")
        else:
            print(f"[WARNING] Firewall rule failed (no admin?): {result.stderr}")
            print(f"[INFO] IP {ip} logged as blocked in DB anyway")
    except (subprocess.SubprocessError, OSError) as e:
        print(f"[ERROR] Firewall command failed: {e}")
        print(f"[INFO] IP {ip} logged as blocked in DB anyway")

    db_execute(
        "INSERT OR REPLACE INTO blocked_ips (ip, unblock_time) VALUES (?, ?)",
        params=(ip, unblock_time)
    )
    threading.Timer(duration, unblock_ip, args=[ip]).start()
    
    
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
    db_execute("DELETE FROM blocked_ips WHERE ip=?", params=(ip,))


def restore_blocks() -> None:
    """Re-schedule unblock timers for IPs that were blocked before the process restarted.

    Call this explicitly from main.py after all modules are loaded — not at import time.
    """
    now = int(time.time())
    rows = db_execute("SELECT ip, unblock_time FROM blocked_ips", fetch=True)

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