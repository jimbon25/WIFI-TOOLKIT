
import os
import sys
import subprocess
import time
import re

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class NmapTool:
    """
    A class to provide a menu-driven, automated interface for nmap.
    """
    def __init__(self, log_func):
        self._log = log_func
        self.active_processes = []

    def _run_command(self, command):
        """Executes a shell command, handling errors and logging."""
        self._log("INFO", f"Executing nmap command: {' '.join(command)}")
        try:
            process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.active_processes.append(process)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            rc = process.poll()
            if rc != 0:
                self._log("ERROR", f"nmap command failed with exit code {rc}.")

        except FileNotFoundError:
            print(f"{RED}Error: Command not found: {command[0]}{NC}")
            self._log("ERROR", f"Command not found: {command[0]}")
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{NC}")
            self._log("ERROR", f"An unexpected error occurred with command {' '.join(command)}: {e}")
        finally:
            if 'process' in locals() and process in self.active_processes:
                self.active_processes.remove(process)

    def _get_target(self):
        """Prompts the user for a target IP, range, or domain."""
        try:
            target = input(f"{YELLOW}[?] Enter the target (e.g., 192.168.1.1, 192.168.1.0/24, scanme.nmap.org): {NC}").strip()
            if not target:
                print(f"{RED}[!] Target cannot be empty.{NC}")
                time.sleep(2)
                return None
            return target
        except Exception as e:
            print(f"{RED}[!] Invalid input: {e}{NC}")
            return None

    def _show_nmap_menu(self):
        """Displays the main menu for the nmap tool."""
        os.system('clear')
        print(f"{BLUE}---[ Network Mapper (nmap) ]---{NC}")
        print(f"  [{GREEN}1{NC}] Quick Scan (-T4 -F)")
        print(f"  [{GREEN}2{NC}] Intense Scan (-T4 -A -v)")
        print(f"  [{GREEN}3{NC}] Ping Scan (Find Live Hosts)")
        print(f"  [{GREEN}4{NC}] Vulnerability Scan (--script vulners)")
        print(f"  [{GREEN}5{NC}] UDP Scan (-sU)")
        print(f"  [{GREEN}6{NC}] Custom Scan")
        print(f"  [{GREEN}7{NC}] Back to Main Menu")
        print(f"{BLUE}--------------------------------{NC}")

    def _quick_scan(self):
        os.system('clear')
        print(f"{YELLOW}[*] NMAP - QUICK SCAN{NC}")
        target = self._get_target()
        if not target: return

        print(f"\n{YELLOW}[*] Starting Quick Scan on {target}...{NC}")
        command = ['nmap', '-T4', '-F', target]
        self._run_command(command)
        print(f"\n{GREEN}[✔] Quick Scan complete. Press any key to continue...{NC}")
        input()

    def _intense_scan(self):
        os.system('clear')
        print(f"{YELLOW}[*] NMAP - INTENSE SCAN{NC}")
        target = self._get_target()
        if not target: return

        print(f"\n{YELLOW}[*] Starting Intense Scan on {target}... (This may take a while){NC}")
        command = ['nmap', '-T4', '-A', '-v', target]
        self._run_command(command)
        print(f"\n{GREEN}[✔] Intense Scan complete. Press any key to continue...{NC}")
        input()

    def _ping_scan(self):
        os.system('clear')
        print(f"{YELLOW}[*] NMAP - PING SCAN (HOST DISCOVERY){NC}")
        target = self._get_target()
        if not target: return

        print(f"\n{YELLOW}[*] Starting Ping Scan on {target}...{NC}")
        command = ['nmap', '-sn', target]
        self._run_command(command)
        print(f"\n{GREEN}[✔] Ping Scan complete. Press any key to continue...{NC}")
        input()

    def _vuln_scan(self):
        os.system('clear')
        print(f"{YELLOW}[*] NMAP - VULNERABILITY SCAN{NC}")
        print(f"{YELLOW}[!] This scan uses the 'vulners' script and requires an internet connection.{NC}")
        target = self._get_target()
        if not target: return

        print(f"\n{YELLOW}[*] Starting Vulnerability Scan on {target}... (This may take a significant amount of time){NC}")
        command = ['nmap', '-sV', '--script', 'vulners', target]
        self._run_command(command)
        print(f"\n{GREEN}[✔] Vulnerability Scan complete. Press any key to continue...{NC}")
        input()

    def _udp_scan(self):
        os.system('clear')
        print(f"{YELLOW}[*] NMAP - UDP SCAN{NC}")
        target = self._get_target()
        if not target: return

        print(f"\n{YELLOW}[*] Starting UDP Scan on {target}... (This is often slow){NC}")
        command = ['nmap', '-sU', target]
        self._run_command(command)
        print(f"\n{GREEN}[✔] UDP Scan complete. Press any key to continue...{NC}")
        input()

    def _custom_scan(self):
        os.system('clear')
        print(f"{YELLOW}[*] NMAP - CUSTOM SCAN{NC}")
        target = self._get_target()
        if not target: return
        
        try:
            flags = input(f"{YELLOW}[?] Enter custom nmap flags (e.g., -p 80,443 -sV): {NC}").strip()
        except Exception as e:
            print(f"{RED}[!] Invalid input: {e}{NC}")
            return

        print(f"\n{YELLOW}[*] Starting Custom Scan on {target} with flags '{flags}'...{NC}")
        command = ['nmap'] + flags.split() + [target]
        self._run_command(command)
        print(f"\n{GREEN}[✔] Custom Scan complete. Press any key to continue...{NC}")
        input()

    def run(self):
        """Displays the main nmap menu and handles user input."""
        while True:
            self._show_nmap_menu()
            choice = input(f"\n{YELLOW}Select an option [1-7]:{NC} ").strip()

            if choice == '1':
                self._quick_scan()
            elif choice == '2':
                self._intense_scan()
            elif choice == '3':
                self._ping_scan()
            elif choice == '4':
                self._vuln_scan()
            elif choice == '5':
                self._udp_scan()
            elif choice == '6':
                self._custom_scan()
            elif choice == '7':
                print(f"{YELLOW}Returning to main menu...{NC}")
                break
            else:
                print(f"{RED}Invalid option. Please try again.{NC}")
                time.sleep(1)
                
    def cleanup(self):
        """Cleans up any running processes."""
        print(f"{YELLOW}[*] Cleaning up nmap processes...{NC}")
        for proc in self.active_processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
        self.active_processes = []
        self._log("INFO", "nmap cleanup completed.")
