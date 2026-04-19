import ipaddress
import requests

_location_cache: dict[str, str] = {}


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


def get_location(ip: str) -> str:
    if not is_valid_ip(ip):
        return "Unknown"

    if ip in _location_cache:
        return _location_cache[ip]

    try:
        response = requests.get(f"https://ipwho.is/{ip}", timeout=2)

        if response.status_code != 200:
            return "Unknown"

        data = response.json()

        # ipwho.is returns {"success": false} for private or unresolvable IPs.
        # Default is False so a missing field does not bypass this check.
        if not data.get("success", False):
            return "Unknown"

        country: str = data.get("country", "Unknown")
        _location_cache[ip] = country
        return country

    except requests.exceptions.RequestException:
        return "Unknown"


def check_payload(packet) -> bool:
    from scapy.packet import Raw

    SUSPICIOUS_KEYWORDS = ("malware", "exploit", "attack", "trojan", "virus")

    if not packet.haslayer(Raw):
        return False

    try:
        payload = packet[Raw].load.decode(errors="ignore").lower()[:500]
        return any(kw in payload for kw in SUSPICIOUS_KEYWORDS)
    except (UnicodeDecodeError, AttributeError):
        return False
