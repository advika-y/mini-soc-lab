from collections import defaultdict, deque
from typing import Optional
import ipaddress
import statistics
import time
from config import *
from logger import log_alert
from responder import block_ip
from threat_intel import is_malicious
from dashboard import update_dashboard, log_alert_event
from soc_types import Alert
from utils import check_payload, get_location, is_valid_ip, sanitize_ip
from scapy.packet import Packet

# Pre-compile CIDR ranges once at startup. Per-packet checks are then O(n)
# membership tests against already-parsed objects rather than repeated string parsing.
_WHITELIST_NETWORKS = [ipaddress.ip_network(cidr) for cidr in WHITELIST_CIDRS]

ip_activity: dict[str, list[tuple[float, int | None]]] = defaultdict(list)
ip_attack_history: dict[str, list[tuple[str, float]]] = defaultdict(list)
alerted_ips: dict[str, float] = {}
global_traffic: deque[tuple[float, str]] = deque(maxlen=10000)
traffic_window: deque[int] = deque(maxlen=50)
ip_reputation: dict[str, int] = defaultdict(int)
ip_offense_count: dict[str, int] = defaultdict(int)

# Minimum gap between repeated alerts for the same IP to prevent log flooding.
ALERT_TTL = 300


def is_whitelisted(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in net for net in _WHITELIST_NETWORKS)
    except ValueError:
        return False


def update_traffic(count: int) -> None:
    traffic_window.append(count)

def is_anomaly(current_count: int) -> bool:
    if len(traffic_window) < 10:
        return False
    try:
        mean = statistics.mean(traffic_window)
        stdev = statistics.stdev(traffic_window)
    except statistics.StatisticsError:
        return False
    if stdev == 0:
        return False
    return (current_count - mean) / stdev > 2.5


def classify_attack(records: list[tuple[float, int | None]], ports: set[int]) -> str:
    if len(ports) > PORT_SCAN_THRESHOLD:
        return "PORT_SCAN"
    if len(records) > REQUEST_THRESHOLD:
        return "DDOS"
    return "NORMAL"


def correlate(ip: str, attack_type: str) -> bool:
    """Return True if this IP has used more than one distinct attack type in the last 10 minutes."""
    now = time.time()
    ip_attack_history[ip].append((attack_type, now))
    ip_attack_history[ip] = [
        (a, t) for (a, t) in ip_attack_history[ip] if now - t < 600
    ]
    return len(set(a for a, _ in ip_attack_history[ip])) > 1


def process_packet(packet: Packet) -> None:
    from scapy.layers.inet import IP, TCP, UDP

    if not packet.haslayer(IP):
        return

    src_ip = sanitize_ip(packet[IP].src)

    if not is_valid_ip(src_ip):
        return

    if is_whitelisted(src_ip):
        return

    if is_malicious(src_ip):
        log_alert(_make_alert(src_ip, "THREAT_INTEL", 10, "Unknown", "BLOCKED"))
        block_ip(src_ip)
        return

    update_dashboard(src_ip)

    timestamp = time.time()
    port: Optional[int] = None
    if packet.haslayer(TCP):
        port = packet[TCP].dport
    elif packet.haslayer(UDP):
        port = packet[UDP].dport

    global_traffic.append((timestamp, src_ip))
    ip_activity[src_ip].append((timestamp, port))

    analyze(src_ip, packet)


def detect_slow_attack(ip: str) -> bool:
    """Detect attacks that spread requests over a long window to evade rate limits."""
    history = ip_activity[ip]
    if len(history) < 10:
        return False
    time_span = history[-1][0] - history[0][0]
    return time_span > TIME_WINDOW and len(history) > (BASELINE * 1.5)


def detect_distributed_attack() -> tuple[bool, set[str]]:
    """Return (True, ip_set) if traffic matches a distributed attack pattern."""
    current_time = time.time()
    recent = [ip for (t, ip) in global_traffic if current_time - t < TIME_WINDOW]
    unique_ips = set(recent)
    if not unique_ips:
        return False, set()
    if len(unique_ips) > 20 and len(recent) / len(unique_ips) > 10:
        return True, unique_ips
    return False, set()


def calculate_score(
    ip: str,
    records: list,
    attack_type: str,
    payload_flag: bool,
    slow_attack: bool,
    distributed: bool,
) -> int:
    score = 0
    if len(records) > REQUEST_THRESHOLD:
        score += 4
    if attack_type == "PORT_SCAN":
        score += 3
    if attack_type == "DDOS":
        score += 5
    if payload_flag:
        score += 4

    current_count = len([s for (t, s) in global_traffic if time.time() - t < TIME_WINDOW])
    update_traffic(current_count)

    if is_anomaly(current_count):
        score += 3
    if slow_attack:
        score += 3
    if distributed:
        score += 4

    return min(score, 15)


def get_block_duration(ip: str, score: int) -> int:
    offenses = ip_offense_count[ip]
    if score >= 10:
        return 600
    if offenses == 0:
        return 30
    if offenses == 1:
        return 120
    return 300


def should_alert(ip: str) -> bool:
    now = time.time()
    if ip in alerted_ips and now - alerted_ips[ip] < ALERT_TTL:
        return False
    alerted_ips[ip] = now
    return True


def _make_alert(ip: str, attack_type: str, score: int, country: str, action: str) -> Alert:
    return {
        "ip": ip,
        "type": attack_type,
        "score": score,
        "country": country,
        "action": action,
        "timestamp": int(time.time()),
    }


def analyze(ip: str, packet: Packet) -> None:
    current_time = time.time()
    country = get_location(ip)
    alert_allowed = should_alert(ip)

    ip_activity[ip] = [
        (t, p) for (t, p) in ip_activity[ip] if current_time - t < TIME_WINDOW
    ]

    records = ip_activity[ip]
    ports = set(p for (_, p) in records if p is not None)

    attack_type = classify_attack(records, ports)
    payload_flag = check_payload(packet)
    slow_attack = detect_slow_attack(ip)
    distributed, _ = detect_distributed_attack()

    score = calculate_score(ip, records, attack_type, payload_flag, slow_attack, distributed)

    ip_reputation[ip] = min(ip_reputation[ip] + score, 100)

    if ip_reputation[ip] > 15 and alert_allowed:
        log_alert(_make_alert(ip, attack_type, score, country, "Repeat Offender Detected"))

    if slow_attack and alert_allowed:
        log_alert(_make_alert(ip, attack_type, score, country, "Stealthy Attack Detected"))

    if distributed and alert_allowed:
        log_alert(_make_alert(ip, attack_type, score, country, "Distributed Attack Detected"))

    if score > 0 and (score >= BLOCK_THRESHOLD or ip_reputation[ip] > 20):
        log_alert(_make_alert(ip, attack_type, score, country, "BLOCKED"))
        log_alert_event()
        block_ip(ip, get_block_duration(ip, score))
        ip_offense_count[ip] += 1
    elif score >= ALERT_THRESHOLD and alert_allowed:
        log_alert(_make_alert(ip, attack_type, score, country, "ALERT"))
        log_alert_event()

    if correlate(ip, attack_type) and alert_allowed:
        log_alert(_make_alert(ip, attack_type, score, country, "Multi-Stage Attack Detected"))
