# Evil Twin Attack Guide

This document explains the Evil Twin Attack feature in the `wifiToolkit` program, including how it works, its requirements, and important considerations.

## Overview

An Evil Twin Attack is a technique where an attacker creates a fake Access Point (AP) that mimics a legitimate Wi-Fi network. The goal is to lure nearby devices to connect to the attacker's fake AP instead of the real one. Once connected, the attacker can monitor traffic, redirect victims to fake pages, or, with proper configuration, provide controlled internet access.

The Evil Twin feature in `wifiToolkit` automates this process, including target scanning, fake AP creation with WPA2 support, DHCP server setup, and deauthenticating clients from the real AP.

## Requirements

To effectively run an Evil Twin attack, especially with internet access for clients, you will need:

1.  **Two Wireless Adapters:**
    *   **Adapter 1 (Deauthentication Interface):** Must support monitor mode. Used to disconnect clients from the real AP.
    *   **Adapter 2 (Fake AP Interface):** Must support AP (Access Point) mode. Used to create the fake AP.
2.  **Third Network Adapter (Optional, for Internet Access):**
    *   This is a separate network interface connected to the internet (e.g., a wired Ethernet adapter or a third Wi-Fi adapter connected to a legitimate Wi-Fi network).
    *   **IMPORTANT:** Without this third adapter, clients will be able to connect to your fake AP and obtain an IP address, but **will not have internet access**.
3.  **Software Tools:**
    *   `aircrack-ng` (provides `airmon-ng`, `airodump-ng`, `aireplay-ng`)
    *   `mdk4`
    *   `macchanger`
    *   `iw`
    *   `hostapd`
    *   `dnsmasq`
    *   `iptables`
    *   `systemd-resolved` (will be temporarily stopped and restarted by the program)

## How it Works

The `EvilTwin` program automates the following steps:

1.  **Interface Selection:** When you launch the attack, the toolkit will first ensure a primary wireless interface is selected and put into monitor mode for deauthentication. Then, you will be prompted to select a secondary interface to be used for the fake AP (in managed mode).
2.  **Target Scanning:** The program scans nearby Wi-Fi networks to identify the target AP to mimic.
3.  **Target AP Selection:** You select the target AP from the discovered list. If the target AP uses WPA2, you will be asked to enter the WPA2 password.
4.  **Fake AP Interface Preparation:**
    *   `NetworkManager` is stopped.
    *   The fake AP interface is configured to managed mode and set to the target AP's channel.
    *   Any existing IP configuration on the fake AP interface is flushed (`ip addr flush`).
    *   Any potentially running `dnsmasq` processes are forcefully stopped (`pkill -9 dnsmasq`).
5.  **Fake AP Creation (`hostapd`):** The fake AP is created with the same ESSID and channel as the target AP, supporting WPA2 encryption if a password is provided.
6.  **DHCP Server Setup (`dnsmasq`):**
    *   `systemd-resolved` is temporarily stopped to free up port 53.
    *   The fake AP interface is assigned an IP address (`10.0.0.1/24`).
    *   A DHCP server is configured and started to provide IP addresses to clients connecting to your fake AP.
7.  **IP Forwarding and NAT (`iptables`) - If Internet Interface Found:**
    *   The program attempts to detect an internet-connected interface (other than the deauthentication and fake AP interfaces).
    *   If an internet interface is found, IP forwarding is enabled (`net.ipv4.ip_forward=1`).
    *   `iptables` rules are added to allow traffic to flow from the fake AP to the internet and perform Network Address Translation (NAT) so clients can access the internet.
8.  **Deauthentication Attack (`aireplay-ng`):** Continuous deauthentication packets are sent to the real AP, forcing clients to disconnect and potentially connect to your fake AP.
9.  **Client Monitoring:** The program monitors the `dnsmasq` logs for notifications of new client connections to your fake AP.
10. **Cleanup:** When the attack is stopped (with Ctrl+C), the program automatically:
    *   Stops all attack processes (`hostapd`, `dnsmasq`, `aireplay-ng`).
    *   Deletes temporary configuration files.
    *   Restores the fake AP interface to managed mode.
    *   Restarts `NetworkManager` and `systemd-resolved`.
    *   Deletes `iptables` rules and disables IP forwarding (if enabled).

## Usage

1.  Ensure all [Requirements](#requirements) are met.
2.  Run `wifiToolkit` with root privileges:
    ```bash
    sudo ./wifiToolkit
    ```
3.  From the main menu, select the option to "Launch Evil Twin Attack".
4.  Follow the on-screen instructions to select interfaces and the target AP.
5.  If prompted, enter the WPA2 password for the target AP.
6.  The attack will begin. Press `Ctrl+C` to stop it.

## Important Notes

*   **Internet Access:** As mentioned above, internet access for fake AP clients **requires a third network adapter connected to the internet**. If you only have two wireless adapters, clients will connect but will not have internet access.
*   **Ethics:** Use this tool responsibly and only on networks you have permission to test.
*   **Stability:** Although the program includes comprehensive cleanup steps, there is always a small possibility of unexpected issues. It is recommended to verify your network status after an attack.
