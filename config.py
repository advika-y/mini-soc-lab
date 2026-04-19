TIME_WINDOW = 10              # seconds
PORT_SCAN_THRESHOLD = 20     # number of ports
REQUEST_THRESHOLD = 100      # number of packets
WHITELIST_CIDRS = [
    "127.0.0.0/8",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "169.254.0.0/16",  # link-local
    "::1/128"          # IPv6 loopback
]
BASELINE = 50               # for anomaly detection
ALERT_THRESHOLD = 5
BLOCK_THRESHOLD = 8
