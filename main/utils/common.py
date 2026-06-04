"""
Common utility functions used across multiple modules.
Eliminates code duplication throughout the wifi-tool codebase.
"""

import sys
import os

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
WHITE = '\033[0;37m'
NC = '\033[0m'

# Color combinations
SUCCESS = GREEN
WARNING = YELLOW
ERROR = RED
INFO = CYAN
HEADER = BLUE


def getch():
    """
    Read a single character from stdin without requiring Enter.
    Works on both Windows and Unix-like systems.
    
    Returns:
        Single character string
    """
    try:
        # Try Windows method first
        from msvcrt import getch as win_getch
        char = win_getch()
        return char.decode('utf-8') if isinstance(char, bytes) else char
    except ImportError:
        # Unix/Linux method
        import termios
        import tty
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def press_any_key(message: str = "Press any key to continue..."):
    """
    Display a message and wait for user to press any key.
    
    Args:
        message: Message to display
    """
    print(f"\n{INFO}{message}{NC}")
    getch()


def clear_screen():
    """
    Clear terminal screen in a safe, cross-platform way.
    Avoids using os.system() which is a security risk.
    """
    # ANSI escape sequence works on Unix/Linux/Mac
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()
    
    # Fallback for Windows (if ANSI not supported)
    if sys.platform == 'win32':
        try:
            os.system('cls')
        except (OSError, Exception):
            pass


def print_header(title: str, width: int = 50):
    """
    Print a formatted header with title.
    
    Args:
        title: Header title text
        width: Total width of header (default 50)
    """
    padding = (width - len(title) - 4) // 2
    print(f"\n{HEADER}{'='*width}{NC}")
    print(f"{HEADER}{'='*(padding)}{title}{'='*(width-padding-len(title))}{NC}")
    print(f"{HEADER}{'='*width}{NC}\n")


def print_menu(title: str, options: list, show_back: bool = True):
    """
    Print a formatted menu with options.
    
    Args:
        title: Menu title
        options: List of tuples (key, description)
        show_back: Whether to show 'Back' option (default True)
        
    Example:
        options = [
            ('1', 'Scan networks'),
            ('2', 'Evil Twin attack'),
        ]
        print_menu("Main Menu", options)
    """
    clear_screen()
    print_header(title)
    
    for key, description in options:
        print(f"  [{GREEN}{key}{NC}] {description}")
    
    if show_back:
        print(f"  [{RED}0{NC}] Back / Exit")
    
    print()


def print_success(message: str):
    """Print a success message."""
    print(f"{SUCCESS}[✓] {message}{NC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{INFO}[*] {message}{NC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{WARNING}[!] {message}{NC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{ERROR}[✗] {message}{NC}")


def table_format(data: list, headers: list = None, max_width: int = 80):
    """
    Format data as a simple ASCII table.
    
    Args:
        data: List of rows (each row is a list of values)
        headers: Optional column headers
        max_width: Maximum table width
        
    Returns:
        Formatted table as string
    """
    if not data:
        return ""
    
    if headers is None:
        headers = [f"Col {i+1}" for i in range(len(data[0]))]
    
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        width = len(str(header))
        for row in data:
            if i < len(row):
                width = max(width, len(str(row[i])))
        col_widths.append(width)
    
    # Build table
    lines = []
    sep = '+' + '+'.join(['-' * (w + 2) for w in col_widths]) + '+'
    
    # Header
    lines.append(sep)
    header_row = '|' + '|'.join([
        f" {str(h).ljust(w)} " for h, w in zip(headers, col_widths)
    ]) + '|'
    lines.append(header_row)
    lines.append(sep)
    
    # Rows
    for row in data:
        row_str = '|' + '|'.join([
            f" {str(row[i] if i < len(row) else '').ljust(w)} "
            for i, w in enumerate(col_widths)
        ]) + '|'
        lines.append(row_str)
    
    lines.append(sep)
    return '\n'.join(lines)


def yes_no_prompt(prompt: str, default: bool = False) -> bool:
    """
    Prompt user for yes/no response.
    
    Args:
        prompt: Prompt text
        default: Default value if user just presses Enter
        
    Returns:
        True for yes, False for no
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if response == '':
        return default
    return response in ('y', 'yes')


def wait_for_keypress(timeout: int = None):
    """
    Wait for keypress with optional timeout.
    
    Args:
        timeout: Timeout in seconds (None for no timeout)
        
    Returns:
        True if key was pressed, False if timeout
    """
    import select
    
    if sys.platform == 'win32':
        # Windows doesn't support select on stdin
        getch()
        return True
    
    if timeout:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        return bool(ready)
    else:
        getch()
        return True


def sanitize_filename(filename: str, replacement: str = '_') -> str:
    """
    Remove/replace unsafe characters from filename.
    
    Args:
        filename: Filename to sanitize
        replacement: Character to replace unsafe chars with
        
    Returns:
        Sanitized filename
    """
    import re
    # Remove/replace dangerous characters
    unsafe_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(unsafe_chars, replacement, filename)
    # Remove trailing dots and spaces
    sanitized = sanitized.rstrip('. ')
    return sanitized


def format_bytes(bytes_count: int) -> str:
    """
    Format byte count as human-readable string.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"
