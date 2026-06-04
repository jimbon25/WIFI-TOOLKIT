"""
Utility Functions for Rogue AP Detection
========================================

Helper functions for MAC validation, formatting, etc.
"""

import re
import hashlib
import json
from datetime import datetime
from .constants import (
    COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_BLUE, COLOR_RESET,
    SIGNAL_STRENGTH_EXCELLENT, SIGNAL_STRENGTH_GOOD, SIGNAL_STRENGTH_FAIR,
    SIGNAL_STRENGTH_WEAK, SIGNAL_STRENGTH_POOR, MAC_OBFUSCATION_CHAR
)
from .exceptions import InvalidMACAddressError, InvalidBSSIDError


def validate_mac_address(mac_address):
    """
    Validate MAC address format.
    
    Args:
        mac_address (str): MAC address to validate (format: AA:BB:CC:DD:EE:FF)
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        InvalidMACAddressError: If format is completely invalid
    """
    if not mac_address:
        raise InvalidMACAddressError(mac_address)
    
    # Remove common separators and normalize
    mac = mac_address.replace('-', ':').replace('.', ':').upper()
    
    # MAC should be 6 pairs of hex digits separated by colons
    mac_pattern = r'^([0-9A-F]{2}:){5}([0-9A-F]{2})$'
    
    if not re.match(mac_pattern, mac):
        raise InvalidMACAddressError(mac_address)
    
    return True


def validate_bssid(bssid):
    """
    Validate BSSID (same as MAC address).
    
    Args:
        bssid (str): BSSID to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        InvalidBSSIDError: If format is invalid
    """
    try:
        validate_mac_address(bssid)
        return True
    except InvalidMACAddressError as e:
        raise InvalidBSSIDError(bssid)


def normalize_mac_address(mac_address):
    """
    Normalize MAC address to standard format (AA:BB:CC:DD:EE:FF).
    
    Args:
        mac_address (str): MAC address in any format
        
    Returns:
        str: Normalized MAC address
    """
    # Remove separators
    mac = mac_address.replace('-', '').replace(':', '').replace('.', '').upper()
    
    # Add colons every 2 characters
    return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))


def obfuscate_mac_address(mac_address, show_chars=2):
    """
    Obfuscate MAC address for privacy (e.g., AA:BB:CC:DD:*:*).
    
    Args:
        mac_address (str): MAC address to obfuscate
        show_chars (int): Number of octets to show from start
        
    Returns:
        str: Obfuscated MAC address
    """
    parts = mac_address.split(':')
    obfuscated = parts[:show_chars] + [MAC_OBFUSCATION_CHAR * 2] * (6 - show_chars)
    return ':'.join(obfuscated)


def extract_oui(mac_address):
    """
    Extract OUI (Organizationally Unique Identifier) from MAC address.
    
    Args:
        mac_address (str): MAC address
        
    Returns:
        str: First 8 characters of MAC (OUI in format AA:BB:CC)
    """
    parts = mac_address.split(':')
    return ':'.join(parts[:3])


def format_signal_strength(rssi_dbm):
    """
    Format signal strength in dBm with human-readable description.
    
    Args:
        rssi_dbm (int): Signal strength in dBm
        
    Returns:
        tuple: (formatted_string, description, color_code)
    """
    if not rssi_dbm or rssi_dbm < -100 or rssi_dbm > -20:
        return "N/A", "Unknown", COLOR_RESET
    
    if SIGNAL_STRENGTH_EXCELLENT[0] <= rssi_dbm <= SIGNAL_STRENGTH_EXCELLENT[1]:
        return f"{rssi_dbm} dBm", "Excellent", COLOR_GREEN
    elif SIGNAL_STRENGTH_GOOD[0] <= rssi_dbm <= SIGNAL_STRENGTH_GOOD[1]:
        return f"{rssi_dbm} dBm", "Good", COLOR_GREEN
    elif SIGNAL_STRENGTH_FAIR[0] <= rssi_dbm <= SIGNAL_STRENGTH_FAIR[1]:
        return f"{rssi_dbm} dBm", "Fair", COLOR_YELLOW
    elif SIGNAL_STRENGTH_WEAK[0] <= rssi_dbm <= SIGNAL_STRENGTH_WEAK[1]:
        return f"{rssi_dbm} dBm", "Weak", COLOR_YELLOW
    elif SIGNAL_STRENGTH_POOR[0] <= rssi_dbm <= SIGNAL_STRENGTH_POOR[1]:
        return f"{rssi_dbm} dBm", "Poor", COLOR_RED
    else:
        return f"{rssi_dbm} dBm", "Unknown", COLOR_RESET


def estimate_distance(rssi_dbm, frequency_ghz=2.4):
    """
    Estimate distance from AP based on signal strength (rough estimate).
    
    Args:
        rssi_dbm (int): Signal strength in dBm
        frequency_ghz (float): Frequency in GHz (2.4 or 5.0)
        
    Returns:
        float: Estimated distance in meters
    """
    if not rssi_dbm or rssi_dbm == 0:
        return 0
    
    # Free space path loss formula
    # Distance = 10^((27.55 - 20*log10(freq) + |rssi|)/20)
    import math
    
    const = 27.55 - 20 * math.log10(frequency_ghz)
    distance = 10 ** ((const + rssi_dbm) / 20)
    
    return round(distance, 1)


