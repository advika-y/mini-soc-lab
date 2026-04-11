import requests
import ipaddress

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def sanitize_ip(ip: str) -> str:
    if not isinstance(ip, str):
        return ""

    return ip.strip().replace("\n", "").replace("\r", "").replace("\t", "")

cache = {}

def get_location(ip):
    # Step 1: Validate IP before API call
    if not is_valid_ip(ip):
        return "Unknown"

    # Step 2: Check cache
    if ip in cache:
        return cache[ip]

    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}",
            timeout=2
        )

        if response.status_code != 200:
            return "Unknown"

        data = response.json()
        country = data.get("country", "Unknown")

        cache[ip] = country
        return country

    except requests.exceptions.RequestException:
        return "Unknown"

def check_payload(packet):
    from scapy.packet import Raw

    suspicious_keywords = ["malware", "exploit", "attack", "trojan", "virus"]

    if packet.haslayer(Raw):
        try:
            payload = packet[Raw].load.decode(errors="ignore").lower()

            # Limit payload size (prevent abuse)
            payload = payload[:500]

            for keyword in suspicious_keywords:
                if keyword in payload:
                    return True

        except Exception:
            return False

    return False