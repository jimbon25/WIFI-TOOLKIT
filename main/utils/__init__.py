"""
Utility modules for wifi-tool
"""

from .safe_subprocess import (
    safe_execute,
    safe_execute_with_output,
    safe_popen,
    is_valid_cli_input,
    validate_command_args
)

from .input_validation import (
    ValidationError,
    validate_string_input,
    validate_filepath,
    validate_essid,
    validate_password,
    validate_ip_address,
    validate_interface_name,
    create_secure_temp_file,
    create_secure_temp_dir
)

from .logging_config import (
    setup_logger,
    LoggingMixin,
    wifi_logger,
    network_logger,
    attack_logger,
    security_logger,
    debug_logger,
)

from .common import (
    getch,
    press_any_key,
    clear_screen,
    print_header,
    print_menu,
    print_success,
    print_info,
    print_warning,
    print_error,
    table_format,
    yes_no_prompt,
    wait_for_keypress,
    sanitize_filename,
    format_bytes,
    # Color constants
    RED,
    GREEN,
    YELLOW,
    BLUE,
    CYAN,
    MAGENTA,
    WHITE,
    NC,
    SUCCESS,
    WARNING,
    ERROR,
    INFO,
    HEADER,
)

from .di_container import (
    ServiceContainer,
    CircularDependencyError,
    ServiceNotFoundError,
    LifetimeError,
    get_container,
    inject,
    get_service,
    setup_wifi_tool_container,
    register_core_services,
)

__all__ = [
    # Subprocess utilities
    'safe_execute',
    'safe_execute_with_output', 
    'safe_popen',
    'is_valid_cli_input',
    'validate_command_args',
    # Input validation
    'ValidationError',
    'validate_string_input',
    'validate_filepath',
    'validate_essid',
    'validate_password',
    'validate_ip_address',
    'validate_interface_name',
    'create_secure_temp_file',
    'create_secure_temp_dir',
    # Logging
    'setup_logger',
    'LoggingMixin',
    'wifi_logger',
    'network_logger',
    'attack_logger',
    'security_logger',
    'debug_logger',
    # Common utilities
    'getch',
    'press_any_key',
    'clear_screen',
    'print_header',
    'print_menu',
    'print_success',
    'print_info',
    'print_warning',
    'print_error',
    'table_format',
    'yes_no_prompt',
    'wait_for_keypress',
    'sanitize_filename',
    'format_bytes',
    # Colors
    'RED',
    'GREEN',
    'YELLOW',
    'BLUE',
    'CYAN',
    'MAGENTA',
    'WHITE',
    'NC',
    'SUCCESS',
    'WARNING',
    'ERROR',
    'INFO',
    'HEADER',
    # Dependency Injection
    'ServiceContainer',
    'CircularDependencyError',
    'ServiceNotFoundError',
    'LifetimeError',
    'get_container',
    'inject',
    'get_service',
    'setup_wifi_tool_container',
    'register_core_services',
]
