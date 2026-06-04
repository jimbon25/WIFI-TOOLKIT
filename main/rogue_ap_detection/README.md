"""
README - Rogue AP Detection Module
=================================

ANONYMOUS CLIENT DETECTION FOR ROGUE ACCESS POINTS

This module detects and tracks devices that connect to your rogue AP,
while maintaining complete anonymity - clients never know who created the AP.

================================================================================
QUICK START
================================================================================

Basic usage:

    from rogue_ap_detection import RogueAPDetector
    
    # Initialize detector
    detector = RogueAPDetector(
        rogue_bssid="AA:BB:CC:DD:EE:FF",  # Your rogue AP's BSSID
        interface="wlan0",                 # Monitor mode interface
        timeout=300                        # 5 minutes
    )
    
    # Start detection
    detector.start_detection()
    
    # Monitor clients...
    print(f"Clients detected: {len(detector.get_connected_clients())}")
    
    # Stop and get report
    report = detector.stop_detection()
    print(f"Total clients: {report['total_clients']}")

================================================================================
FEATURES
================================================================================

✅ ANONYMOUS MODE (Fully Unidentifiable):
   - No operator information stored
   - No logs of who ran the detection
   - Minimal data retention
   - Easy cleanup/deletion

✅ REAL-TIME DETECTION:
   - Track clients as they connect
   - Monitor signal strength changes
   - Detect data transmission patterns
   - Identify device types/manufacturers

✅ COMPREHENSIVE DATA COLLECTION:
   - MAC addresses
   - Signal strength (RSSI)
   - Device manufacturers (from MAC OUI)
   - Probable device types (phone, laptop, etc)
   - Connection timing
   - Data frame counts

✅ ROBUST STORAGE:
   - SQLite database (clients.db)
   - JSON export
   - CSV export
   - Timestamped logging

✅ MODULAR ARCHITECTURE:
   - Independent components
   - Easy to extend/customize
   - Clear separation of concerns
   - Production-ready error handling

================================================================================
ARCHITECTURE
================================================================================

detector.py
    └─ RogueAPDetector (main orchestrator)
       ├─ PacketSniffer (captures packets)
       ├─ ClientTracker (stores in database)
       ├─ DeviceFingerprinter (identifies devices)
       └─ DetectionLogger (structured logging)

File Structure:
    rogue_ap_detection/
    ├─ __init__.py              (package exports)
    ├─ detector.py              (main class)
    ├─ packet_sniffer.py        (packet capture)
    ├─ client_tracker.py        (database layer)
    ├─ device_fingerprint.py    (device identification)
    ├─ logger.py                (event logging)
    ├─ constants.py             (configuration)
    ├─ exceptions.py            (error types)
    ├─ utils.py                 (helper functions)
    └─ data/                    (auto-created)
       ├─ clients.db            (SQLite database)
       ├─ clients.json          (JSON export)
       ├─ clients.csv           (CSV export)
       └─ logs/                 (log files)

================================================================================
USAGE EXAMPLES
================================================================================

EXAMPLE 1: Basic Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    from rogue_ap_detection import RogueAPDetector
    import time
    
    detector = RogueAPDetector(
        rogue_bssid="AA:BB:CC:DD:EE:FF",
        interface="wlan0"
    )
    
    detector.start_detection()
    
    # Run for 2 minutes
    time.sleep(120)
    
    report = detector.stop_detection()
    
    print(f"Clients detected: {report['total_clients']}")
    print(f"Manufacturers: {report['statistics']['manufacturers']}")

EXAMPLE 2: Real-time Monitoring
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    detector = RogueAPDetector("AA:BB:CC:DD:EE:FF", "wlan0")
    detector.start_detection()
    
    while True:
        clients = detector.get_connected_clients()
        stats = detector.get_statistics()
        
        print(f"Connected: {len(clients)} | Elapsed: {stats['elapsed_time']:.1f}s")
        
        for client in clients:
            print(f"  - {client['mac_address']}: {client['manufacturer']}")
        
        time.sleep(2)

EXAMPLE 3: Export Data
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    detector = RogueAPDetector("AA:BB:CC:DD:EE:FF", "wlan0")
    detector.start_detection()
    time.sleep(60)
    detector.stop_detection()
    
    # Export as JSON
    json_data = detector.export_report(format='json')
    with open('clients.json', 'w') as f:
        f.write(json_data)
    
    # Export as CSV
    csv_data = detector.export_report(format='csv')
    with open('clients.csv', 'w') as f:
        f.write(csv_data)
    
    # Export logs
    logs = detector.export_logs(format='json')

EXAMPLE 4: Anonymous Cleanup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    # Get report first
    report = detector.stop_detection()
    data = detector.export_report()
    
    # Then clean up - delete all traces
    detector.cleanup(delete_database=True)
    
    # Database file is now deleted, no traces left

================================================================================
CONFIGURATION
================================================================================

Tunable parameters in constants.py:

    DETECTION_TIMEOUT = 300          # Max detection time (seconds)
    SIGNAL_THRESHOLD = -75           # Min signal to track (dBm)
    PACKET_BUFFER_SIZE = 1000        # Packet buffer size
    DB_BATCH_SIZE = 50               # Database batch size
    DUPLICATE_WINDOW = 2             # Duplicate check window (seconds)
    
    ANONYMIZE_LOGS = True            # Anonymize in logs
    OBFUSCATE_MAC_IN_OUTPUT = False  # Mask MACs in terminal output
    STORE_OPERATOR_INFO = False      # Never store who ran it

================================================================================
CAPTURED DATA
================================================================================

Per client, the system captures:

    ✓ MAC Address (unique device identifier)
    ✓ Signal Strength (RSSI in dBm)
    ✓ First Seen (connection timestamp)
    ✓ Last Seen (last activity timestamp)
    ✓ Manufacturer (from MAC OUI database)
    ✓ Device Type (identified from manufacturer/probes)
    ✓ Fingerprint Hash (unique device signature)
    ✓ Data Frames Count (activity indicator)
    ✓ Connection Status (active/disconnected)

Example client record:
    {
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "manufacturer": "Apple Inc.",
        "device_type": "iPhone/iPad",
        "signal_strength": -45,
        "first_seen": "2025-11-22 10:30:00",
        "last_seen": "2025-11-22 10:35:45",
        "data_frames": 142,
        "fingerprint": "a1b2c3d4e5f6g7h8",
        "is_active": true
    }

================================================================================
DATABASE SCHEMA
================================================================================

TABLE: connected_clients
    id                  - Unique ID
    mac_address         - Client MAC (unique)
    first_seen          - Connection timestamp
    last_seen           - Last activity timestamp
    signal_strength     - Current RSSI (dBm)
    data_frames         - Data frame count
    device_type         - Identified device type
    manufacturer        - MAC OUI manufacturer
    fingerprint         - Unique fingerprint hash
    is_active           - Connection status
    created_at          - Record creation time

TABLE: session_logs
    id                  - Unique ID
    timestamp           - Event timestamp
    event_type          - Event type (connected, data_tx, disconnected)
    mac_address         - Client MAC (FK)
    signal_strength     - Signal at event time
    data_bytes          - Bytes transferred
    details             - JSON details

Indices:
    - idx_mac_address (for fast client lookup)
    - idx_timestamp (for time-based queries)
    - idx_event_type (for event filtering)

================================================================================
API REFERENCE
================================================================================

RogueAPDetector()
  ├─ start_detection()           - Begin monitoring
  ├─ stop_detection()            - Stop and get report
  ├─ get_connected_clients()     - Get active clients
  ├─ get_all_clients()           - Get all clients (including disconnected)
  ├─ get_client_details(mac)     - Get detailed info
  ├─ get_statistics()            - Get stats
  ├─ export_report(format)       - Export as json/csv/dict
  ├─ export_logs(format)         - Export event logs
  ├─ cleanup(delete_database)    - Clean up resources
  └─ is_detecting                - Status flag

Example: Get client info
    
    stats = detector.get_statistics()
    print(f"Total clients: {stats['clients_detected']}")
    print(f"Time elapsed: {stats['elapsed_time']:.1f}s")
    print(f"Manufacturers: {stats['manufacturers']}")
    
    clients = detector.get_connected_clients()
    for client in clients:
        details = detector.get_client_details(client['mac_address'])
        print(f"{client['manufacturer']}: {details['device_type']}")

================================================================================
ERROR HANDLING
================================================================================

The module includes robust error handling with custom exceptions:

    InterfaceNotFoundError       - Interface not available
    InterfaceNotInMonitorMode   - Interface not in monitor mode
    PermissionDeniedError       - Need sudo/elevated privileges
    PacketCaptureError          - Packet capture failed
    DatabaseError               - Database operation failed
    FingerprintingError         - Device identification failed
    DependencyMissingError      - Required tool not installed
    
Example:

    from rogue_ap_detection.exceptions import InterfaceNotFoundError
    
    try:
        detector = RogueAPDetector("AA:BB:CC:DD:EE:FF", "wlan0")
        detector.start_detection()
    except InterfaceNotFoundError as e:
        print(f"Error: {e}")
        # Handle error

================================================================================
INTEGRATION WITH WIFI TOOLKIT
================================================================================

The detection module is designed to work alongside beacon flood attacks.
Example integration:

    # In wifi_toolkit.py beacon flood method:
    
    from rogue_ap_detection import RogueAPDetector
    
    def _beacon_flood_attack(self, ...):
        # Start beacon flood
        # ...existing code...
        
        # ALSO start client detection
        detector = RogueAPDetector(
            rogue_bssid=self.rogue_ap_mac,
            interface=interface
        )
        detector.start_detection()
        
        try:
            # Run both simultaneously
            while not stop_event.is_set():
                time.sleep(1)
                clients = detector.get_connected_clients()
                print(f"[*] {len(clients)} clients connected")
        
        finally:
            # Get final report
            report = detector.stop_detection()
            self._save_attack_report(report)

================================================================================
ANONYMITY & PRIVACY
================================================================================

This module is designed for ANONYMOUS operation:

✅ NO OPERATOR TRACKING:
   - No usernames stored
   - No timestamp of who ran it
   - No identifying information
   - Anonymous by design

✅ MINIMAL DATA RETENTION:
   - Only client device data (MAC, signal, type)
   - No operator info
   - Easy deletion (cleanup(delete_database=True))

✅ OPTIONAL ANONYMIZATION:
   - ANONYMIZE_LOGS = True (default)
   - Only partial MACs in logs
   - Can obfuscate MACs in output

✅ FULL CLEANUP:
   - Delete database
   - Clear all traces
   - Clean shutdown

Example:

    # After getting report, delete all traces
    report = detector.stop_detection()
    
    # Export data to another location first
    backup = detector.export_report()
    
    # Clean up everything
    detector.cleanup(delete_database=True)
    # Database file deleted, no traces left on system

================================================================================
LEGAL & ETHICAL
================================================================================

⚠️  IMPORTANT DISCLAIMER:

This tool is for AUTHORIZED penetration testing only:

✓ Authorized security testing
✓ Authorized research
✓ Your own networks/devices
✓ With explicit permission from network owner

✗ Unauthorized network monitoring
✗ Collecting data without consent
✗ Using on networks you don't own/control

This tool captures device information from clients connecting to a rogue AP.
Use responsibly and only in authorized contexts (pentesting, security research, etc).

See LICENSE file for full terms.

================================================================================
TROUBLESHOOTING
================================================================================

Problem: "Interface not in monitor mode"
Solution: Put interface in monitor mode first:
    sudo airmon-ng start wlan0

Problem: "No clients detected"
Solution: 
    - Verify rogue AP is actually running
    - Check BSSID is correct
    - Ensure clients are actually connecting
    - Check WiFi range

Problem: "Permission denied accessing WiFi interface"
Solution: Run with sudo:
    sudo python script.py

Problem: "airodump-ng not found"
Solution: Install aircrack-ng suite:
    sudo apt install aircrack-ng

================================================================================
DEPENDENCIES
================================================================================

Core (included):
    - sqlite3 (Python standard library)
    - json (Python standard library)
    - threading (Python standard library)

Optional:
    - scapy (pip install scapy) - for Scapy-based packet capture
    - aircrack-ng (sudo apt install aircrack-ng) - for airodump-ng method

================================================================================
VERSION & LICENSE
================================================================================

Version: 1.0.0
License: See LICENSE file
Author: Anonymous

The module is fully anonymized and unattributable by design.

================================================================================
"""

print(__doc__)
