import argparse
import sys
import os
import yaml
from urllib.parse import urlparse

from garuda.core.engine import GarudaEngine

def display_disclaimer():
    """
    Displays a disclaimer message when the program is run.

    Behavior:
        - Displays a warning to the user to use this tool responsibly.
        - States that this tool is created for educational and cybersecurity testing purposes.
    """
    print("━" * 60)
    print("WARNING: Use this tool responsibly.")
    print("This tool is created for educational and cybersecurity testing purposes only.")
    print("The author is not responsible for any misuse.")
    print("━" * 60, "\n")

def create_argument_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the parser for command-line arguments.

    Returns:
        argparse.ArgumentParser: Configured parser to read CLI arguments.

    Behavior:
        - Provides options to specify target, attack method, configuration file, and other parameters.
        - Displays usage examples in the epilog section.
    """
    parser = argparse.ArgumentParser(
        description="Garuda: Advanced Load Testing Toolkit.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Usage examples:\n"
            "  python main.py --config config.example.yaml\n"
            "  python main.py http://target.com -m http-flood -c 500\n"
            "  python main.py --config config.yaml -c 1000  (override connections)"
        )
    )
    parser.add_argument("target", nargs='?', default=None, help="Full target URL (e.g., http://example.com).")
    parser.add_argument("-m", "--method", choices=['http-flood', 'slowloris', 'mixed'], help="Attack method to use.")
    
    parser.add_argument("--config", help="Path to the YAML configuration file.")
    parser.add_argument("--attacks", nargs='+', choices=['http-flood', 'slowloris'], help="(Only for 'mixed' mode) List of attacks to combine.")
    parser.add_argument("-c", "--connections", type=int, help="Number of simultaneous connections per attack.")
    parser.add_argument("-d", "--duration", type=int, help="Attack duration in seconds.")
    parser.add_argument("--confirm-target", help="Confirm target domain name to prevent errors.")
    parser.add_argument("--stealth", action='store_true', help="Enable stealth mode (only for http-flood).")
    return parser

def main():
    """
    Main entry point that now supports configuration files.

    Behavior:
        - Displays the disclaimer to the user.
        - Reads arguments from command-line and/or YAML configuration file.
        - Merges arguments from CLI and configuration file.
        - Validates required arguments such as target and attack method.
        - Starts the attack using `GarudaEngine`.

    Exceptions:
        - Stops the program if the configuration file is not found.
        - Displays an error message if arguments are invalid or an error occurs during execution.
    """
    display_disclaimer()
    
    parser = create_argument_parser()
    args = parser.parse_args()
    
    config_from_file = {}
    if args.config:
        if not os.path.exists(args.config):
            print(f"[FATAL] Configuration file not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        with open(args.config, 'r') as f:
            config_from_file = yaml.safe_load(f) or {}

    final_args = argparse.Namespace()
    
    for key, value in config_from_file.items():
        setattr(final_args, key, value)
        
    for key, value in vars(args).items():
        if value is not None and value is not False:
            setattr(final_args, key, value)

    if not getattr(final_args, 'target', None) or not getattr(final_args, 'method', None):
        parser.error("'target' and '-m/--method' arguments are required (either via CLI or config file).")
    
    if final_args.method == 'mixed' and not getattr(final_args, 'attacks', None):
        parser.error("--attacks argument is required when using 'mixed' method.")
        
    if not hasattr(final_args, 'connections'): final_args.connections = 100
    if not hasattr(final_args, 'duration'): final_args.duration = 60
    if not hasattr(final_args, 'stealth'): final_args.stealth = False

    target_domain = urlparse(final_args.target).hostname
    if getattr(final_args, 'confirm_target', None) and final_args.confirm_target != target_domain:
        print(f"[ERROR] Domain name in --confirm-target ('{final_args.confirm_target}') does not match target ('{target_domain}').", file=sys.stderr)
        sys.exit(1)

    try:
        engine = GarudaEngine(final_args)
        engine.start()
        print("\n[SUCCESS] Attack session completed normally.")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n[FATAL] An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()