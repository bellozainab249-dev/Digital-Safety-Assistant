import socket
def grab_banner(ip, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((ip, port))

        # ✅ Send request for HTTP
        if port == 80:
            sock.send(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")

        banner = sock.recv(1024).decode().strip()
        sock.close()

        return banner

    except:
        return None