import socket
from concurrent.futures import ThreadPoolExecutor

port_info = {
    80: ("HTTP",
         "Web traffic (not encrypted). Browsers use this for websites.",
         "LOW",
         "Safe for local networks. Prefer HTTPS when possible."),

    443: ("HTTPS",
          "Secure web traffic using encryption.",
          "SAFE",
          "No action needed. This is the secure standard."),

    53: ("DNS",
         "Resolves domain names like google.com into IP addresses.",
         "LOW",
         "Essential for internet. No action needed."),

    22: ("SSH",
         "Allows remote login to the system.",
         "HIGH",
         "Disable if not needed or restrict access with firewall."),

    445: ("SMB",
          "Windows file sharing service. Enables file & printer sharing on the network.",
          "HIGH",
          "Normal for home use. Ensure firewall is enabled and not exposed to the internet."),

    135: ("RPC",
          "Windows internal communication service used by system processes.",
          "MEDIUM",
          "Normal. Should never be exposed outside your network."),

    139: ("NetBIOS",
          "Legacy Windows file sharing protocol.",
          "HIGH",
          "Outdated. Disable if possible."),

    902: ("VMware",
          "Used by virtual machines running locally.",
          "LOW",
          "Expected if using VMware."),

    912: ("VMware",
          "Used by virtual machines running locally.",
          "LOW",
          "Expected if using VMware."),
}

def check_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)

    result = sock.connect_ex((target, port))
    sock.close()

    return port if result == 0 else None


def scan(target, mode):

    if mode == "basic":
        ports = range(20, 1025)
    else:
        ports = range(20, 10001)

    results = []

    # Check every port at once instead of one at a time. Most ports
    # are closed and just sit waiting for the timeout, so threading
    # this cuts a 1000-port scan from ~minutes down to a few seconds.
    with ThreadPoolExecutor(max_workers=200) as executor:
        for result in executor.map(lambda p: check_port(target, p), ports):
            if result:
                results.append(result)

    results.sort()
    return results