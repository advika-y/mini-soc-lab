from scapy.all import sniff
from detector import process_packet

def start_sniffing():
    print("[*] Starting packet capture...\n")
    sniff(filter="ip", prn=process_packet, store=False)