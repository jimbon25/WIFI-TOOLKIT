"""
Device Fingerprinter - Device Identification
============================================

Identifies device types and manufacturers from MAC/probe requests.
"""

from .constants import MAC_OUI_DATABASE
from .utils import extract_oui, create_fingerprint_hash
from .exceptions import FingerprintingError


class DeviceFingerprinter:
    """Fingerprint and identify devices."""
    
    def __init__(self, oui_database=None):
        """
        Initialize fingerprinter.
        
        Args:
            oui_database (dict): MAC OUI to manufacturer mapping (None = use default)
        """
        self.oui_database = oui_database or MAC_OUI_DATABASE
        self.fingerprints_cache = {}
    
    def get_manufacturer(self, mac_address):
        """
        Get manufacturer from MAC address OUI.
        
        Args:
            mac_address (str): MAC address
            
        Returns:
            str: Manufacturer name or 'Unknown'
        """
        try:
            oui = extract_oui(mac_address)
            return self.oui_database.get(oui, 'Unknown')
        except Exception as e:
            raise FingerprintingError(f"Failed to extract manufacturer from {mac_address}: {str(e)}")
    
    def identify_device_type(self, mac_address, probe_requests=None):
        """
        Identify device type from MAC and optional probe data.
        
        Args:
            mac_address (str): MAC address
            probe_requests (list): Probe request SSIDs (optional)
            
        Returns:
            str: Device type (iPhone, Android, Laptop, etc)
        """
        try:
            manufacturer = self.get_manufacturer(mac_address)
            
            # Use manufacturer hints
            type_mapping = {
                'Apple': 'iPhone/iPad',
                'Samsung': 'Android',
                'Xiaomi': 'Android',
                'Motorola': 'Android',
                'Google': 'Pixel/Android',
                'OnePlus': 'Android',
                'Sony': 'Sony Device',
                'LG': 'LG Device',
                'Cisco': 'Network Device',
                'Hewlett': 'Printer/Device',
                'Dell': 'Laptop',
                'Toshiba': 'Laptop',
                'Asus': 'Laptop/Tablet',
                'Acer': 'Laptop',
                'Netgear': 'Router',
                'Huawei': 'Huawei Device'
            }
            
            for brand, device_type in type_mapping.items():
                if brand.lower() in manufacturer.lower():
                    return device_type
            
            # Analyze probe requests if available
            if probe_requests:
                device_type = self._analyze_probes(probe_requests)
                if device_type:
                    return device_type
            
            return 'Unknown Device'
        
        except Exception as e:
            raise FingerprintingError(f"Failed to identify device type: {str(e)}")
    
    def _analyze_probes(self, probe_requests):
        """
        Analyze probe requests for device hints.
        
        Args:
            probe_requests (list): SSIDs being probed
            
        Returns:
            str: Detected device type or None
        """
        if not probe_requests:
            return None
        
        probe_str = ' '.join(probe_requests).lower()
        
        # iPhone patterns
        iphone_keywords = ['iphone', 'ipad', 'apple', 'airpods']
        if any(kw in probe_str for kw in iphone_keywords):
            return 'iPhone/iPad'
        
        # Android patterns
        android_keywords = ['android', 'samsung', 'pixel', 'nexus', 'moto', 'xiaomi']
        if any(kw in probe_str for kw in android_keywords):
            return 'Android'
        
        # Laptop patterns
        laptop_keywords = ['windows', 'mac', 'linux', 'ubuntu', 'dell', 'hp', 'lenovo']
        if any(kw in probe_str for kw in laptop_keywords):
            return 'Laptop/Desktop'
        
        # IoT patterns
        iot_keywords = ['iot', 'smart', 'echo', 'alexa', 'google home']
        if any(kw in probe_str for kw in iot_keywords):
            return 'IoT Device'
        
        return None
    
    def create_fingerprint(self, mac_address, probe_requests=None, additional_data=None):
        """
        Create device fingerprint hash.
        
        Args:
            mac_address (str): MAC address
            probe_requests (list): Probe SSIDs (optional)
            additional_data (dict): Additional data (optional)
            
        Returns:
            str: Fingerprint hash
        """
        try:
            components = [mac_address]
            
            if probe_requests:
                components.extend(probe_requests)
            
            if additional_data:
                for key, value in additional_data.items():
                    components.append(f"{key}:{value}")
            
            fingerprint = create_fingerprint_hash(*components)
            self.fingerprints_cache[mac_address] = fingerprint
            
            return fingerprint
        
        except Exception as e:
            raise FingerprintingError(f"Failed to create fingerprint: {str(e)}")
    
    def get_fingerprint(self, mac_address):
        """
        Get cached fingerprint.
        
        Args:
            mac_address (str): MAC address
            
        Returns:
            str: Fingerprint or None
        """
        return self.fingerprints_cache.get(mac_address)
    
    def analyze_device(self, mac_address, signal_strength=None, probe_requests=None):
        """
        Comprehensive device analysis.
        
        Args:
            mac_address (str): MAC address
            signal_strength (int): Signal in dBm (optional)
            probe_requests (list): Probe requests (optional)
            
        Returns:
            dict: Complete device analysis
        """
        try:
            manufacturer = self.get_manufacturer(mac_address)
            device_type = self.identify_device_type(mac_address, probe_requests)
            fingerprint = self.create_fingerprint(mac_address, probe_requests)
            
            analysis = {
                'mac_address': mac_address,
                'manufacturer': manufacturer,
                'device_type': device_type,
                'fingerprint': fingerprint,
                'oui': extract_oui(mac_address),
                'signal_strength': signal_strength,
                'probe_requests': probe_requests,
                'confidence': self._calculate_confidence(manufacturer, device_type)
            }
            
            return analysis
        
        except Exception as e:
            raise FingerprintingError(f"Analysis failed: {str(e)}")
    
    def _calculate_confidence(self, manufacturer, device_type):
        """
        Calculate identification confidence level.
        
        Args:
            manufacturer (str): Identified manufacturer
            device_type (str): Identified device type
            
        Returns:
            float: Confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Manufacturer found
        if manufacturer != 'Unknown':
            confidence += 0.3
        
        # Device type specific
        if device_type != 'Unknown Device':
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def batch_fingerprint(self, mac_list):
        """
        Fingerprint multiple MACs.
        
        Args:
            mac_list (list): List of MAC addresses
            
        Returns:
            list: List of fingerprints
        """
        return [self.create_fingerprint(mac) for mac in mac_list]
    
    def get_device_profile(self, mac_address):
        """
        Get complete device profile.
        
        Args:
            mac_address (str): MAC address
            
        Returns:
            dict: Device profile
        """
        try:
            return {
                'mac_address': mac_address,
                'oui': extract_oui(mac_address),
                'manufacturer': self.get_manufacturer(mac_address),
                'probable_device_type': self.identify_device_type(mac_address),
                'fingerprint': self.get_fingerprint(mac_address),
                'is_common_device': self._is_common_device(mac_address)
            }
        except Exception as e:
            raise FingerprintingError(f"Failed to create profile: {str(e)}")
    
    def _is_common_device(self, mac_address):
        """
        Check if this is a commonly seen device.
        
        Args:
            mac_address (str): MAC address
            
        Returns:
            bool: True if common/known device
        """
        manufacturer = self.get_manufacturer(mac_address)
        common_brands = ['Apple', 'Samsung', 'Google', 'Microsoft', 'Cisco', 'Netgear']
        return any(brand.lower() in manufacturer.lower() for brand in common_brands)
    
    def clear_cache(self):
        """Clear fingerprint cache."""
        self.fingerprints_cache.clear()
