"""
Custom Exceptions for Rogue AP Detection
========================================

Specific exception types for error handling.
"""


class RogueAPDetectionError(Exception):
    """Base exception for all rogue AP detection errors."""
    pass


class InterfaceNotFoundError(RogueAPDetectionError):
    """Raised when WiFi interface cannot be found or accessed."""
    
    def __init__(self, interface_name, message="Interface not found or not accessible"):
        self.interface_name = interface_name
        self.message = f"{message}: {interface_name}"
        super().__init__(self.message)


class InterfaceNotInMonitorMode(RogueAPDetectionError):
    """Raised when interface is not in monitor mode."""
    
    def __init__(self, interface_name):
        self.message = f"Interface {interface_name} is not in monitor mode"
        super().__init__(self.message)


class PermissionDeniedError(RogueAPDetectionError):
    """Raised when insufficient permissions to access hardware."""
    
    def __init__(self, resource="WiFi interface"):
        self.message = f"Permission denied accessing {resource}. Try with sudo."
        super().__init__(self.message)


class PacketCaptureError(RogueAPDetectionError):
    """Raised when packet capture fails."""
    
    def __init__(self, reason="Unknown"):
        self.message = f"Packet capture error: {reason}"
        super().__init__(self.message)


class PacketFilterError(RogueAPDetectionError):
    """Raised when packet filtering fails."""
    
    def __init__(self, filter_expression="Unknown"):
        self.message = f"Packet filter error: {filter_expression}"
        super().__init__(self.message)


class DatabaseError(RogueAPDetectionError):
    """Raised when database operations fail."""
    
    def __init__(self, operation="Unknown", reason=""):
        self.operation = operation
        self.message = f"Database error during {operation}: {reason}"
        super().__init__(self.message)


class DatabaseConnectionError(DatabaseError):
    """Raised when cannot connect to database."""
    
    def __init__(self, db_path=""):
        super().__init__("connection", f"Cannot access database at {db_path}")


class DatabaseTransactionError(DatabaseError):
    """Raised when database transaction fails."""
    
    def __init__(self, reason="Transaction failed"):
        super().__init__("transaction", reason)


class FingerprintingError(RogueAPDetectionError):
    """Raised when device fingerprinting fails."""
    
    def __init__(self, reason="Unknown"):
        self.message = f"Fingerprinting error: {reason}"
        super().__init__(self.message)


class InvalidMACAddressError(RogueAPDetectionError):
    """Raised when MAC address format is invalid."""
    
    def __init__(self, mac_address=""):
        self.mac_address = mac_address
        self.message = f"Invalid MAC address format: {mac_address}"
        super().__init__(self.message)


class InvalidBSSIDError(RogueAPDetectionError):
    """Raised when BSSID format is invalid."""
    
    def __init__(self, bssid=""):
        self.bssid = bssid
        self.message = f"Invalid BSSID format: {bssid}"
        super().__init__(self.message)


class DetectionTimeoutError(RogueAPDetectionError):
    """Raised when detection times out."""
    
    def __init__(self, timeout_seconds=0):
        self.message = f"Detection timed out after {timeout_seconds} seconds"
        super().__init__(self.message)


class NoClientsDetectedError(RogueAPDetectionError):
    """Raised when no clients connect within timeout period."""
    
    def __init__(self):
        self.message = "No clients detected connecting to rogue AP"
        super().__init__(self.message)


class ConfigurationError(RogueAPDetectionError):
    """Raised when configuration is invalid."""
    
    def __init__(self, config_name="", reason=""):
        self.message = f"Configuration error in {config_name}: {reason}"
        super().__init__(self.message)


class DependencyMissingError(RogueAPDetectionError):
    """Raised when required external tool is not installed."""
    
    def __init__(self, tool_name="", install_hint=""):
        self.tool_name = tool_name
        self.message = f"Required tool not found: {tool_name}. {install_hint}"
        super().__init__(self.message)


class AirodumpNotInstalledError(DependencyMissingError):
    """Raised when airodump-ng is not installed."""
    
    def __init__(self):
        super().__init__(
            "airodump-ng",
            "Install with: sudo apt install aircrack-ng"
        )


class ScapyNotInstalledError(DependencyMissingError):
    """Raised when Scapy is not installed."""
    
    def __init__(self):
        super().__init__(
            "scapy",
            "Install with: pip install scapy"
        )


class ProcessError(RogueAPDetectionError):
    """Raised when subprocess execution fails."""
    
    def __init__(self, command="", exit_code=0, stderr=""):
        self.command = command
        self.exit_code = exit_code
        self.message = f"Process failed: {command} (exit code: {exit_code})"
        if stderr:
            self.message += f"\nError: {stderr}"
        super().__init__(self.message)


class LoggingError(RogueAPDetectionError):
    """Raised when logging operations fail."""
    
    def __init__(self, reason="Unknown"):
        self.message = f"Logging error: {reason}"
        super().__init__(self.message)


class ExportError(RogueAPDetectionError):
    """Raised when data export fails."""
    
    def __init__(self, export_format="", reason=""):
        self.message = f"Export error ({export_format}): {reason}"
        super().__init__(self.message)


class JSONExportError(ExportError):
    """Raised when JSON export fails."""
    
    def __init__(self, reason=""):
        super().__init__("JSON", reason)


class CSVExportError(ExportError):
    """Raised when CSV export fails."""
    
    def __init__(self, reason=""):
        super().__init__("CSV", reason)
