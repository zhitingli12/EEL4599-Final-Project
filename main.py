import serial
import requests
import time
import config
import re

try:
    ser = serial.Serial(config.SERIAL_PORT, 9600, timeout=1)
    ser.reset_input_buffer()
    print(f"Connected to {config.SERIAL_PORT} (Gateway Active)")
except Exception as e:
    print(f"Error: {e}")
    exit()

# Dictionary to hold the most recent data
temps = {"A": None, "B": None}
last_upload_time = time.time()

MIN_TEMP = 50.0   # Discard anything below 50.0 F
MAX_TEMP = 120.0  # Discard anything above 120.0 F

print(f"Gateway Running...")
print(f"Filtering: Keeping values between {MIN_TEMP} and {MAX_TEMP} F")

while True:
    try:
        # Read recieve data
        raw_data = ser.readline()
        line = raw_data.decode('utf-8', errors='ignore').strip()

        if line:

            sender_id = None
            if "A:" in line: sender_id = "A"
            elif "B:" in line: sender_id = "B"

            if sender_id:
                match = re.search(r"[-+]?\d*\.\d+|\d+", line)
                if match:
                    val = float(match.group())
                    
                    if val < MIN_TEMP or val > MAX_TEMP:
                        print(f"Outlier Ignored: {val} F (Outside {MIN_TEMP}-{MAX_TEMP} range)")
                    else:
                        temps[sender_id] = val
                        print(f"Updated Sensor {sender_id}: {val} F")

        # Upload every 20 seconds)
        current_time = time.time()
        if current_time - last_upload_time > 20: 
            if temps["A"] is not None or temps["B"] is not None:
                print(">>> Sending current data to ThingSpeak...")
                
                params = {'api_key': config.API_KEY}
                if temps["A"] is not None: params['field1'] = temps["A"]
                if temps["B"] is not None: params['field2'] = temps["B"]

                try:
                    response = requests.get(config.BASE_URL, params=params)
                    if response.status_code == 200:
                        print(f"SUCCESS | Sent -> A: {temps['A']} | B: {temps['B']}")
                    
                    # Clear data after sending to wait for fresh readings
                    temps = {"A": None, "B": None}
                    last_upload_time = time.time()
                    ser.reset_input_buffer() 
                except Exception as e:
                    print(f"Network Error: {e}")
            else:
                last_upload_time = time.time()
                print(f"Waiting for valid data ({MIN_TEMP}-{MAX_TEMP} F) before upload...")

    except KeyboardInterrupt:
        print("\nStopping Gateway...")
        ser.close()
        break