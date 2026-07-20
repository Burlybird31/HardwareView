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

tracking_active = False
start_button = None
stop_button = None

def clear_console():
    """ This just clears the terminal screen """
    
    if os.name == 'nt': # "nt" is for windows
        os.system('cls')
    else:
        os.system('clear')

def get_cpu_telemetry():
    """ CPU data """
    
    cpu_usage = psutil.cpu_percent()
    return cpu_usage

def get_ram_telemetry():
    """ RAM data """

    ram_usage = psutil.virtual_memory()
    used_gb = round(ram_usage.used / (1024 ** 3) + 0.5, 1) # converting from bytes to gigabytes
    return used_gb, ram_usage.percent

def run_telemetry():
    """ main running file """

    global tracking_active

    csv_filename = "hardwareView.csv"
    headers = ["CPU_Util%", "RAM_USG", "RAM_Util%"]

    arduino_port = 'COM3'
    baud_rate = 9600

    print("Opening serial port...")
    clear_console()

    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)
        print(f"Connected to Arduino on {arduino_port}!")
    except Exception as e:
        print(f"Could not connect to {arduino_port}: {e}")

    with open(csv_filename, mode='w', newline='', buffering=1) as file:
        writer = csv.writer(file)

        #writer.writerow(headers)

        while tracking_active:

            cpu_usage = get_cpu_telemetry()
            ram_gb, ram_pct = get_ram_telemetry()
            writer.writerow([cpu_usage, ram_gb, ram_pct])
            #print("logged to CSV")

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
    global tracking_active
    if not tracking_active:
        tracking_active = True
        start_button.config(state="disabled") 
        stop_button.config(state="normal")
        
        telemetry_thread = threading.Thread(target=run_telemetry)
        telemetry_thread.daemon = True
        telemetry_thread.start()

def stop_telemetry():
    global tracking_active
    tracking_active = False
    start_button.config(state="normal")
    stop_button.config(state="disabled")

def create_gui():
    global start_button, stop_button

    root = tk.Tk()
    root.title("HardwareView")
    root.geometry("1000x500")

    start_button = tk.Button(root, text="Start Tracking", command=start_telemetry_thread, bg="green", fg="white")
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Tracking", command=stop_telemetry, bg="red", fg="white", state="disabled")
    stop_button.pack(pady=10)

    # 1. Setup / Flash Button (New!)
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
    # 1. Get the directory where THIS script is currently sitting
    if getattr(sys, 'frozen', False):
        # If the app is compiled into an .exe later
        base_path = sys._MEIPASS
    else:
        # If running as a standard .py file
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 2. Point directly to the bundled files next to your script
    avrdude_path = os.path.join(base_path, "avrdude.exe")
    avrdude_config = os.path.join(base_path, "avrdude.conf")
    hex_file_path = os.path.join(base_path, hex_file_name)

    # 3. Build the command using these local paths
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

    # 4. Run the flashing process
    try:
        print(f"Flashing Arduino Mega on {com_port}...")
        # Run the command in the background and capture the output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("Flash Successful!")
        return True
    except subprocess.CalledProcessError as e:
        print("Flash Failed!")
        print("--- AVRDUDE STDERR ---")
        print(e.stderr)  # This will print the exact error to your terminal
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def start_flash_thread():
    # We will temporarily hardcode 'COM3' (or whichever port your Mega is on) 
    # and the exact name of your .hex file for testing.
    target_port = "COM3" 
    hex_name = "arduinoFirm.ino.hex" # Change this to your actual .hex filename!

    def run_flash():
        # Call the flashing function we wrote earlier
        success = flash_arduino(target_port, hex_name)
        
        # Pop up a window alert to let the user know the outcome
        if success:
            messagebox.showinfo("Success", f"Arduino successfully flashed on {target_port}!")
        else:
            messagebox.showerror("Error", "Flashing failed. Check console output for details.")

    # Run the flashing process on a background thread so the GUI doesn't freeze
    flash_thread = threading.Thread(target=run_flash)
    flash_thread.daemon = True
    flash_thread.start()

create_gui()