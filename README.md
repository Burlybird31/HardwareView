# HardwareView 

A lightweight, standalone Windows application built to monitor real-time PC system telemetry and seamlessly flash custom firmware onto an Arduino Mega hardware interface. 

This is my very first GitHub project as I continue learning how to code!

##  Features

* **Real-Time Telemetry Dashboard:** Tracks and transmits key PC performance metrics.
* **No Python Environment Required:** Ships as a standalone Windows executable (`.exe`).
* **Embedded Tooling:** Features an integrated flasher interface leveraging bundled AVRDUDE utilities to program your microcontroller directly from the application.
* **Custom Hardware Output:** Designed specifically to output system data to a physical display interface.

##  Hardware Requirements

To utilize this system out of the box, you will need:
* **Microcontroller:** Arduino Mega
* **Display:** I2C LCD Display Module

##  Installation & Setup

1. Navigate to the **Releases** section on the right side of this repository page and download the latest `HardwareView_v1.0.0.zip` archive.
2. Extract the contents of the `.zip` file to your preferred local directory.
3. Wire your **I2C LCD Display** to your **Arduino Mega**.
4. Connect the Arduino Mega to your PC using a USB cable.
5. Open the extracted folder, locate **`HardwareView.exe`**, and launch it.
6. Follow the intuitive on-screen prompts to flash the pre-compiled firmware and initiate the telemetry stream!

## ⚠️ Important Note on Antivirus Warnings

Because this application is bundled into a standalone executable (`.exe`) via PyInstaller, Windows Defender or other third-party antivirus software **will almost certainly flag or block it** as an unrecognized file upon launch. 

This is a very common false positive for independent Python executables. To run the application:
1. Click **"More Info"** on the Windows Defender popup.
2. Select **"Run Anyway"**.
