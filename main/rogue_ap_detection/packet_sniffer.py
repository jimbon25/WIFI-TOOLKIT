"""
Packet Sniffer - Low-level Packet Capture
==========================================

Captures WiFi packets using Scapy or airodump-ng.
"""

import subprocess
import threading
import time
import os
from .constants import DUPLICATE_WINDOW
from .exceptions import (
    PacketCaptureError, DependencyMissingError,
    AirodumpNotInstalledError, ProcessError
)
from .utils import validate_bssid, normalize_mac_address


class PacketSniffer:
    """Capture WiFi packets and extract client information."""
    
    def __init__(self, interface, target_bssid, method='airodump'):
        """
        Initialize packet sniffer.
        
        Args:
            interface (str): WiFi interface (must be in monitor mode)
            target_bssid (str): Target BSSID to filter
            method (str): Capture method ('airodump' or 'scapy')
        """
        validate_bssid(target_bssid)
        
        self.interface = interface
        self.target_bssid = normalize_mac_address(target_bssid)
        self.method = method
        self.is_sniffing = False
        self.client_callback = None
        self.sniffer_thread = None
        self.captured_clients = {}
        self.seen_packets = {}  # For duplicate detection
    
    def start_sniffing(self, callback=None):
        """
        Start packet capture.
        
        Args:
            callback (callable): Callback function for new clients
                                 Signature: callback(mac, signal, manufacturer)
        """
        if self.is_sniffing:
            raise PacketCaptureError("Sniffer already running")
        
        self.client_callback = callback
        self.is_sniffing = True
        
        if self.method == 'airodump':
            self.sniffer_thread = threading.Thread(
                target=self._sniff_airodump,
                daemon=True
            )
        elif self.method == 'scapy':
            self.sniffer_thread = threading.Thread(
                target=self._sniff_scapy,
                daemon=True
            )
        else:
            raise PacketCaptureError(f"Unknown method: {self.method}")
        
        self.sniffer_thread.start()
    
    def stop_sniffing(self):
        """Stop packet capture."""
        self.is_sniffing = False
        if self.sniffer_thread:
            self.sniffer_thread.join(timeout=2)
    
    def get_captured_clients(self):
        """
        Get all captured clients.
        
        Returns:
            dict: {mac_address: {signal, manufacturer, first_seen, last_seen}}
        """
        return self.captured_clients.copy()
    
    def _sniff_airodump(self):
        """Capture using airodump-ng."""
        try:
            # Check if airodump-ng is installed
            try:
                subprocess.run(['which', 'airodump-ng'], check=True, 
                             capture_output=True, timeout=2)
            except subprocess.CalledProcessError:
                raise AirodumpNotInstalledError()
            
            # Start airodump-ng
            self.temp_prefix = f"/tmp/airodump_out_{os.getpid()}_{int(time.time())}"
            cmd = [
                'airodump-ng',
                self.interface,
                '--bssid', self.target_bssid,
                '-w', self.temp_prefix,
                '--output-format', 'csv'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            while self.is_sniffing:
                try:
                    # Parse CSV output
                    csv_path = f"{self.temp_prefix}-01.csv"
                    with open(csv_path, 'r') as f:
                        lines = f.readlines()
                        self._parse_airodump_csv(lines)
                except (FileNotFoundError, IOError, ValueError):
                    pass
                
                time.sleep(0.5)
            
            process.terminate()
            
            # Cleanup temp files
            import glob
            for f in glob.glob(f"{self.temp_prefix}*"):
                try:
                    os.remove(f)
                except OSError:
                    pass
        
        except AirodumpNotInstalledError:
            raise
        except Exception as e:
            raise PacketCaptureError(f"airodump-ng failed: {str(e)}")
    
    def _sniff_scapy(self):
        """Capture using Scapy."""
        try:
            from scapy.all import sniff, Dot11, Dot11Beacon, Dot11ProbeReq
        except ImportError:
            raise DependencyMissingError(
                "scapy",
                "Install with: pip install scapy"
            )
        
        try:
            def packet_handler(packet):
                """Handle captured packet."""
                if not self.is_sniffing:
                    return
                
                # Extract client MAC from various frame types
                client_mac = None
                signal = None
                
                # Beacon frames: client MAC in receiver address
                if packet.haslayer(Dot11Beacon):
                    if packet.FCfield.to_DS and packet.addr2 != self.target_bssid:
                        client_mac = packet.addr2
                
                # Association response: client MAC in address 1
                if hasattr(packet, 'addr1') and hasattr(packet, 'addr2'):
                    if packet.addr2 == self.target_bssid:
                        client_mac = packet.addr1
                
                # Data frames: client MAC in address 2 (sender)
                if hasattr(packet, 'type') and packet.type == 2:  # Data frame
                    if hasattr(packet, 'addr1') and packet.addr1 == self.target_bssid:
                        client_mac = packet.addr2
                
                if client_mac:
                    self._process_client(client_mac, signal)
            
            # Start sniffing
            sniff(
                iface=self.interface,
                prn=packet_handler,
                stop_filter=lambda x: not self.is_sniffing,
                monitor=True
            )
        
        except Exception as e:
            raise PacketCaptureError(f"Scapy sniffing failed: {str(e)}")
    
    def _parse_airodump_csv(self, lines):
        """Parse airodump-ng CSV output."""
        in_clients = False
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('BSSID'):
                continue
            
            # Client section starts after empty line following AP section
            if line == '':
                in_clients = True
                continue
            
            if in_clients and line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    try:
                        client_mac = parts[0].upper()
                        signal = int(parts[3])
                        frames = int(parts[4])
                        
                        self._process_client(client_mac, signal)
                    except (ValueError, IndexError):
                        continue
    
    def _process_client(self, client_mac, signal=None):
        """
        Process detected client.
        
        Args:
            client_mac (str): Client MAC address
            signal (int): Signal strength in dBm (optional)
        """
        try:
            client_mac = normalize_mac_address(client_mac)
            
            # Duplicate detection
            current_time = time.time()
            packet_key = f"{client_mac}:{current_time}"
            
            # Clean old entries
            self.seen_packets = {
                k: v for k, v in self.seen_packets.items()
                if current_time - v < DUPLICATE_WINDOW
            }
            
            # Check if duplicate
            if client_mac in [p.split(':')[0] for p in self.seen_packets.keys()]:
                return
            
            self.seen_packets[packet_key] = current_time
            
            # Add/update client
            if client_mac not in self.captured_clients:
                self.captured_clients[client_mac] = {
                    'signal': signal,
                    'first_seen': current_time,
                    'last_seen': current_time,
                    'manufacturer': 'Unknown'
                }
                
                # Call callback for new client
                if self.client_callback:
                    self.client_callback(client_mac, signal, 'Unknown')
            else:
                self.captured_clients[client_mac]['last_seen'] = current_time
                if signal:
                    self.captured_clients[client_mac]['signal'] = signal
        
        except Exception:
            pass  # Silently skip malformed packets
    
    def get_client_count(self):
        """Get number of unique clients detected."""
        return len(self.captured_clients)
    
    def is_running(self):
        """Check if sniffer is running."""
        return self.is_sniffing and self.sniffer_thread.is_alive()
