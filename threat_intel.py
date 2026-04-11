import random

BLACKLIST = {
    "10.0.0.66",
    "192.168.1.200",
    "8.8.8.8"
}

def is_malicious(ip):
    return ip in BLACKLIST

def simulate_feed_update():
    if random.random() < 0.01:
        print("[THREAT INTEL] Feed updated")