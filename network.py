
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor

def ping_host(ip):
    response = subprocess.run(
        ["ping", "-n", "1", "-w", "500", ip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if "TTL=" in response.stdout:
        return ip
    return None

def scan_network():

    local_ip = socket.gethostbyname(socket.gethostname())
    base_ip = ".".join(local_ip.split(".")[:3]) + "."

    ips = [base_ip + str(i) for i in range(1, 255)]

    devices = []

    # Ping all 254 addresses at once instead of one at a time.
    # Each ping just sits waiting for a reply or timeout, so this
    # is a great fit for threads even though Python threads don't
    # give true parallel CPU work.
    with ThreadPoolExecutor(max_workers=50) as executor:
        for result in executor.map(ping_host, ips):
            if result:
                devices.append(result)

    return devices
