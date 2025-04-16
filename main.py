import subprocess
import re
import platform
import os
import time
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

VENDOR_PREFIXES = {
    "FC-AA-14": "Apple",
    "28-37-37": "Samsung",
    "00-1A-2B": "Windows PC",
    "AC-BC-32": "Xiaomi",
    "B8-27-EB": "Raspberry Pi",
    "40-4E-36": "Huawei",
}

previous_devices = set()

def get_vendor(mac):
    prefix = mac.upper()[0:8]
    for known_prefix, vendor in VENDOR_PREFIXES.items():
        if prefix.startswith(known_prefix):
            return vendor
    return "Unknown"

def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    try:
        subprocess.check_output(command, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def get_connected_devices():
    local_ip_prefix = "192.168.137."
    devices = []

    for i in range(1, 20):
        ip = f"{local_ip_prefix}{i}"
        ping_ip(ip)
        time.sleep(0.03)

    try:
        output = subprocess.check_output("arp -a", shell=True, encoding='utf-8')
        lines = output.splitlines()

        for line in lines:
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([\w-]+)\s+(\w+)", line)
            if match:
                ip = match.group(1)
                mac = match.group(2)
                vendor = get_vendor(mac)
                devices.append((ip, mac, vendor))

        return devices
    except Exception as e:
        print(Fore.RED + f"\n❌ Error: {e}")
        return []

def print_logo():
    print(Fore.MAGENTA + "==========================================")
    print(Fore.GREEN + "   🔥 Wi-Fi Hotspot Device Scanner 🔥")
    print(Fore.MAGENTA + "==========================================")

def print_devices(devices, previous_devices_set):
    if not devices:
        print(Fore.RED + "\n⚠️  No connected devices found.")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(Fore.YELLOW + f"\n📅 Scan Time: {now}")
    print(Fore.CYAN + "{:<20} {:<20} {:<15}".format("IP Address", "MAC Address", "Device Type"))
    print(Fore.CYAN + "-" * 55)

    current_device_set = set()
    log_lines = [f"\n=== Scan at {now} ==="]

    for ip, mac, vendor in devices:
        current_device_set.add(mac)
        is_new = mac not in previous_devices_set
        ip_str = Fore.GREEN + "{:<20}".format(ip)
        mac_str = Fore.BLUE + "{:<20}".format(mac)
        vendor_str = Fore.MAGENTA + "{:<15}".format(vendor)

        if is_new:
            print(Fore.RED + "🆕 NEW DEVICE DETECTED!")
            print(ip_str + mac_str + vendor_str)
        else:
            print(ip_str + mac_str + vendor_str)

        log_lines.append(f"{ip} | {mac} | {vendor} {'(NEW)' if is_new else ''}")

    with open("scan_log.txt", "a") as f:
        f.write("\n".join(log_lines))
        f.write("\n")

    return current_device_set

def clear_console():
    os.system("cls" if platform.system() == "Windows" else "clear")

def run_interactive_scanner():
    global previous_devices
    while True:
        clear_console()
        print_logo()
        devices = get_connected_devices()
        previous_devices = print_devices(devices, previous_devices)
        print(Fore.YELLOW + "\n🔁 Press [r] to rescan | [q] to quit")
        choice = input(">>> ").lower()
        if choice == 'q':
            break

# 🏁 تشغيل التول
if __name__ == "__main__":
    run_interactive_scanner()
