# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.11.1] - 2025-11-14

### Added
- **Hybrid Attack Feature (Deauth + Beacon Flood)**: New advanced attack mode
- **Hybrid Attack SSID File Picker**: Auto-discovery of SSID list files across 5 search locations with interactive menu selection. Users can now choose from multiple SSID lists (default, aggressive, stealth, or custom).
- **Hybrid Attack Progress Visualization**: Real-time progress display for beacon flood attacks:
- Multi-threaded orchestration: 1 thread per target deauth + 1 beacon flood thread
  - Network scanning with target selection
  - Support for flexible SSID list loading from external files
  - Interactive menu for duration, target selection, and attack configuration
  - Integrated into main menu as option 5 in `show_attack_suite_menu()`
- **SSID List Flexibility**: Enhanced beacon flood to support external SSID files with automatic fallback to hardcoded default (20 SSIDs) if no file found.
- **Test SSID Files**: Created two sample SSID lists for different attack strategies:
  - `ssidlist_aggressive.txt`: 15 aggressive/noisy network names
  - `ssidlist_stealth.txt`: 13 stealth/hidden network names
- **Hybrid Attack Documentation**: Comprehensive guides and quick references for the new hybrid attack feature (3 documentation files, 42 KB total).
  - Timed attacks: 50-character progress bar with percentage and countdown timer
  - Continuous mode: Rotating spinner animation with elapsed time counter
  - Updates every 1 second for smooth visual feedback

## [2.11.0] - 2025-11-13

### Changed
- **UI Modernization - Modern Minimalist Design**: Complete visual redesign for cleaner:
  - Converted multi-line status bar to compact single-line format
  - Updated main menu to clean table layout with type indicators
  - Refined all sub-menus for consistency and readability
  - Cleaned up error/info messages with consistent label format

### Added
- **Hierarchical Menu Structure with Sub-Menus**: Refactored main menu to improve UX and tool organization:
  - Reduced main menu from 15 items to 10 items
  - Implemented 4 context-specific sub-menus for better tool grouping
  - Clearer categorization: Network Scanning, WiFi Attacks, Handshakes, Web Security
- **Hybrid Attack in RATA Lite Menu**: Added Hybrid Attack (Deauth + Beacon Flood) as option 13 in `rata_lite.py` with download prompt, promoting the full version feature.

## [2.10.0] - 2025-11-12

### Added
- **Flexible Exit Options**: Implemented a new exit sub-menu in the main toolkit, allowing users to choose between a full network cleanup/restore (recommended) or a quick exit without altering network settings.
- **Structured SQLmap Output Parsing**: Enhanced `sqlmap_tool.py` to leverage `sqlmap`'s JSON output for database listing, table listing, and guided data dumping. This significantly improves the robustness and reliability of parsing `sqlmap` results, reducing fragility to output format changes.
- **Formatted SQLmap Dump Display**: Added a helper function (`_print_dumped_data`) in `sqlmap_tool.py` to present JSON-parsed `sqlmap` dump results in a clear, formatted table.

### Changed
- **UI Consistency (Menu Navigation)**: Standardized menu navigation across `nmap_tool.py`, `sqlmap_tool.py` to use `getch()` for single-key selections. This provides a more responsive and consistent user experience, aligning with the main toolkit's menu.

### Fixed
- **Evil Twin Cleanup File Path**: Corrected a bug in `evilTwin.py` where a hardcoded, incorrect temporary file path was used during `dnsmasq` configuration cleanup, ensuring proper file removal.
- **SQLmap Crawl Hang**: Resolved an issue in `sqlmap_tool.py`'s `_crawl_and_scan` function where `sqlmap` would hang due to interactive prompts. The `--batch` flag has been added to ensure non-interactive execution.

## [2.9.8] - 2025-11-10

### Added
- **Automated Vulnerability Scanner (Nuclei) Integration**: Integrated the Nuclei vulnerability scanner as a new menu option.
- **Advanced Nuclei Scan Options**: Implemented advanced options for Nuclei, including filtering by severity exclusion, template listing/display, and redirect control.

## [2.9.7] - 2025-11-10

