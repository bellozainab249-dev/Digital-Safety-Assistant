from scanner import scan, port_info
from network import scan_network
from banner import grab_banner
import socket

# ✅ Load previous devices

try:
    with open("devices.txt", "r") as f:
        old_devices = set(line.strip() for line in f.readlines())
except:
    old_devices = set()


# ✅ Get hostname
def get_device_name(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown Device"


print("\n--- Scan Results ---\n")

devices = scan_network()
current_devices = set(devices)

# ✅ Compare devices
new_devices = current_devices - old_devices
missing_devices = old_devices - current_devices

print(f"Devices: {devices}")

# ✅ Show tracking alerts
if old_devices:
    for dev in new_devices:
        print(f"\n⚠️ NEW DEVICE DETECTED: {dev}")

for dev in missing_devices:
    print(f"\nℹ️ Device disconnected: {dev}")

# ✅ Save updated device list
with open("devices.txt", "w") as f:
    for d in devices:
        f.write(d.strip() + "\n")



print(f"DEBUG old_devices: {old_devices}")
print(f"DEBUG current_devices: {current_devices}")



# ✅ Mode selection
FORCE_MODE = None

if FORCE_MODE:
    mode = FORCE_MODE
    print(f"\nMode: {mode.upper()} SCAN\n")
else:
    mode = "basic"
    print("\nMode: BASIC SCAN (auto for speed)\n")




important_ports = [22, 80, 443]

total_ports = 0
high_risk = 0

# ✅ main loop
for device in devices:
    device_name = get_device_name(device)

    print(f"\nDevice: {device} ({device_name})")
    print("-" * 40)

    ports = scan(device, mode)

    if ports:
        for port in ports:

            total_ports += 1

            if port in port_info:
                pname, description, risk, advice = port_info[port]

                print(f"  🔎 Port {port} ({pname})")
                print(f"    Description: {description}")
                print(f"    Risk Level: {risk}")
                print(f"    Recommendation: {advice}")

                if risk == "HIGH":
                    high_risk += 1

                # ✅ Insights
                if port == 445:
                    print("    💡 Insight: File sharing is enabled.")
                elif port == 80:
                    print("    💡 Insight: Not encrypted — avoid sensitive data.")
                elif port == 443:
                    print("    💡 Insight: Secure encrypted traffic ✅")

            else:
                print(f"  ⚠️ Port {port} (Unknown service)")

            # ✅ Banner
            if port in important_ports:
                banner = grab_banner(device, port)

                if banner:
                    short_banner = banner.split("\n")[0]
                    print(f"    Service Info: {short_banner}")
                else:
                    print("    Service Info: Not available")

    else:
        print("  No open ports detected")


# ✅ SUMMARY
print("\n--- Summary ---")
print(f"Devices scanned: {len(devices)}")
print(f"Total open ports: {total_ports}")
print(f"High-risk ports: {high_risk}")

if high_risk >= 3:
    print("Overall Risk: 🔴 HIGH")
elif high_risk >= 1:
    print("Overall Risk: ⚠️ MEDIUM")
else:
    print("Overall Risk: ✅ LOW")


