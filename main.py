import serial
import requests
import config  # Import your new config file

# Use the variables from config.py
ser = serial.Serial(config.SERIAL_PORT, 9600, timeout=1)

# Store current values
temps = {"A": None, "B": None}

print("Gateway Running...")

while True:
    line = ser.readline().decode('utf-8').strip()
    if line and ":" in line:
        try:
            identifier, value = line.split(":")
            temps[identifier] = float(value)
            
            # Use the API_KEY and URL from the config file
            params = {'api_key': config.API_KEY}
            
            if identifier == "A":
                params['field1'] = temps["A"]
            elif identifier == "B":
                params['field2'] = temps["B"]

            response = requests.get(config.BASE_URL, params=params)
            print(f"Sent {identifier} to ThingSpeak. Status: {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")