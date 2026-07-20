import time
import os
import psutil
import csv
import serial
import tkinter as tk
from tkinter import messagebox
import threading
import sys
import subprocess

# Global flags and UI references for tracking state across threads
tracking_active = False
start_button = None
stop_button = None

def clear_console():
    """Clears the terminal screen depending on the operating system."""
    if os.name == 'nt':  # Windows environment
        os.system('cls')
    else:  # macOS or Linux environment
        os.system('clear')

def get_cpu_telemetry():
    """Retrieves the current total CPU utilization percentage."""
    cpu_usage = psutil.cpu_percent()
    return cpu_usage

def get_ram_telemetry():
    """Retrieves RAM usage metrics, converting raw bytes into gigabytes."""
    ram_usage = psutil.virtual_memory()
    # Convert bytes to gigabytes and round cleanly
    used_gb = round(ram_usage.used / (1024 ** 3) + 0.5, 1) 
    return used_gb, ram_usage.percent

def run_telemetry():
    """Main background loop handling data logging and serial communication."""
    global tracking_active

    csv_filename = "hardwareView.csv"
    headers = ["CPU_Util%", "RAM_USG", "RAM_Util%"]

    arduino_port = 'COM3'
    baud_rate = 9600

    print("Opening serial port...")
    clear_console()

    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)  # Allow time for Arduino serial connection to settle
        print(f"Connected to Arduino on {arduino_port}!")
    except Exception as e:
        print(f"Could not connect to {arduino_port}: {e}")

    with open(csv_filename, mode='w', newline='', buffering=1) as file:
        writer = csv.writer(file)

        # writer.writerow(headers)

        while tracking_active:
            cpu_usage = get_cpu_telemetry()
            ram_gb, ram_pct = get_ram_telemetry()
            
            # Log local performance metrics to CSV file
            writer.writerow([cpu_usage, ram_gb, ram_pct])
            # print("logged to CSV")

            # Stream telemetry string to the Arduino via Serial if connected
            if ser is not None:
                try: 
                    sentString = f"{cpu_usage},{ram_gb},{ram_pct},"
                    ser.write(sentString.encode('utf-8'))
                except Exception as e:
                    print("Serial Connection Lost")
                    ser.close()
                    ser = None

            time.sleep(1)

def start_telemetry_thread():
    """Initiates the telemetry loop on a background thread to prevent UI freezing."""
    global tracking_active
    if not tracking_active:
        tracking_active = True
        start_button.config(state="disabled") 
        stop_button.config(state="normal")
        
        telemetry_thread = threading.Thread(target=run_telemetry)
        telemetry_thread.daemon = True
        telemetry_thread.start()

def stop_telemetry():
    """Stops the data collection loop and updates the UI button states."""
    global tracking_active
    tracking_active = False
    start_button.config(state="normal")
    stop_button.config(state="disabled")

def create_gui():
    """Initializes and displays the application interface using Tkinter."""
    global start_button, stop_button

    root = tk.Tk()
    root.title("HardwareView")
    root.geometry("1000x500")

    # Start and Stop telemetry streaming controls
    start_button = tk.Button(root, text="Start Tracking", command=start_telemetry_thread, bg="green", fg="white")
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Tracking", command=stop_telemetry, bg="red", fg="white", state="disabled")
    stop_button.pack(pady=10)

    # Firmware flash interface button
    flash_button = tk.Button(
        root, 
        text="Flash Arduino Firmware", 
        command=start_flash_thread, 
        bg="blue", 
        fg="white", 
        font=("Arial", 10, "bold")
    )
    flash_button.pack(pady=15)

    root.mainloop()

def flash_arduino(com_port, hex_file_name):
    """Handles the AVRDUDE flashing subprocess invocation for the Arduino Mega."""
    if getattr(sys, 'frozen', False):
        # Resolve assets path from the PyInstaller temporary extraction folder
        base_path = sys._MEIPASS
    else:
        # Resolve assets path relative to the active script folder execution
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Construct file paths for local dependency binaries and firmware
    avrdude_path = os.path.join(base_path, "avrdude.exe")
    avrdude_config = os.path.join(base_path, "avrdude.conf")
    hex_file_path = os.path.join(base_path, hex_file_name)

    # Compile the formal execution command arguments for AVRDUDE
    cmd = [
        avrdude_path,
        "-C", avrdude_config,
        "-c", "wiring",
        "-p", "m2560",
        "-P", com_port,
        "-b", "115200",
        "-D",
        "-U", f"flash:w:{hex_file_path}:i"
    ]

    try:
        print(f"Flashing Arduino Mega on {com_port}...")
        # Execute the process synchronously and capture logging output streams
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("Flash Successful!")
        return True
    except subprocess.CalledProcessError as e:
        print("Flash Failed!")
        print("--- AVRDUDE STDERR ---")
        print(e.stderr)  # Outputs detailed device errors directly to the console
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def start_flash_thread():
    """Spawns the microcontroller flasher task onto a detached background thread."""
    target_port = "COM3" 
    hex_name = "arduinoFirm.ino.hex" 

    def run_flash():
        success = flash_arduino(target_port, hex_name)
        
        # Display explicit interface notification alerts depending on status
        if success:
            messagebox.showinfo("Success", f"Arduino successfully flashed on {target_port}!")
        else:
            messagebox.showerror("Error", "Flashing failed. Check console output for details.")

    # Execute flashing routine context in a distinct thread to maintain UI interactivity
    flash_thread = threading.Thread(target=run_flash)
    flash_thread.daemon = True
    flash_thread.start()

create_gui()