def format_timestamp(timestamp=None):
    """
    Format timestamp in ISO format.
    
    Args:
        timestamp (datetime): Timestamp to format (None = now)
        
    Returns:
        str: Formatted timestamp
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    if isinstance(timestamp, str):
        return timestamp
    
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def create_fingerprint_hash(*args):
    """
    Create hash from device fingerprint components.
    
    Args:
        *args: Components to hash (MAC, probes, etc)
        
    Returns:
        str: SHA256 hash of fingerprint
    """
    data = ''.join(str(arg) for arg in args)
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def format_bytes(bytes_count):
    """
    Format byte count to human-readable format.
    
    Args:
        bytes_count (int): Number of bytes
        
    Returns:
        str: Formatted size (B, KB, MB, GB)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    
    return f"{bytes_count:.2f} PB"


def format_duration(seconds):
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration (1h 23m 45s)
    """
    if not seconds:
        return "0s"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return ' '.join(parts)


def create_report_header(title, width=80):
    """
    Create formatted report header.
    
    Args:
        title (str): Header title
        width (int): Header width
        
    Returns:
        str: Formatted header
    """
    border = '=' * width
    padding = (width - len(title) - 2) // 2
    header = f"{border}\n {title.center(width - 2)}\n{border}"
    return header


def create_report_section(title, width=80):
    """
    Create formatted report section.
    
    Args:
        title (str): Section title
        width (int): Width
        
    Returns:
        str: Formatted section header
    """
    border = '-' * width
    return f"\n{title}\n{border}"


def colorize_text(text, color_code):
    """
    Add color to text for terminal output.
    
    Args:
        text (str): Text to colorize
        color_code (str): Color code constant
        
    Returns:
        str: Colored text
    """
    return f"{color_code}{text}{COLOR_RESET}"


def safe_json_encode(obj):
    """
    Safely encode object to JSON.
    
    Args:
        obj: Object to encode
        
    Returns:
        str: JSON string
    """
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception as e:
        return f'{{"error": "JSON encoding failed: {str(e)}"}}'


def safe_json_decode(json_str):
    """
    Safely decode JSON string.
    
    Args:
        json_str (str): JSON string to decode
        
    Returns:
        dict: Decoded object or empty dict on error
    """
    try:
        return json.loads(json_str)
    except Exception:
        return {}


def is_broadcast_mac(mac_address):
    """
    Check if MAC is broadcast address (FF:FF:FF:FF:FF:FF).
    
    Args:
        mac_address (str): MAC address to check
        
    Returns:
        bool: True if broadcast MAC
    """
    return mac_address.upper() == 'FF:FF:FF:FF:FF:FF'


def is_multicast_mac(mac_address):
    """
    Check if MAC is multicast address (first octet odd).
    
    Args:
        mac_address (str): MAC address to check
        
    Returns:
        bool: True if multicast MAC
    """
    first_octet = int(mac_address.split(':')[0], 16)
    return (first_octet & 1) == 1


def is_locally_administered_mac(mac_address):
    """
    Check if MAC is locally administered (bit 1 of first octet set).
    
    Args:
        mac_address (str): MAC address to check
        
    Returns:
        bool: True if locally administered
    """
    first_octet = int(mac_address.split(':')[0], 16)
    return (first_octet & 2) == 2


def group_macs_by_manufacturer(mac_list, oui_database):
    """
    Group MAC addresses by manufacturer.
    
    Args:
        mac_list (list): List of MAC addresses
        oui_database (dict): OUI to manufacturer mapping
        
    Returns:
        dict: Grouped MACs by manufacturer
    """
    grouped = {}
    
    for mac in mac_list:
        oui = extract_oui(mac)
        manufacturer = oui_database.get(oui, 'Unknown')
        
        if manufacturer not in grouped:
            grouped[manufacturer] = []
        
        grouped[manufacturer].append(mac)
    
    return grouped


def compare_signal_trends(signals_list):
    """
    Analyze signal strength trends.
    
    Args:
        signals_list (list): List of signal strength readings
        
    Returns:
        dict: Trend analysis (direction, avg, trend_type)
    """
    if len(signals_list) < 2:
        return {
            'trend': 'insufficient_data',
            'average': signals_list[0] if signals_list else 0,
            'direction': 'none'
        }
    
    first_half_avg = sum(signals_list[:len(signals_list)//2]) / max(1, len(signals_list)//2)
    second_half_avg = sum(signals_list[len(signals_list)//2:]) / max(1, len(signals_list) - len(signals_list)//2)
    
    if second_half_avg > first_half_avg + 3:
        direction = 'improving'
    elif second_half_avg < first_half_avg - 3:
        direction = 'degrading'
    else:
        direction = 'stable'
    
    return {
        'trend': 'analyzed',
        'average': sum(signals_list) / len(signals_list),
        'direction': direction,
        'recent_signal': signals_list[-1] if signals_list else 0
    }
