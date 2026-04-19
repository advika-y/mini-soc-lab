from scapy.all import sniff
from detector import process_packet
from scapy.packet import Packet

def start_sniffing():
    print("[*] Starting packet capture...\n")
    sniff(filter="ip", prn=process_packet, store=False)