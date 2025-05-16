#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime
import platform
import json

def detect_os():
    """Detect the operating system"""
    system = platform.system().lower()
    if 'linux' in system:
        return 'linux'
    elif 'windows' in system:
        return 'windows'
    elif 'darwin' in system:
        return 'macos'
    else:
        return 'unknown'

def run_command(command):
    """Run a command and return its output"""
    try:
        result = subprocess.run(command, shell=True, check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e.stderr}")
        return None

def scan_wifi_linux():
    """Scan for available WiFi networks on Linux"""
    print("Scanning for available WiFi networks...")
    try:
        # Use nmcli to scan for networks
        run_command("nmcli device wifi rescan")
        networks = run_command("nmcli -t -f SSID device wifi list")
        if networks:
            return [net for net in networks.split('\n') if net]
    except Exception as e:
        print(f"Error scanning WiFi networks: {e}")
    return []

def get_wifi_passwords_linux():
    """Get stored WiFi passwords on Linux"""
    passwords = {}
    try:
        # Get list of known connections
        connections = run_command("nmcli -t -f NAME connection show")
        if connections:
            for conn in connections.split('\n'):
                if conn:
                    # Get WiFi password for each connection
                    output = run_command(f"nmcli -s -g 802-11-wireless-security.psk connection show '{conn}'")
                    if output and output != '--':
                        passwords[conn] = output
    except Exception as e:
        print(f"Error getting WiFi passwords: {e}")
    return passwords

def scan_wifi_windows():
    """Scan for available WiFi networks on Windows"""
    print("Scanning for available WiFi networks...")
    try:
        # Use netsh to list all WiFi profiles
        profiles = run_command("netsh wlan show networks mode=bssid")
        if profiles:
            networks = []
            for line in profiles.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    networks.append(line.split(":")[1].strip())
            return networks
    except Exception as e:
        print(f"Error scanning WiFi networks: {e}")
    return []

def get_wifi_passwords_windows():
    """Get stored WiFi passwords on Windows"""
    passwords = {}
    try:
        # Get list of all profiles
        profiles = run_command("netsh wlan show profiles")
        if profiles:
            for line in profiles.split('\n'):
                if "All User Profile" in line:
                    profile = line.split(":")[1].strip()
                    # Get password for each profile
                    output = run_command(f'netsh wlan show profile name="{profile}" key=clear')
                    if output:
                        for outline in output.split('\n'):
                            if "Key Content" in outline:
                                password = outline.split(":")[1].strip()
                                passwords[profile] = password
                                break
    except Exception as e:
        print(f"Error getting WiFi passwords: {e}")
    return passwords

def save_results(networks, passwords, filename):
    """Save the results to a text file"""
    with open(filename, 'w') as f:
        f.write(f"WiFi Network Scan Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        
        f.write("Available WiFi Networks:\n")
        f.write("-"*30 + "\n")
        for network in networks:
            f.write(f"{network}\n")
        
        f.write("\nStored WiFi Passwords:\n")
        f.write("-"*30 + "\n")
        if passwords:
            for ssid, pwd in passwords.items():
                f.write(f"SSID: {ssid}\nPassword: {pwd}\n\n")
        else:
            f.write("No stored passwords found\n")
    
    print(f"\nResults saved to {filename}")

def main():
    """Main function"""
    # Check if running as root/admin
    if os.name == 'posix' and os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        sys.exit(1)
    
    current_os = detect_os()
    print(f"Detected OS: {current_os}")
    
    networks = []
    passwords = {}
    
    if current_os == 'linux':
        networks = scan_wifi_linux()
        passwords = get_wifi_passwords_linux()
    elif current_os == 'windows':
        networks = scan_wifi_windows()
        passwords = get_wifi_passwords_windows()
    elif current_os == 'macos':
        print("macOS support is not implemented in this script.")
        sys.exit(1)
    else:
        print("Unsupported operating system")
        sys.exit(1)
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"wifi_passwords_{timestamp}.txt"
    
    # Save results
    save_results(networks, passwords, output_file)

if __name__ == "__main__":
    main()
