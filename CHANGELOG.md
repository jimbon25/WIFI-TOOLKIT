# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
