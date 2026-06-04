"""
Configuration Constants for Rogue AP Detection
==============================================

All tunable parameters in one place.
"""

import os

# ============================================================================
# DETECTION PARAMETERS
# ============================================================================

# Maximum time to wait for first client detection (seconds)
DETECTION_TIMEOUT = 300  # 5 minutes

# Minimum signal strength threshold (dBm)
# Range: -30 (very strong) to -90 (very weak)
SIGNAL_THRESHOLD = -75

# Packet buffer size before batch processing
PACKET_BUFFER_SIZE = 1000

# Database transaction batch size
DB_BATCH_SIZE = 50

# Duplicate client check window (seconds)
# Ignore duplicate MAC detections within this window
DUPLICATE_WINDOW = 2

# ============================================================================
# PATHS & STORAGE
# ============================================================================

# Get module directory
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(MODULE_DIR, 'data')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')

# Database file
DATABASE_PATH = os.path.join(DATA_DIR, 'clients.db')
DATABASE_BACKUP_PATH = os.path.join(DATA_DIR, 'clients_backup.db')

# Export paths (auto-created)
JSON_EXPORT_PATH = os.path.join(DATA_DIR, 'clients.json')
CSV_EXPORT_PATH = os.path.join(DATA_DIR, 'clients.csv')

# Log file
LOG_FILE = os.path.join(LOGS_DIR, 'detection.log')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# ============================================================================
# MAC OUI DATABASE (Manufacturer lookup)
# ============================================================================

# Common manufacturers (can be expanded)
MAC_OUI_DATABASE = {
    '00:1A:2B': 'Cisco Systems',
    '00:03:47': 'Huawei Technologies',
    '00:04:9A': 'Netgear',
    '00:05:1C': 'Intel',
    '00:0B:85': 'Nortel Networks',
    '00:11:22': 'Apple Inc.',
    '00:15:E9': 'Sony Ericsson',
    '00:16:B4': 'Hewlett Packard',
    '00:18:F3': 'Acer',
    '00:1D:E0': 'Motorola',
    '00:21:5C': 'Asus',
    '00:23:6C': 'Dell',
    '00:24:2B': 'Samsung Electronics',
    '00:25:B3': 'LG Electronics',
    '00:26:5A': 'Toshiba',
    '00:30:53': 'Blackberry',
    '50:9F:27': 'Apple Inc. (iPhone)',
    '58:A0:CB': 'Apple Inc. (iPad)',
    '60:1D:8E': 'Samsung Galaxy',
    '9C:37:F5': 'Amazon AWS',
    'B4:CE:F6': 'Google Android',
    'E0:55:3D': 'OnePlus',
    'F4:4E:FD': 'Xiaomi',
}

# ============================================================================
# LOGGING
# ============================================================================

# Log levels
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'
LOG_LEVEL_CRITICAL = 'CRITICAL'

# Default log level
DEFAULT_LOG_LEVEL = LOG_LEVEL_INFO

# Log format
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================================================
# DETECTION MODES
# ============================================================================

# Detection methods
DETECTION_MODE_AIRODUMP = 'airodump'  # airodump-ng based
DETECTION_MODE_SCAPY = 'scapy'         # Scapy packet sniffing
DETECTION_MODE_ARP = 'arp'             # ARP monitoring

# Default method (fallback chain)
DEFAULT_DETECTION_MODES = [
    DETECTION_MODE_AIRODUMP,
    DETECTION_MODE_SCAPY,
    DETECTION_MODE_ARP
]

# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

# Color codes (for terminal output)
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_RESET = '\033[0m'
COLOR_BOLD = '\033[1m'

# Signal strength interpretation
SIGNAL_STRENGTH_EXCELLENT = (-30, -50)  # dBm range
SIGNAL_STRENGTH_GOOD = (-50, -60)
SIGNAL_STRENGTH_FAIR = (-60, -70)
SIGNAL_STRENGTH_WEAK = (-70, -80)
SIGNAL_STRENGTH_POOR = (-80, -100)

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

# SQL for creating tables
SQL_CREATE_CLIENTS_TABLE = """
CREATE TABLE IF NOT EXISTS connected_clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address TEXT UNIQUE NOT NULL,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signal_strength INTEGER,
    data_frames INTEGER DEFAULT 0,
    device_type TEXT,
    manufacturer TEXT,
    fingerprint TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

SQL_CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS session_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    mac_address TEXT NOT NULL,
    signal_strength INTEGER,
    data_bytes INTEGER DEFAULT 0,
    details TEXT,
    FOREIGN KEY (mac_address) REFERENCES connected_clients(mac_address)
)
"""

SQL_CREATE_INDEX_MAC = "CREATE INDEX IF NOT EXISTS idx_mac_address ON connected_clients(mac_address)"
SQL_CREATE_INDEX_TIMESTAMP = "CREATE INDEX IF NOT EXISTS idx_timestamp ON session_logs(timestamp)"
SQL_CREATE_INDEX_EVENT = "CREATE INDEX IF NOT EXISTS idx_event_type ON session_logs(event_type)"

# ============================================================================
# ALERT THRESHOLDS
# ============================================================================

# Alert triggers
ALERT_ON_CLIENT_CONNECT = True
ALERT_ON_HIGH_DATA_VOLUME = True
ALERT_ON_SUSPICIOUS_PROBES = True

# Data volume threshold (MB) before alert
HIGH_DATA_VOLUME_THRESHOLD = 10

# ============================================================================
# ANONYMITY SETTINGS
# ============================================================================

# Keep all traces anonymous - no identifying information stored
ANONYMIZE_LOGS = True
OBFUSCATE_MAC_IN_OUTPUT = False  # Set to True to mask real MACs
MAC_OBFUSCATION_CHAR = '*'

# Do not store detector operator information
STORE_OPERATOR_INFO = False

# Encrypt sensitive database fields
ENCRYPT_SENSITIVE_DATA = False  # Can be enabled for extra security
