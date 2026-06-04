"""
Input validation and secure file handling utilities.
Prevents injection attacks and unsafe file operations.
"""

import os
import re
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Patterns for dangerous input
DANGEROUS_PATTERNS = [
    r'[;&|`$]',  # Shell metacharacters
    r'\.\.',  # Directory traversal
    r'[\x00-\x1f]',  # Control characters
]


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_string_input(
    value: str,
    max_length: int = 1000,
    allow_spaces: bool = True,
    pattern: Optional[str] = None
) -> str:
    """
    Validate and sanitize user string input.
    
    Args:
        value: Input string to validate
        max_length: Maximum allowed length
        allow_spaces: Whether to allow spaces
        pattern: Regex pattern that value must match
        
    Returns:
        Sanitized string
        
    Raises:
        ValidationError: If input fails validation
    """
    if not isinstance(value, str):
        raise ValidationError(f"Expected string, got {type(value)}")
    
    if len(value) > max_length:
        raise ValidationError(f"Input exceeds maximum length of {max_length}")
    
    if len(value) == 0:
        raise ValidationError("Input cannot be empty")
    
    # Check for dangerous patterns
    for danger_pattern in DANGEROUS_PATTERNS:
        if re.search(danger_pattern, value):
            raise ValidationError(f"Input contains prohibited characters")
    
    # If spaces not allowed, check for them
    if not allow_spaces and ' ' in value:
        raise ValidationError("Input cannot contain spaces")
    
    # Check against custom pattern if provided
    if pattern:
        if not re.match(pattern, value):
            raise ValidationError(f"Input does not match required pattern")
    
    logger.debug(f"Input validation passed for: {value[:50]}")
    return value


def validate_filepath(filepath: str, allow_relative: bool = False) -> str:
    """
    Validate file path to prevent directory traversal attacks.
    
    Args:
        filepath: Path to validate
        allow_relative: Whether to allow relative paths
        
    Returns:
        Normalized path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not isinstance(filepath, str):
        raise ValidationError("Filepath must be string")
    
    if not filepath:
        raise ValidationError("Filepath cannot be empty")
    
    # Resolve path to prevent directory traversal
    try:
        resolved = os.path.abspath(filepath)
    except (OSError, ValueError) as e:
        raise ValidationError(f"Invalid filepath: {e}")
    
    # Check for attempts to escape restricted directories
    if '..' in filepath:
        logger.warning(f"Directory traversal attempt detected: {filepath}")
        raise ValidationError("Directory traversal not allowed")
    
    return resolved


def validate_essid(essid: str) -> str:
    """
    Validate WiFi ESSID (network name).
    
    Args:
        essid: Network name to validate
        
    Returns:
        Validated ESSID
        
    Raises:
        ValidationError: If ESSID is invalid
    """
    if not isinstance(essid, str):
        raise ValidationError("ESSID must be string")
    
    # ESSID can be 0-32 bytes (empty is valid for hidden networks)
    if len(essid.encode('utf-8')) > 32:
        raise ValidationError("ESSID exceeds maximum length of 32 bytes")
    
    # Check for null bytes
    if '\x00' in essid:
        raise ValidationError("ESSID contains null bytes")
    
    return essid


def validate_password(password: str, min_length: int = 8) -> str:
    """
    Validate WiFi password/passphrase.
    
    Args:
        password: Password to validate
        min_length: Minimum allowed length
        
    Returns:
        Validated password
        
    Raises:
        ValidationError: If password is invalid
    """
    if not isinstance(password, str):
        raise ValidationError("Password must be string")
    
    if len(password) < min_length:
        raise ValidationError(f"Password must be at least {min_length} characters")
    
    # WPA2 password max length is 63
    if len(password) > 63:
        raise ValidationError("Password exceeds maximum length of 63 characters")
    
    # Check for null bytes
    if '\x00' in password:
        raise ValidationError("Password contains null bytes")
    
    return password


def validate_ip_address(ip: str) -> str:
    """
    Validate IP address or CIDR notation.
    
    Args:
        ip: IP address or range to validate
        
    Returns:
        Validated IP address
        
    Raises:
        ValidationError: If IP is invalid
    """
    # Simple IP validation - match IPv4 or CIDR notation
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?$'
    
    if not re.match(ip_pattern, ip):
        raise ValidationError(f"Invalid IP address format: {ip}")
    
    # Validate octets are in range 0-255
    if '/' in ip:
        ip_part = ip.split('/')[0]
    else:
        ip_part = ip
    
    octets = ip_part.split('.')
    for octet in octets:
        if int(octet) > 255:
            raise ValidationError(f"IP octet out of range: {octet}")
    
    return ip


def validate_interface_name(ifname: str) -> str:
    """
    Validate network interface name.
    
    Args:
        ifname: Interface name to validate
        
    Returns:
        Validated interface name
        
    Raises:
        ValidationError: If interface name is invalid
    """
    # Interface names are typically short like eth0, wlan0, etc
    if not isinstance(ifname, str):
        raise ValidationError("Interface name must be string")
    
    if len(ifname) > 16:  # Linux IFNAMSIZ limit
        raise ValidationError("Interface name too long")
    
    # Should be alphanumeric with possible ':' or '-'
    if not re.match(r'^[a-zA-Z0-9\:\-_]+$', ifname):
        raise ValidationError("Invalid interface name characters")
    
    return ifname


def create_secure_temp_file(suffix: str = '', prefix: str = 'wifitool_') -> tuple:
    """
    Create a secure temporary file with proper permissions.
    
    Args:
        suffix: File suffix/extension
        prefix: File name prefix
        
    Returns:
        Tuple of (file_handle, filepath)
    """
    try:
        # Create temp file with restrictive permissions (owner read/write only)
        temp_file = tempfile.NamedTemporaryFile(
            mode='w+',
            suffix=suffix,
            prefix=prefix,
            delete=False,
            encoding='utf-8'
        )
        
        # Ensure secure permissions (0o600 = owner only)
        os.chmod(temp_file.name, 0o600)
        
        logger.debug(f"Created secure temp file: {temp_file.name}")
        return temp_file, temp_file.name
        
    except Exception as e:
        logger.error(f"Failed to create secure temp file: {e}")
        raise


def create_secure_temp_dir(prefix: str = 'wifitool_') -> str:
    """
    Create a secure temporary directory with proper permissions.
    
    Args:
        prefix: Directory name prefix
        
    Returns:
        Path to temporary directory
    """
    try:
        # Create temp directory with restrictive permissions
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        
        # Ensure secure permissions (0o700 = owner only)
        os.chmod(temp_dir, 0o700)
        
        logger.debug(f"Created secure temp directory: {temp_dir}")
        return temp_dir
        
    except Exception as e:
        logger.error(f"Failed to create secure temp directory: {e}")
        raise
