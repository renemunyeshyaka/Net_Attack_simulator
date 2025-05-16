#!/usr/bin/env python3
import subprocess
import socket
import uuid
import os
import platform
import re
import ipaddress
import threading
from datetime import datetime

def get_system_info():
    """Collect basic system information"""
    try:
        hostname = socket.gethostname()
        
        # Get MAC address
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        
        # Get IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = socket.gethostbyname(hostname)
        
        # Get default gateway
        gateway = get_default_gateway()
        
        return {
            "MAC Address": mac,
            "Computer Name": hostname,
            "IP Address": ip,
            "Default Gateway": gateway,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "OS": platform.system()
        }
    except Exception as e:
        return {"Error": f"System info collection failed: {str(e)}"}

def get_default_gateway():
    """Get default gateway based on OS"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            match = re.search(r"Default Gateway\s*\.*\s*:\s*([0-9\.]+)", result.stdout)
            return match.group(1) if match else "Not found"
        else:
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            match = re.search(r"default via ([0-9\.]+)", result.stdout)
            return match.group(1) if match else "Not found"
    except:
        return "Could not determine"

def scan_network(base_ip=None):
    """Scan local network for connected devices"""
    devices = []
    try:
        # Determine network to scan
        if not base_ip:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        else:
            network = ipaddress.IPv4Network(base_ip, strict=False)
        
        print(f"[*] Scanning network: {network}")
        
        # Threaded ping sweep
        threads = []
        for ip in network.hosts():
            t = threading.Thread(target=ping_device, args=(str(ip), devices))
            threads.append(t)
            t.start()
            
            # Limit number of concurrent threads
            if len(threads) > 50:
                for t in threads:
                    t.join()
                threads = []
        
        for t in threads:
            t.join()
            
    except Exception as e:
        devices.append({"Error": f"Network scan failed: {str(e)}"})
    
    return devices

def ping_device(ip, devices_list):
    """Ping a device and check if it's alive"""
    try:
        if platform.system() == "Windows":
            param = '-n'
            timeout = '1000'  # in milliseconds
        else:
            param = '-c'
            timeout = '1'  # in seconds
        
        command = ['ping', param, '1', '-w', timeout, ip]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except:
                hostname = "Unknown"
            
            devices_list.append({
                "IP": ip,
                "Hostname": hostname,
                "Status": "Active"
            })
    except:
        pass

def save_to_file(system_info, devices, filename="extractor_report.txt"):
    """Append data to report file"""
    try:
        with open(filename, 'a') as f:
            f.write("\n" + "="*60 + "\n")
            f.write(f"Report generated at: {system_info['Timestamp']}\n")
            f.write(f"System Type: {system_info['OS']}\n")
            f.write("="*60 + "\n\n")
            
            f.write("=== SYSTEM NETWORK INFORMATION ===\n")
            f.write(f"{'MAC Address':<15}: {system_info['MAC Address']}\n")
            f.write(f"{'Computer Name':<15}: {system_info['Computer Name']}\n")
            f.write(f"{'IP Address':<15}: {system_info['IP Address']}\n")
            f.write(f"{'Default Gateway':<15}: {system_info['Default Gateway']}\n")
            
            f.write("\n=== CONNECTED DEVICES ===\n")
            if isinstance(devices, list) and len(devices) > 0:
                f.write(f"{'IP':<15} {'Hostname':<25} {'Status':<10}\n")
                f.write("-" * 50 + "\n")
                for device in devices:
                    if "Error" in device:
                        f.write(f"Error: {device['Error']}\n")
                    else:
                        f.write(f"{device['IP']:<15} {device['Hostname']:<25} {device['Status']:<10}\n")
            else:
                f.write("No devices found or scan failed\n")
            
            f.write("\n")
    except Exception as e:
        print(f"Failed to save report: {str(e)}")

def main():
    print("\n=== Network Information Extractor ===\n")
    
    print("[*] Collecting system information...")
    system_info = get_system_info()
    
    print("[*] Scanning local network for connected devices...")
    devices = scan_network()
    
    print("[*] Saving to extractor_report.txt...")
    save_to_file(system_info, devices)
    
    print("[+] Operation completed successfully")
    print(f"[+] Report saved to: {os.path.abspath('extractor_report.txt')}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Operation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"[-] Critical error: {str(e)}")
        exit(1)