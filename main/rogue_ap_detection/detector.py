"""
Main Rogue AP Detector - Orchestrates Everything
================================================

Main class that coordinates all detection components.
"""

import time
import threading
from datetime import datetime
from .packet_sniffer import PacketSniffer
from .client_tracker import ClientTracker
from .device_fingerprint import DeviceFingerprinter
from .logger import DetectionLogger
from .constants import (
    DETECTION_TIMEOUT, SIGNAL_THRESHOLD, COLOR_GREEN,
    COLOR_YELLOW, COLOR_RED, COLOR_RESET
)
from .exceptions import DetectionTimeoutError, NoClientsDetectedError
from .utils import validate_bssid, normalize_mac_address, format_duration, format_signal_strength


class RogueAPDetector:
    """
    Main orchestrator for rogue AP client detection.
    
    ANONYMOUS MODE:
    - No operator information stored
    - No identifying logs of who ran detection
    - Minimal data retention
    - Clean shutdown with optional data deletion
    """
    
    def __init__(self, rogue_bssid, interface, timeout=None, db_path=None, enable_logging=True):
        """
        Initialize rogue AP detector in anonymous mode.
        
        Args:
            rogue_bssid (str): Target rogue AP BSSID
            interface (str): WiFi interface (monitor mode)
            timeout (int): Detection timeout in seconds (None = no limit)
            db_path (str): Custom database path (None = default)
            enable_logging (bool): Enable logging (default True)
        """
        validate_bssid(rogue_bssid)
        
        self.rogue_bssid = normalize_mac_address(rogue_bssid)
        self.interface = interface
        self.timeout = timeout or DETECTION_TIMEOUT
        self.enable_logging = enable_logging
        self.is_detecting = False
        self.detection_start_time = None
        self.detection_end_time = None
        
        # Initialize components
        self.logger = DetectionLogger() if enable_logging else None
        self.tracker = ClientTracker(db_path)
        self.fingerprinter = DeviceFingerprinter()
        self.sniffer = PacketSniffer(interface, rogue_bssid)
        
        # Statistics
        self.stats = {
            'clients_detected': 0,
            'max_signal': -100,
            'min_signal': -30,
            'data_received': 0,
            'duration': 0,
            'manufacturers': {}
        }
    
    def start_detection(self):
        """Start detection process."""
        if self.is_detecting:
            raise RuntimeError("Detection already running")
        
        self.is_detecting = True
        self.detection_start_time = time.time()
        
        if self.logger:
            self.logger.log_detection_start(self.rogue_bssid, self.interface)
        
        # Start packet sniffer with callback
        self.sniffer.start_sniffing(callback=self._on_client_detected)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=False
        )
        self.monitor_thread.start()
    
    def stop_detection(self):
        """Stop detection and generate report."""
        if not self.is_detecting:
            return None
        
        self.is_detecting = False
        self.detection_end_time = time.time()
        self.stats['duration'] = self.detection_end_time - self.detection_start_time
        
        # Stop sniffer
        self.sniffer.stop_sniffing()
        
        # Wait for monitoring thread
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
        
        # Generate report
        report = self._generate_report()
        
        if self.logger:
            self.logger.log_detection_stop(
                self.stats['clients_detected'],
                self.stats['duration']
            )
        
        return report
    
    def _on_client_detected(self, mac_address, signal_strength, manufacturer):
        """
        Callback when new client detected.
        
        Args:
            mac_address (str): Client MAC
            signal_strength (int): Signal in dBm
            manufacturer (str): Device manufacturer
        """
        try:
            # Analyze device
            analysis = self.fingerprinter.analyze_device(
                mac_address,
                signal_strength
            )
            
            # Add to database
            self.tracker.add_client(
                mac_address,
                signal_strength,
                manufacturer=analysis['manufacturer'],
                device_type=analysis['device_type']
            )
            
            # Update stats
            self.stats['clients_detected'] += 1
            if signal_strength:
                self.stats['max_signal'] = max(self.stats['max_signal'], signal_strength)
                self.stats['min_signal'] = min(self.stats['min_signal'], signal_strength)
            
            # Update manufacturer count
            mfg = analysis['manufacturer']
            self.stats['manufacturers'][mfg] = self.stats['manufacturers'].get(mfg, 0) + 1
            
            # Log
            if self.logger:
                self.logger.log_client_connected(
                    mac_address,
                    signal_strength,
                    analysis['manufacturer']
                )
            
            # Console output
            self._print_client_alert(mac_address, analysis, signal_strength)
        
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Failed to process client {mac_address}", e)
    
    def _monitoring_loop(self):
        """Continuous monitoring loop."""
        while self.is_detecting:
            try:
                # Check timeout
                elapsed = time.time() - self.detection_start_time
                if elapsed > self.timeout:
                    self.is_detecting = False
                    break
                
                # Periodic reporting (every 5 seconds)
                time.sleep(5)
            
            except Exception as e:
                if self.logger:
                    self.logger.log_error("Monitoring loop error", e)
    
    def _print_client_alert(self, mac_address, analysis, signal_strength):
        """Print alert for new client."""
        signal_str, quality, color = format_signal_strength(signal_strength)
        
        output = f"\n{COLOR_GREEN}[+] CLIENT DETECTED{COLOR_RESET}\n"
        output += f"    MAC Address: {mac_address}\n"
        output += f"    Manufacturer: {analysis['manufacturer']}\n"
        output += f"    Device Type: {analysis['device_type']}\n"
        output += f"    Signal: {color}{signal_str} ({quality}){COLOR_RESET}\n"
        output += f"    Fingerprint: {analysis['fingerprint']}\n"
        output += f"    Confidence: {int(analysis['confidence']*100)}%\n"
        
        print(output)
    
    def _generate_report(self):
        """Generate final detection report."""
        clients = self.tracker.get_all_clients()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'rogue_bssid': self.rogue_bssid,
            'interface': self.interface,
            'detection_duration': self.stats['duration'],
            'total_clients': self.stats['clients_detected'],
            'clients': clients,
            'statistics': {
                'max_signal': self.stats['max_signal'],
                'min_signal': self.stats['min_signal'],
                'manufacturers': self.stats['manufacturers'],
                'unique_manufacturers': len(self.stats['manufacturers'])
            }
        }
        
        return report
    
    def get_connected_clients(self):
        """Get list of connected clients."""
        return self.tracker.get_all_clients(active_only=True)
    
    def get_all_clients(self):
        """Get all detected clients (including disconnected)."""
        return self.tracker.get_all_clients(active_only=False)
    
    def get_client_details(self, mac_address):
        """Get detailed info for a client."""
        return self.tracker.get_client_stats(mac_address)
    
    def get_statistics(self):
        """Get detection statistics."""
        return {
            'detection_active': self.is_detecting,
            'elapsed_time': time.time() - self.detection_start_time if self.detection_start_time else 0,
            'clients_detected': self.stats['clients_detected'],
            'signal_range': (self.stats['min_signal'], self.stats['max_signal']),
            'manufacturers': self.stats['manufacturers'],
            'database_info': {
                'total_records': self.tracker.get_clients_count(active_only=False),
                'active_clients': self.tracker.get_clients_count(active_only=True),
                'database_path': self.tracker.db_path
            }
        }
    
    def export_report(self, format='json'):
        """
        Export detection report.
        
        Args:
            format (str): 'json', 'csv', or 'dict'
            
        Returns:
            str or dict: Exported data
        """
        if format == 'json':
            return self.tracker.export_to_json()
        elif format == 'csv':
            return self.tracker.export_to_csv()
        elif format == 'dict':
            return self._generate_report()
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def export_logs(self, format='json'):
        """
        Export detection logs.
        
        Args:
            format (str): 'json' or 'csv'
            
        Returns:
            str: Exported logs
        """
        if not self.logger:
            return None
        
        if format == 'json':
            return self.logger.export_events_json()
        elif format == 'csv':
            return self.logger.export_events_csv()
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def cleanup(self, delete_database=False):
        """
        Clean up resources (use for anonymous cleanup).
        
        Args:
            delete_database (bool): Delete database file after cleanup
        """
        if self.is_detecting:
            self.stop_detection()
        
        self.sniffer.stop_sniffing()
        
        if delete_database:
            import os
            try:
                self.tracker.close()
                if os.path.exists(self.tracker.db_path):
                    os.remove(self.tracker.db_path)
            except (AttributeError, FileNotFoundError, OSError):
                pass
        else:
            self.tracker.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            if self.is_detecting:
                self.stop_detection()
        except (AttributeError, Exception):
            pass
