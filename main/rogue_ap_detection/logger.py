"""
Detection Logger - Structured Logging for Rogue AP Detection
===========================================================

Handles all logging with proper formatting and file output.
"""

import logging
import json
from datetime import datetime
from .constants import (
    LOG_FILE, LOG_LEVEL_INFO, LOG_FORMAT, LOG_DATE_FORMAT,
    ANONYMIZE_LOGS
)
from .exceptions import LoggingError
from .utils import format_timestamp, safe_json_encode


class DetectionLogger:
    """Structured logging for detection events."""
    
    def __init__(self, name="RogueAPDetection", log_file=None):
        """
        Initialize logger.
        
        Args:
            name (str): Logger name
            log_file (str): Log file path (None = use default)
        """
        self.name = name
        self.log_file = log_file or LOG_FILE
        self.logger = self._setup_logger()
        self.event_buffer = []
        
    def _setup_logger(self):
        """Set up Python logging."""
        try:
            logger = logging.getLogger(self.name)
            logger.setLevel(LOG_LEVEL_INFO)
            
            # File handler
            fh = logging.FileHandler(self.log_file)
            fh.setLevel(LOG_LEVEL_INFO)
            
            # Formatter
            formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
            fh.setFormatter(formatter)
            
            # Clear existing handlers
            logger.handlers.clear()
            logger.addHandler(fh)
            
            return logger
        except Exception as e:
            raise LoggingError(f"Failed to setup logger: {str(e)}")
    
    def log_client_connected(self, mac_address, signal_strength, manufacturer=None):
        """
        Log client connection event.
        
        Args:
            mac_address (str): Client MAC address
            signal_strength (int): Signal in dBm
            manufacturer (str): Device manufacturer (optional)
        """
        if ANONYMIZE_LOGS:
            display_mac = mac_address[-8:]  # Show only last 8 chars
        else:
            display_mac = mac_address
        
        msg = f"CLIENT CONNECTED | MAC: {display_mac} | Signal: {signal_strength} dBm"
        if manufacturer:
            msg += f" | Manufacturer: {manufacturer}"
        
        self.logger.info(msg)
        
        self.event_buffer.append({
            'timestamp': format_timestamp(),
            'event': 'client_connected',
            'mac': mac_address,
            'signal': signal_strength,
            'manufacturer': manufacturer
        })
    
    def log_client_disconnected(self, mac_address):
        """
        Log client disconnection event.
        
        Args:
            mac_address (str): Client MAC address
        """
        if ANONYMIZE_LOGS:
            display_mac = mac_address[-8:]
        else:
            display_mac = mac_address
        
        msg = f"CLIENT DISCONNECTED | MAC: {display_mac}"
        self.logger.info(msg)
        
        self.event_buffer.append({
            'timestamp': format_timestamp(),
            'event': 'client_disconnected',
            'mac': mac_address
        })
    
    def log_data_transmission(self, mac_address, bytes_transmitted, frame_count=0):
        """
        Log data transmission from client.
        
        Args:
            mac_address (str): Client MAC address
            bytes_transmitted (int): Bytes sent/received
            frame_count (int): Number of data frames
        """
        if ANONYMIZE_LOGS:
            display_mac = mac_address[-8:]
        else:
            display_mac = mac_address
        
        msg = f"DATA TRANSMISSION | MAC: {display_mac} | Bytes: {bytes_transmitted} | Frames: {frame_count}"
        self.logger.info(msg)
        
        self.event_buffer.append({
            'timestamp': format_timestamp(),
            'event': 'data_transmission',
            'mac': mac_address,
            'bytes': bytes_transmitted,
            'frames': frame_count
        })
    
    def log_probe_request(self, mac_address, probe_ssids=None):
        """
        Log probe request from client.
        
        Args:
            mac_address (str): Client MAC address
            probe_ssids (list): SSIDs being probed (optional)
        """
        if ANONYMIZE_LOGS:
            display_mac = mac_address[-8:]
        else:
            display_mac = mac_address
        
        msg = f"PROBE REQUEST | MAC: {display_mac}"
        if probe_ssids:
            msg += f" | SSIDs: {','.join(probe_ssids[:3])}"
        
        self.logger.debug(msg)
        
        self.event_buffer.append({
            'timestamp': format_timestamp(),
            'event': 'probe_request',
            'mac': mac_address,
            'ssids': probe_ssids
        })
    
    def log_alert(self, message, severity='WARNING', mac_address=None):
        """
        Log alert/warning.
        
        Args:
            message (str): Alert message
            severity (str): 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
            mac_address (str): Related MAC (optional)
        """
        if mac_address and ANONYMIZE_LOGS:
            message = message.replace(mac_address, mac_address[-8:])
        
        log_func = getattr(self.logger, severity.lower(), self.logger.warning)
        log_func(f"[ALERT] {message}")
        
        self.event_buffer.append({
            'timestamp': format_timestamp(),
            'event': 'alert',
            'severity': severity,
            'message': message,
            'mac': mac_address
        })
    
    def log_signal_change(self, mac_address, old_signal, new_signal):
        """
        Log signal strength change.
        
        Args:
            mac_address (str): Client MAC
            old_signal (int): Previous signal
            new_signal (int): Current signal
        """
        if ANONYMIZE_LOGS:
            display_mac = mac_address[-8:]
        else:
            display_mac = mac_address
        
        change = new_signal - old_signal
        direction = "📈" if change > 0 else "📉"
        
        msg = f"SIGNAL CHANGE | MAC: {display_mac} | {old_signal} → {new_signal} dBm {direction}"
        self.logger.info(msg)
        
        self.event_buffer.append({
            'timestamp': format_timestamp(),
            'event': 'signal_change',
            'mac': mac_address,
            'old_signal': old_signal,
            'new_signal': new_signal,
            'change': change
        })
    
    def log_detection_start(self, target_bssid, interface):
        """
        Log detection start.
        
        Args:
            target_bssid (str): Rogue AP BSSID
            interface (str): WiFi interface
        """
        if ANONYMIZE_LOGS:
            display_bssid = target_bssid[-8:]
        else:
            display_bssid = target_bssid
        
        msg = f"DETECTION STARTED | BSSID: {display_bssid} | Interface: {interface}"
        self.logger.info(msg)
    
    def log_detection_stop(self, client_count, duration_seconds):
        """
        Log detection stop with summary.
        
        Args:
            client_count (int): Number of unique clients detected
            duration_seconds (float): Detection duration
        """
        msg = f"DETECTION STOPPED | Clients: {client_count} | Duration: {duration_seconds:.1f}s"
        self.logger.info(msg)
    
    def log_error(self, error_message, exception=None):
        """
        Log error with exception details.
        
        Args:
            error_message (str): Error message
            exception (Exception): Exception object (optional)
        """
        if exception:
            msg = f"{error_message}\nException: {str(exception)}"
        else:
            msg = error_message
        
        self.logger.error(msg)
        
        self.event_buffer.append({
            'timestamp': format_timestamp(),
            'event': 'error',
            'message': error_message,
            'exception': str(exception) if exception else None
        })
    
    def get_event_buffer(self):
        """
        Get buffered events.
        
        Returns:
            list: Event buffer
        """
        return self.event_buffer.copy()
    
    def clear_event_buffer(self):
        """Clear event buffer."""
        self.event_buffer.clear()
    
    def export_events_json(self):
        """
        Export events to JSON format.
        
        Returns:
            str: JSON string of events
        """
        return safe_json_encode(self.event_buffer)
    
    def export_events_csv(self):
        """
        Export events to CSV format.
        
        Returns:
            str: CSV string of events
        """
        if not self.event_buffer:
            return "timestamp,event,mac,details\n"
        
        lines = ["timestamp,event,mac,details"]
        
        for event in self.event_buffer:
            timestamp = event.get('timestamp', '')
            event_type = event.get('event', '')
            mac = event.get('mac', '')
            details = json.dumps({k: v for k, v in event.items() 
                                if k not in ['timestamp', 'event', 'mac']})
            
            lines.append(f'"{timestamp}","{event_type}","{mac}","{details}"')
        
        return '\n'.join(lines)
    
    def get_summary(self):
        """
        Get event summary statistics.
        
        Returns:
            dict: Summary statistics
        """
        event_counts = {}
        for event in self.event_buffer:
            event_type = event.get('event', 'unknown')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        unique_macs = len(set(e.get('mac') for e in self.event_buffer if 'mac' in e))
        
        return {
            'total_events': len(self.event_buffer),
            'event_counts': event_counts,
            'unique_clients': unique_macs,
            'first_event': self.event_buffer[0].get('timestamp') if self.event_buffer else None,
            'last_event': self.event_buffer[-1].get('timestamp') if self.event_buffer else None
        }