### Added
- **Geolocation Attack (Seeker) Integration**: Integrated the [Seeker](https://github.com/thewhiteh4t/seeker) tool as a new menu option (`11`). This feature automates the process of starting an `ngrok` tunnel and launching Seeker to obtain a target's geographical location by sending them a link.
- **Public "Lite" Script (`rata_lite.py`)**: Created a separate, distributable "lite" version of the script. This version displays the full menu for UX consistency but only enables the Geolocation feature, prompting users to download the full version for other features. This protects the main source code from being exposed.
- **Seeker Dependency Checker**: Added a user-friendly dependency check for `php`, `ssh`, and `ngrok` that runs before the Geolocation attack is launched, guiding users on installation if needed.

### Fixed
- **Multi-Digit Menu Selection**: Replaced the `getch()` input method with the standard `input()` in the main menu loop. This resolves a critical bug where the script could not process two-digit menu selections (e.g., "11"), making the new feature inaccessible. Users now press Enter after their choice.

## [2.9.6] - 2025-11-03

### Added
- **SQL Injection (sqlmap) Integration**: Added a comprehensive, menu-driven wrapper for `sqlmap`. This feature automates complex tasks, providing a "Guided Dump" wizard to step through database enumeration and a powerful "Auto-Discover & Scan" option to crawl and test entire sites for SQL injection vulnerabilities.
- **Network Mapper (nmap) Integration**: Integrated `nmap` as a new menu option for advanced network discovery and security auditing. It includes pre-configured scans for quick host discovery, intense service/OS detection, and automated vulnerability scanning using the `vulners` script.

## [2.9.5] - 2025-11-02

### Fixed
- **Network Bandwidth Limiter**: Resolved a critical bug that caused the limiter feature (Menu 0) to fail on startup. The integration with `evillimiter` has been stabilized, ensuring all its dependencies and modules are loaded correctly.

## [2.9.4] - 2025-11-01

### Added
- **Network Bandwidth Limiter (Evil Limiter) Integration**: Integrated the powerful [Evil Limiter](https://github.com/bitbrute/evillimiter) tool as a new menu option. This feature allows users to monitor, analyze, and limit the bandwidth of devices on their local network. It operates on a managed (non-monitor mode) interface, requiring the selection of an active network connection.

### Changed
- **Main Menu Structure**: Added a new menu option `[0]` for the Network Bandwidth Limiter, adjusting the main menu selection prompt accordingly.

## [2.9.3] - 2025-10-31

### Changed
- **Startup Workflow**: Refactored the script's startup sequence. The script now opens directly to the main menu. Interface selection and monitor mode activation are performed on-demand only when a feature requires them. This prevents `airmon-ng check kill` from running unnecessarily and disrupting other network connections at launch.
- **Dependency Check**: Improved the initial dependency check to include optional tools (`hostapd`, `dnsmasq`). The script now shows a non-blocking warning if optional tools for the Evil Twin attack are missing, rather than failing later when the feature is used.

### Fixed
- **WiFi Jamming Attack**: Fixed a critical bug where the attack was unreliable due to a race condition when using `mdk4` in a loop. The feature has been refactored to use multiple `aireplay-ng` processes for a more stable and effective multi-target deauthentication attack.

## [2.9.2] - 2025-10-30

### Fixed
- **Evil Twin `dnsmasq` Conflict**: Resolved "Address already in use" error by flushing IP addresses on the AP interface and aggressively terminating any lingering `dnsmasq` processes before starting a new one.
- **Evil Twin `systemd-resolved` Management**: Implemented explicit stopping of `systemd-resolved` before starting `dnsmasq` and restarting it during cleanup to prevent port conflicts and ensure proper system state restoration.

### Added
- **Evil Twin Internet Access (IP Forwarding & NAT)**: Implemented IP forwarding and NAT (`iptables`) rules to provide internet access to clients connected to the fake Access Point.

### Changed
- **Evil Twin Internet Interface Detection**: Improved the detection logic for the internet-connected interface by excluding the deauthentication and fake AP interfaces from consideration, ensuring the correct interface is identified for NAT.

### Important Note
- **Evil Twin Internet Access Requirement**: Providing internet access to clients connected to the fake AP now requires a *third* network interface that is actively connected to the internet. If only two wireless adapters are available, clients will be able to connect to the fake AP but will not have internet access.

## [2.9.1] - 2025-10-30

### Fixed
- **Evil Twin Attack**: Resolved a critical logic flaw where a single wireless interface was used for both creating the Access Point (requiring managed mode) and deauthenticating clients (requiring monitor mode). The attack now correctly utilizes two separate wireless interfaces.
- **Evil Twin `dnsmasq` Conflict**: Fixed an issue where `dnsmasq` would fail to start its DNS service due to a port conflict with `systemd-resolved` on port 53. `dnsmasq` is now configured to bind only to the fake AP's interface IP.
- **Evil Twin Cleanup**: The cleanup process now properly restores the secondary interface (used for the AP) back to managed mode upon exiting the attack.

### Changed
- **Evil Twin Workflow**: The workflow has been updated to be more intuitive. The primary interface selected at the start of the script is now used for deauthentication (monitor mode), and the user is prompted to select a secondary interface to be used for the fake Access Point (managed mode).

## [2.9.0] - 2025-10-29

### Added
- **Evil Twin Attack (WPA2 Support & Client Notification)**: Enhanced the Evil Twin Attack to support WPA2-encrypted fake APs using `hostapd`. Users can now input the WPA2 password for the target AP.
- Implemented real-time client connection notifications in the terminal when devices connect to the fake AP.
- **Evil Twin Attack (Core Implementation)**: Implemented core functionality including AP scanning, target selection, fake AP creation, DHCP server setup, and client deauthentication.

## [2.8.3.1] - 2025-10-29

### Fixed
- Resolved unexpected indentation errors in `_combined_dos_attack` and `run_handshake_capture` functions.
- Corrected display formatting for vulnerability assessment columns in target selection menus to ensure proper alignment.

## [2.8.3] - 2025-10-29

### Added
- **Automated Vulnerability Assessment**: Implemented a new feature to analyze and label WiFi networks based on their vulnerability (e.g., `[HIGHLY VULNERABLE]`, `[POTENTIAL TARGET]`, `[SECURE]`). Networks are now sorted by vulnerability priority in target selection menus.
    - This feature is integrated into the target selection for `Launch Targeted Attack`, `Automated Handshake Capture`, and `Smart Adaptive Attack`.
    - **Note on WPS Detection**: Due to limitations in `airodump-ng` CSV output, automatic detection and labeling for `[WPS VULNERABLE]` is not yet supported.

## [2.8.2.2] - 2025-10-29

### Fixed
- Corrected `mdk4` broadcast deauthentication command by removing the unsupported `-m` option, ensuring proper execution.

## [2.8.2] - 2025-10-29

### Changed
- **Optimized mdk4 Deauthentication Flood**: Enhanced the broadcast deauthentication attack by adding `-s 1000` for 1000 packets per second. Removed the unsupported `-m` option.
- **Selective Monitor Mode**: Modified `set_monitor_mode` in the Python script (`wifiTools_2.py`). It no longer runs `airmon-ng check kill` globally, preventing the user's primary WiFi interface from being disconnected when another interface is put into monitor mode.

### Added
- Created the `wifiTools_2.py` script as a variant for this selective monitor mode functionality.

## [2.8.1] - 2025-10-28

### Added
- **Smart Adaptive Attack**: Implemented a new targeted, adaptive DoS attack mode. This feature first scans for networks with active clients, allows the user to select a target, and then initiates an attack while simultaneously monitoring its own effectiveness. It automatically escalates to more aggressive strategies if the current one is not successful at disconnecting clients.

### Changed
- The `Combined DoS Attack` option in the `DoS Attack` menu has been repurposed to launch the new `Smart Adaptive Attack`.
- Updated the UI version number to `2.8.1`.

## [2.8.0] - 2025-10-28

### Added
- **Automated WPA/WPA2 Handshake Capture**: New feature in the main menu to automate the entire process of capturing a handshake. The script now scans for targets, runs `airodump-ng` and `aireplay-ng` in coordination, monitors for the handshake, and saves the `.cap` file to a new `handshakes/` directory.
- **Process Tracking and Management**: All background attack processes (`subprocess.Popen`) are now tracked in a central list (`self.active_processes`).

### Changed
- **UI/UX Overhaul**:
    - The main menu and header have been completely redesigned for a cleaner, more professional, and minimalist look.
    - Removed all special characters and emojis from the menu for better readability and compatibility.
    - Standardized on `getch()` for single-key menu selections across all relevant menus (`DoS Attack`, `Stealth Mode`), creating a more responsive and consistent user experience.
- **Improved `cleanup()` Function**: The global cleanup function now forcefully terminates all tracked background processes upon exit, preventing orphaned/zombie processes.
- **Enhanced Attack Reliability**: Timed attacks (`_eapol_flood_attack`, etc.) now correctly track their processes, ensuring they are properly terminated.

### Fixed
- **Orphaned Processes**: Fixed a critical bug where interrupting the script during timed attacks or scans would leave `mdk4` or `airodump-ng` processes running in the background.
- **UI Inconsistency**: Fixed inconsistent user input methods by replacing `input()` with `getch()` in several menus.