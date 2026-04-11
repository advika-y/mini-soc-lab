from collections import defaultdict
import threading
import time
from config import *
from logger import log_alert
from responder import block_ip
from threat_intel import is_malicious, simulate_feed_update
from dashboard import update_dashboard, log_alert_event
from utils import check_payload
from utils import is_valid_ip, sanitize_ip
import statistics
from collections import deque

ip_activity = defaultdict(list)
ip_attack_history = {}
alerted_ips = {}
ip_request_history = defaultdict(list)
global_traffic = []
traffic_window = deque(maxlen=50)

def update_traffic(count):
    traffic_window.append(count)

ip_reputation = defaultdict(int)
ip_offense_count = defaultdict(int)

def is_anomaly(current_count):
    if len(traffic_window) < 10:
        return False

    try:
        mean = statistics.mean(traffic_window)
        stdev = statistics.stdev(traffic_window)
    except statistics.StatisticsError:
        return False

    if stdev == 0:
        return False

    z_score = (current_count - mean) / stdev

    return z_score > 2.5

def classify_attack(records, ports):
    if len(ports) > PORT_SCAN_THRESHOLD:
        return "PORT_SCAN"
    if len(records) > REQUEST_THRESHOLD:
        return "DDOS"
    return "NORMAL"

def correlate(ip, attack_type):
    now = time.time()

    if ip not in ip_attack_history:
        ip_attack_history[ip] = []

    ip_attack_history[ip].append((attack_type, now))

    # keep only last 10 minutes
    ip_attack_history[ip] = [
        (a, t) for (a, t) in ip_attack_history[ip]
        if now - t < 600
    ]

    unique_attacks = set(a for a, _ in ip_attack_history[ip])

    return len(unique_attacks) > 1

def process_packet(packet):
    from scapy.layers.inet import IP, TCP, UDP

    if packet.haslayer(IP):
        raw_ip = packet[IP].src
        src_ip = sanitize_ip(raw_ip)
        
        if not is_valid_ip(src_ip):
            return

        # 🔹 Whitelist
        if src_ip in WHITELIST:
            return

        # 🔹 Threat intel
        if is_malicious(src_ip):
            alert = {
                "ip": src_ip,
                "type": "THREAT_INTEL",
                "score": 10,
                "country": "Unknown",
                "action": "BLOCKED",
                "timestamp": int(time.time())
            }
            log_alert(alert)
            
            block_ip(src_ip)
            return

        simulate_feed_update()
        update_dashboard(src_ip)

        timestamp = time.time()
        
        port = None
        if packet.haslayer(TCP):
            port = packet[TCP].dport
        elif packet.haslayer(UDP):
            port = packet[UDP].dport

        global_traffic.append((time.time(), src_ip))
        ip_activity[src_ip].append((timestamp, port))
        
        analyze(src_ip, packet)

def detect_slow_attack(ip):
    history = ip_activity[ip]

    if len(history) < 10:
        return False

    time_span = history[-1][0] - history[0][0]

    # Slow scan: many requests spread over time
    if time_span > TIME_WINDOW and len(history) > (BASELINE * 1.5):
        return True

    return False

def detect_distributed_attack():
    current_time = time.time()

    recent = [
        ip for (t, ip) in global_traffic
        if current_time - t < TIME_WINDOW
    ]

    unique_ips = set(recent)
    total_requests = len(recent)

    if len(unique_ips) > 20 and total_requests / len(unique_ips) > 10:
        return True, unique_ips

    return False, set()

def calculate_score(ip, records, attack_type, payload_flag, slow_attack, distributed):
    score = 0

    if len(records) > REQUEST_THRESHOLD:
        score += 4

    if attack_type == "PORT_SCAN":
        score += 3

    if attack_type == "DDOS":
        score += 5

    if payload_flag:
        score += 4
    
    current_count = len([
        src for (t, src) in global_traffic
        if time.time() - t < TIME_WINDOW
    ])
    update_traffic(current_count)

    if is_anomaly(current_count):
        score += 3

    if slow_attack:
        score += 3

    if distributed:
        score += 4

    return min(score, 15)

def get_block_duration(ip, score):
    offenses = ip_offense_count[ip]

    if score >= 10:
        return 600  # 10 minutes

    if offenses == 0:
        return 30   # first time
    elif offenses == 1:
        return 120  # second time
    elif offenses >= 2:
        return 300  # repeat attacker

    return 60

ALERT_TTL = 300  # 5 minutes

def should_alert(ip):
    now = time.time()

    if ip in alerted_ips:
        if now - alerted_ips[ip] < ALERT_TTL:
            return False

    alerted_ips[ip] = now
    return True

def analyze(ip, packet):
    current_time = time.time()
    country = "Unknown"
    alert_allowed = should_alert(ip)

    ip_activity[ip] = [
        (t, p) for (t, p) in ip_activity[ip]
        if current_time - t < TIME_WINDOW
    ]

    records = ip_activity[ip]
    ports = set(p for (_, p) in records if p is not None)

    payload_flag = check_payload(packet)
    attack_type = classify_attack(records, ports)

    slow_attack = detect_slow_attack(ip)
    distributed, attacker_ips = detect_distributed_attack()

    score = calculate_score(ip, records, attack_type, payload_flag, slow_attack, distributed)

    ip_reputation[ip] += score

    if ip_reputation[ip] > 15 and alert_allowed:
        alert = {
            "ip": ip,
            "type": attack_type,
            "score": score,
            "country": country,
            "action": "Repeat Offender Detected",
            "timestamp": int(time.time())
        }
        
        log_alert(alert)

    if slow_attack and alert_allowed:
        alert = {
            "ip": ip,
            "type": attack_type,
            "score": score,
            "country": country,
            "action": "Stealthy Attack Detected",
            "timestamp": int(time.time())
        }
        
        log_alert(alert)

    if distributed and alert_allowed:
        alert = {
            "ip": ip,
            "type": attack_type,
            "score": score,
            "country": country,
            "action": "Distributed Attack Detected",
            "timestamp": int(time.time())
        }
        
        log_alert(alert)
    if score >= BLOCK_THRESHOLD or (ip_reputation[ip] > 20 and score > 0):
        country = "Unknown"

        alert = {
            "ip": ip,
            "type": attack_type,
            "score": score,
            "country": country,
            "action": "BLOCKED",
            "timestamp": int(time.time())
        }
        
        log_alert(alert)

        log_alert_event()
        duration = get_block_duration(ip, score)
        block_ip(ip, duration)
        ip_offense_count[ip] += 1

    elif score >= ALERT_THRESHOLD and alert_allowed:

        country = "Unknown"

        alert = {
            "ip": ip,
            "type": attack_type,
            "score": score,
            "country": country,
            "action": "ALERT",
            "timestamp": int(time.time())
            }
        
        log_alert(alert)

        log_alert_event()

    if correlate(ip, attack_type) and alert_allowed:
        alert = {
            "ip": ip,
            "type": attack_type,
            "score": score,
            "country": country,
            "action": "Multi-Stage Attack Detected",
            "timestamp": int(time.time())
        }
        
        log_alert(alert)

    global_traffic[:] = [
        (t, ip) for (t, ip) in global_traffic
        if time.time() - t < TIME_WINDOW
    ]
