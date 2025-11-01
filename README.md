# WIFI-TOOLKIT - A WiFi Pentest Utility

<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![Integrated: Evil Limiter](https://img.shields.io/badge/Integrated-Evil_Limiter-blue.svg?style=for-the-badge&logo=github)
![GitHub Stars](https://img.shields.io/github/stars/jimbon25/WIFI-TOOLKIT?style=social)

</div>

### Table of Contents
*   [Disclaimer](#-disclaimer)
*   [Project Description](#project-description)
*   [Key Features](#key-features)
*   [Screenshots](#screenshots)
*   [Requirements](#requirements)
*   [Platform Support](#platform-support)
*   [Usage](#usage)
*   [Termux Support](#termux-support)
*   [Support the Project](#support-the-project)
*   [Accessing the Source Code](#accessing-the-source-code)
*   [Credits](#credits)
*   [License](#license)
*   [Changelog](CHANGELOG.md)
*   [User Guide (PANDUAN)](PANDUAN.md)
*   [Security Policy](SECURITY.md)

## ⚠️ Disclaimer
This tool is intended for educational and authorized security testing purposes only. The author is not responsible for any illegal or malicious use of this program. By using this software, you agree to take full responsibility for your actions. **Use at your own risk.**

## Project Description
WIFI-TOOLKIT is a comprehensive, menu-driven utility designed for Wi-Fi penetration testing. It simplifies complex network attacks and provides a user-friendly interface for performing network scanning, DoS attacks, handshake captures, and more.

## Key Features

**Note:** Many features of this toolkit, especially those related to scanning and attacking Wi-Fi networks, require a compatible wireless adapter that supports **monitor mode**.

*   **Wireless Interface Detection & Selection:** Automatically detects interfaces supporting monitor mode.
*   **MAC Address Spoofing:** Change your MAC address for anonymity.
*   **Monitor Mode Activation:** Easily switch your card to monitor mode.
*   **Automated Handshake Capture (WPA/WPA2):** Captures 4-way handshakes and saves them to the `handshakes/` folder.
*   **Network Scanning (airodump-ng):** Scans for Wi-Fi networks to identify APs and clients.
*   **Massive & Targeted Attacks:**
    *   **Deauthentication Attack (mdk4/aireplay-ng):** Broadcast or targeted deauth attacks.
    *   **Beacon Flood Attack (mdk4):** Create thousands of fake APs to disrupt network scanners.
*   **Evil Twin Attack:** Creates a fake AP mimicking a target network, with WPA2 support, to capture client traffic (requires 2 Wi-Fi adapters).
*   **Automated Vulnerability Assessment:** Analyzes and labels networks by vulnerability level.
*   **Network Bandwidth Limiter (Evil Limiter):** Integrates the powerful Evil Limiter tool to monitor, analyze, and limit bandwidth of devices on your local network (requires a managed interface).
*   **UI/UX Improvements:** A clean, professional, and responsive menu-driven interface.
*   **Automatic Cleanup:** Restores all network settings upon exit.

## Screenshots
![WIFI-TOOLKIT Screenshot](screenshot/wifitoolwok.png)

---

## Requirements
This tool depends on several external command-line utilities. Ensure they are installed on your Debian/Ubuntu-based system.

| Tool                                                       | Description                                       |
| ---------------------------------------------------------- | ------------------------------------------------- |
| [Aircrack-ng](https://www.aircrack-ng.org/)                | Essential suite for Wi-Fi security auditing.      |
| [MDK4](https://github.com/aircrack-ng/mdk4)                | Advanced Wi-Fi testing tool for DoS attacks.      |
| [Macchanger](https://github.com/alobbs/macchanger)         | Utility for viewing and manipulating MAC addresses. |
| [iw](https://wireless.wiki.kernel.org/en/users/documentation/iw) | A modern nl80211 based CLI configuration utility. |
| [hostapd](https://w1.fi/hostapd/)                         | User space daemon for AP and authentication servers. |
| [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html)      | A lightweight DHCP and caching DNS server.        |
| [Evil Limiter](https://github.com/bitbrute/evillimiter)    | Bandwidth limiter for local network devices.      |

You can install all requirements with the following command:
```bash
sudo apt update
sudo apt install aircrack-ng mdk4 macchanger iw hostapd dnsmasq iproute2 iptables evillimiter
```

## Platform Support
This tool is designed for and tested on **Linux-based operating systems** due to its heavy reliance on Linux-specific networking utilities (e.g., `airmon-ng`, `iptables`, `tc`).

For Windows users, it is recommended to run `wifiToolkit` within a **Windows Subsystem for Linux (WSL)** environment to ensure all functionalities work as intended.

## Usage
1.  Download the `wifiToolkit` executable from the [Releases page](https://github.com/jimbon25/WIFI-TOOLKIT/releases/tag/v2.9.3).
2.  Make the file executable:
    ```bash
    chmod +x wifiToolkit
    ```
3.  Run the tool with root privileges:
    ```bash
    sudo ./wifiToolkit
    ```

## Termux Support
Support for the Termux environment on Android is currently under development. A version compiled specifically for ARM architectures will be made available in a future release. Stay tuned!

## Support the Project

If you appreciate this tool and would like to support its development, consider buying me a coffee! Your support helps maintain and improve this project.

[Buy Me a Coffee on Saweria](https://saweria.co/dimasla)

## Credits

This project integrates and utilizes the core functionality of [Evil Limiter](https://github.com/bitbrute/evillimiter), a powerful tool for monitoring, analyzing, and limiting bandwidth of devices on a local network. We extend our gratitude to the original author, bitbrute, for their excellent work.

## License
This project is licensed under the MIT License.