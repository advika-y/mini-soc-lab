import random

# Static feed: IPs flagged at startup from a known-bad list.
# Do not add RFC 1918 or public infrastructure addresses here.
_STATIC_FEED: set[str] = set()

# Dynamic feed: IPs added at runtime via add_to_feed() or a live ingestion pipeline.
_DYNAMIC_FEED: set[str] = set()


def is_malicious(ip: str) -> bool:
    return ip in _STATIC_FEED or ip in _DYNAMIC_FEED


def add_to_feed(ip: str) -> None:
    """Add an IP to the runtime threat feed."""
    _DYNAMIC_FEED.add(ip)

#TODO: Replace with real threat intel feed (MISP, AbuseIPDB, etc.)
def simulate_feed_update() -> None:
    """Placeholder for a real periodic threat feed refresh."""
    if random.random() < 0.01:
        print("[THREAT INTEL] Feed updated")
