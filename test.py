import serial
import requests
import time
import config 

try:
    ser = serial.Serial(config.SERIAL_PORT, 9600, timeout=1)
    print(f"Connected to XBee on {config.SERIAL_PORT}")
except Exception as e:
    print(f"Could not open serial port: {e}")
    exit()

last_send_time = 0

while True:
    if ser.in_waiting > 0:
        # Read raw bytes instead of decoding immediately
        raw_data = ser.read(ser.in_waiting)
        
        # Look for numbers in the binary mess
        # This is a 'quick-fix' to extract digits from an API frame
        import re
        decoded_search = re.findall(r"[-+]?\d*\.\d+|\d+", str(raw_data))
        
        if decoded_search:
            value = decoded_search[-1] # Take the last number found
            print(f"Found Value in Packet: {value}")

            current_time = time.time()
            if (current_time - last_send_time) > 16:
                params = {'api_key': config.API_KEY, 'field1': value}
                try:
                    response = requests.get(config.BASE_URL, params=params)
                    if response.status_code == 200:
                        print(f"-> Sent to ThingSpeak: {value}")
                        last_send_time = current_time
                except Exception as e:
                    print(f"Network error: {e}")
            else:
                print("-> Cooldown active...")
    
    time.sleep(0.5)