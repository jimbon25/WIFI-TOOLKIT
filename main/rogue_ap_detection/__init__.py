"""
Rogue AP Detection Module
========================

Anonymous client detection for rogue access points.
Fully modular and independent from main WiFi toolkit.

Classes:
    - RogueAPDetector: Main orchestrator
    - PacketSniffer: Low-level packet capture
    - ClientTracker: Database & tracking
    - DeviceFingerprinter: Device identification
    - DetectionLogger: Structured logging

Usage:
    from rogue_ap_detection import RogueAPDetector
    
    detector = RogueAPDetector(
        rogue_bssid="AA:BB:CC:DD:EE:FF",
        interface="wlan0"
    )
    detector.start_detection()
    # ... monitor ...
    report = detector.stop_detection()
"""

__version__ = "1.0.0"
__author__ = "Anonymous"

from .detector import RogueAPDetector
from .packet_sniffer import PacketSniffer
from .client_tracker import ClientTracker
from .device_fingerprint import DeviceFingerprinter
from .logger import DetectionLogger
from .exceptions import (
    InterfaceNotFoundError,
    PacketCaptureError,
    DatabaseError,
    FingerprintingError
)

__all__ = [
    'RogueAPDetector',
    'PacketSniffer',
    'ClientTracker',
    'DeviceFingerprinter',
    'DetectionLogger',
    'InterfaceNotFoundError',
    'PacketCaptureError',
    'DatabaseError',
    'FingerprintingError'
]
