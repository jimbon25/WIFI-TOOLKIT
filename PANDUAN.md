# WiFi Toolkit User Guide

This document is a comprehensive guide to using all the features available in the `wifiToolkit` program.

---

## Main Menu

When the program is run, you will be greeted with the main menu containing a list of all available functions.

### `[1] Scan for Networks (airodump-ng)`

- **Purpose:** To scan and view WiFi networks and devices (clients) around you.
- **How to Use:**
    1. Select option `1`.
    2. You will be given two choices:
        - **`1) Standard Scan`**: Only displays networks and clients on the screen. Press `Ctrl+C` to stop and return to the menu.
        - **`2) Scan and Save`**: Similar to a standard scan, but also saves all captured packets to a `.cap` file in the current directory. You will be asked to enter a filename for the output.

### `[2] Launch Mass Attack (mdk4)`

- **Purpose:** To launch a mass attack (wide area) without needing to select a specific target. Useful for creating general disruption.
- **How to Use:**
    1. Select option `2`.
    2. Choose the attack type:
        - **`1) Deauthentication Flood (Broadcast)`**: Sends deauthentication packets to all nearby devices, causing mass connection disruption.
        - **`2) Deauthentication Flood (From Target List)`**: Similar to above, but only targets APs whose MAC addresses are in the `blacklist.txt` file.
        - **`3) Beacon Flood (From SSID List)`**: Creates hundreds to thousands of fake Access Points. Fake AP names are taken from the `ssidlist.txt` file. This will clutter the WiFi network list on nearby devices.
    3. After selecting, the attack will run until you stop it with `Ctrl+C`.

### `[3] Launch Targeted Attack (aireplay-ng)`

- **Purpose:** For highly specific deauthentication attacks, targeting one AP and one or all clients connected to it.
- **How to Use:**
    1. Select option `3`.
    2. The program will scan for networks for 20 seconds.
    3. You will be presented with a list of found APs. Select the AP number you want to attack.
    4. The program will then display a list of clients connected to that AP.
    5. You can choose to attack **one specific client** (by selecting its number) or **all clients** on that AP (by pressing the `a` key).
    6. The attack will run continuously until stopped with `Ctrl+C`.

### `[4] Automated Handshake Capture`

- **Purpose:** The most efficient feature for capturing WPA/WPA2 Handshakes (needed for password cracking).
- **How to Use:**
    1. Select option `4`.
    2. The program will scan for networks to find targets using WPA/WPA2 encryption.
    3. Select the target AP from the displayed list.
    4. The program will work **fully automatically**: running `airodump-ng` to listen, and `aireplay-ng` to provoke clients to reconnect.
    5. The program will monitor this process. If a handshake is successfully captured, the attack will stop automatically.
    6. **Result:** The full path to the `.cap` file containing the handshake will be displayed on the screen. The file is saved in a new folder named `handshakes/`.

### `[5] Launch Evil Twin Attack`

- **Purpose:** To create a fake Access Point (AP) that mimics a target network, with the aim of luring nearby devices to connect to your fake AP instead of the real one. This allows you to monitor traffic or redirect them to fake pages.
For more detailed usage instructions, requirements, and security considerations, see [Evil Twin Attack Guide](docs/evil_twin_guide.md).
- **How to Use:**
    1. Select option `5` from the main menu.
    2. The program will start scanning for nearby WiFi networks for 15 seconds.
    3. After the scan is complete, you will be presented with a list of found APs. Select the number of the target AP you want to mimic (e.g., home or office AP).
    4. **If the target AP uses WPA/WPA2**, the program will ask you to enter the WPA2 password for that AP. Make sure you enter the correct password so clients can connect.
    5. The program will automatically:
        *   Set your wireless interface to the target AP's channel.
        *   Create a fake AP with the same name (ESSID) and MAC address (BSSID) as the target AP using **`hostapd`** (supports WPA2 encryption).
        *   Set up a DHCP server using `dnsmasq` to provide IP addresses to clients connected to your fake AP.
        *   Start a continuous deauthentication attack on the real AP using `aireplay-ng`, which will disconnect clients from the real AP.
    6. You will see the message `[*] Evil Twin attack is now active. Clients should be connecting to your fake AP.` This means the attack is active.

- **What to do when the attack is active:**
    *   **Client Connection Notifications:** Each time a new client successfully connects to your fake AP and obtains an IP address, you will see a notification `[!!!] NEW CLIENT CONNECTED: IP=..., MAC=..., Hostname=...` directly in the terminal.
    *   **Wait for Clients to Connect:** Devices disconnected from the real AP will search for networks with the same name. Since your fake AP has the same name and now supports WPA2, there is a high probability they will connect to your fake AP.
    *   **Verify Connected Clients (Additional Methods):**
        *   **Use `Wireshark` or `TShark`:** This is the best way to view traffic. Open a new terminal and run `sudo wireshark -i <your_monitor_interface>` (e.g., `wlan0mon`) or `sudo tshark -i <your_monitor_interface>`. You will see data traffic from connected clients.

- **Stopping the Attack:**
    *   Press `Ctrl+C` in the terminal where the `wifiToolkit` program is running.
    *   The program will automatically stop all attack processes (`hostapd`, `dnsmasq`, `aireplay-ng`), clean up temporary configuration files, and restore your interface to its normal state.

### `[6] Launch DoS Attack`

- **Purpose:** A dedicated menu for various types of Denial-of-Service (DoS) attacks to disrupt networks.
- **How to Use:**
    1. Select option `6`.
    2. You will enter the DoS sub-menu:
        - **Options 1-4** are standard attacks (Jamming, PMKID, Deauth, Beacon) that will ask you to enter the **channel** and **duration** of the attack.
        - **Option `[5] Smart Adaptive Attack`** is the most advanced feature.

#### Detail: `[5] Smart Adaptive Attack`
- **Purpose:** Launches an intelligent DoS attack that can measure its own impact and automatically adjust its aggressiveness.
- **How to Use:**
    1. Select option `5` in the DoS menu.
    2. The program will scan for targets with active clients.
    3. Select the target AP from the list.
    4. The program will start the attack in 'stealthy' mode while continuously monitoring its effectiveness (whether clients are actually disconnected).
    5. If not effective, the program will automatically switch to a more aggressive strategy until the target is successfully disrupted.
    6. Press `Ctrl+C` to stop the attack.

### `[7] Run Automated Chain`

- **Purpose:** To run several types of attacks sequentially and automatically.
- **How to Use:**
    1. Select option `7`.
    2. You will enter the "attack chain" creation mode.
    3. Press `1`, `2`, or `3` to add an attack to the chain.
    4. You can also save (`s`) or load (`l`) existing attack chains.
    5. After finishing the setup, press `d` (Done) to execute all attacks in the chain sequentially.

### `[8] Toggle Stealth Mode`

- **Purpose:** To activate stealth mode to mask your attacks.
- **How to Use:**
    1. Select option `8` to enter the configuration menu.
    2. You can set three parameters:
        - **MAC Rotation Interval:** How often your MAC address will be automatically changed.
        - **Channel Hopping Interval:** How often the program will switch WiFi channels.
        - **TX Power:** Sets the signal strength of your WiFi card (lower is harder to detect).
    3. After configuration, stealth mode will be active and run in the background until you deactivate it again from the same menu.

### `[9] Exit and Restore`

- **Purpose:** To exit the program safely.
- **How to Use:** Select option `9`. The program will automatically:
    - Stop all active attack processes.
    - Restore your WiFi interface to "managed" (normal) mode.
    - Restore your original MAC address.
    - Delete temporary files.
    - Generate a session summary report.
