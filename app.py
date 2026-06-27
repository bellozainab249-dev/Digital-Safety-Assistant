"""
Digital Safety Assistant — Flask backend.

This wraps your existing scanner.py / network.py / banner.py modules
(unchanged) with a small web layer: a dashboard page and a JSON API
that the dashboard calls to run scans and render results.
"""

from flask import Flask, jsonify, render_template
import socket
import datetime
import threading

from scanner import scan, port_info
from network import scan_network
from banner import grab_banner

app = Flask(__name__)

DEVICES_FILE = "devices.txt"
IMPORTANT_PORTS = [22, 80, 443]

# Simple in-memory lock so two scans can't run on top of each other
scan_lock = threading.Lock()
last_result = None  # cache of the most recent scan, served by /api/last


def get_device_name(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "Unknown Device"


def load_old_devices():
    try:
        with open(DEVICES_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_devices(devices):
    with open(DEVICES_FILE, "w") as f:
        for d in devices:
            f.write(d.strip() + "\n")


def run_scan(mode="basic"):
    old_devices = load_old_devices()
    devices = scan_network()
    current_devices = set(devices)

    # Only treat devices as "new" if we actually had a previous baseline
    new_devices = sorted(current_devices - old_devices) if old_devices else []
    missing_devices = sorted(old_devices - current_devices) if old_devices else []

    save_devices(devices)

    device_results = []
    total_ports = 0
    high_risk = 0

    for device in devices:
        name = get_device_name(device)
        ports = scan(device, mode)

        device_entry = {"ip": device, "name": name, "ports": []}

        for port in ports:
            total_ports += 1
            entry = {"port": port}

            if port in port_info:
                pname, description, risk, advice = port_info[port]
                entry.update(
                    {
                        "service": pname,
                        "description": description,
                        "risk": risk,
                        "advice": advice,
                    }
                )
                if risk == "HIGH":
                    high_risk += 1
            else:
                entry.update(
                    {
                        "service": "Unknown service",
                        "description": "This port doesn't match a known service in our database.",
                        "risk": "UNKNOWN",
                        "advice": "Worth investigating if you don't recognize it.",
                    }
                )

            if port in IMPORTANT_PORTS:
                banner = grab_banner(device, port)
                entry["banner"] = banner.split("\n")[0] if banner else None

            device_entry["ports"].append(entry)

        device_results.append(device_entry)

    if high_risk >= 3:
        overall_risk = "HIGH"
    elif high_risk >= 1:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "devices": device_results,
        "alerts": {
            "new": new_devices,
            "missing": missing_devices,
            "has_baseline": bool(old_devices),
        },
        "summary": {
            "device_count": len(devices),
            "total_ports": total_ports,
            "high_risk": high_risk,
            "overall_risk": overall_risk,
        },
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan")
def api_scan():
    """Runs a fresh scan. Blocks if one is already in progress."""
    global last_result
    if not scan_lock.acquire(blocking=False):
        return jsonify({"error": "A scan is already in progress."}), 409
    try:
        last_result = run_scan()
        return jsonify(last_result)
    finally:
        scan_lock.release()


@app.route("/api/last")
def api_last():
    """Returns the most recent cached scan without re-scanning."""
    if last_result is None:
        return jsonify({"error": "No scan has been run yet."}), 404
    return jsonify(last_result)


if __name__ == "__main__":
    app.run(debug=True)
