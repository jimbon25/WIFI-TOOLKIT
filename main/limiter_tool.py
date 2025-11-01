
import os
import sys
import time
import subprocess

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
evillimiter_path = os.path.join(project_root, 'evillimiter')
if evillimiter_path not in sys.path:
    sys.path.insert(0, evillimiter_path)

try:
    import evillimiter.networking.utils as netutils
    from evillimiter.menus.main_menu import MainMenu
    from evillimiter.console.banner import get_main_banner
    from evillimiter.console.io import IO
    from evillimiter import __version__ as evillimiter_version
except ImportError as e:
    print(f"Critical Error: Could not import evillimiter modules: {e}")
    print("Please ensure 'evillimiter' directory is present and all its dependencies are installed.")
    netutils = None
    MainMenu = None

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

class EvilLimiterRunner:
    def __init__(self, interface, log_func):
        self.interface = interface
        self._log = log_func
        self.original_cwd = os.getcwd()

    def run(self):
        """
        Sets up and runs the Evil Limiter tool.
        """
        if not MainMenu:
            time.sleep(4)
            return

        print(f"{YELLOW}[*] Initializing Evil Limiter...{NC}")
        self._log("INFO", "Initializing Evil Limiter integration.")

        evillimiter_root = os.path.join(project_root, 'evillimiter')
        if os.path.isdir(evillimiter_root):
            os.chdir(evillimiter_root)
        
        gateway_ip = netutils.get_default_gateway()
        if not gateway_ip:
            print(f"{RED}[!] Could not determine default gateway for your network.{NC}")
            print(f"{YELLOW}    Please ensure you are connected to a network.{NC}")
            self._log("ERROR", "Evil Limiter: Could not get default gateway.")
            os.chdir(self.original_cwd)
            time.sleep(3)
            return

        gateway_mac = netutils.get_mac_by_ip(self.interface, gateway_ip)
        netmask = netutils.get_default_netmask(self.interface)

        if not all([gateway_mac, netmask]):
            print(f"{RED}[!] Failed to resolve network parameters for interface {self.interface}.{NC}")
            print(f"{RED}    Make sure the interface is connected to a network and has an IP address.{NC}")
            self._log("ERROR", f"Could not resolve network parameters for {self.interface}.")
            os.chdir(self.original_cwd)
            time.sleep(3)
            return

        print(f"{GREEN}[✔] Network Parameters Resolved:{NC}")
        print(f"    - Interface  : {self.interface}")
        print(f"    - Gateway IP : {gateway_ip}")
        print(f"    - Gateway MAC: {gateway_mac}")
        print(f"    - Netmask    : {netmask}")
        time.sleep(2)

        IO.initialize()
        
        if not netutils.enable_ip_forwarding():
            print(f"{RED}[!] Failed to enable IP forwarding. This is required for limiting.{NC}")
            self._log("ERROR", "Failed to enable IP forwarding for Evil Limiter.")
            os.chdir(self.original_cwd)
            return
            
        if not netutils.create_qdisc_root(self.interface):
            print(f"{RED}[!] Failed to create qdisc root handle on {self.interface}.{NC}")
            print(f"{YELLOW}    This can happen if a previous session crashed. Try restarting the script.{NC}")
            self._log("ERROR", f"Failed to create qdisc root for {self.interface}.")
            netutils.disable_ip_forwarding()
            os.chdir(self.original_cwd)
            return

        print(f"{GREEN}[✔] System configured for traffic shaping.{NC}")
        self._log("INFO", "Evil Limiter system environment prepared.")
        
        try:
            os.system('clear')
            print(get_main_banner(evillimiter_version))
            
            limiter_menu = MainMenu(evillimiter_version, self.interface, gateway_ip, gateway_mac, netmask)
            limiter_menu.start()
        
        finally:
            print(f"\n{YELLOW}[*] Cleaning up Evil Limiter settings...{NC}")
            self._log("INFO", "Cleaning up Evil Limiter environment.")
            netutils.delete_qdisc_root(self.interface)
            netutils.disable_ip_forwarding()
            print(f"{GREEN}[✔] Cleanup complete.{NC}")
            os.chdir(self.original_cwd)
            time.sleep(1)
