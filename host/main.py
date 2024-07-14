import csv
import serial
from datetime import datetime
from pzem import PZEM_016 as PZEM016
import time
from pprint import pprint
import os

# Initialize PZEM sensor
pz = PZEM016("/dev/ttyUSB0")
pz.reset_energy()

# Initialize serial connection
s = None

# CSV file name
csv_file = 'data.csv'

# CSV header
csv_header = [
    'timestamp',
    'delta',
    'ac_voltage',
    'ac_current',
    'ac_power',
    'ac_energy',
    'ac_frequency',
    'ac_power_factor',
    'dc_1_voltage',
    'dc_1_current',
    'temp_1'
]
last_time = None

# Open CSV file in append mode
with open(csv_file, 'a', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_header)

    # If file is empty, write header
    if file.tell() == 0:
        writer.writeheader()

    while True:
        # Open serial connection
        while s is None:
            try:
                s = serial.Serial(port="/dev/ttyACM1", parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_ONE, timeout=1)
                s.flush()
            except serial.SerialException:
                print("Waiting for device...")
                time.sleep(1)

        try:
            new_time = time.time()
            data = {
                'timestamp': datetime.now().strftime('%H:%M:%S.%f'),
                'delta': 0 if last_time is None else new_time - last_time,
                'ac_voltage': pz.voltage,
                'ac_current': pz.current,
                'ac_power': pz.power,
                'ac_energy': pz.energy,
                'ac_frequency': pz.frequency,
                'ac_power_factor': pz.power_factor,
                'dc_1_voltage': None,
                'dc_1_current': None,
                'temp_1': None
            }
            last_time = new_time

            # s.flushInput()
            # while data['dc_1_voltage'] is None or data['dc_1_current'] is None or data['temp_1'] is None:
            #     pico_read = s.readline().strip().decode()
            #     try:
            #         key, value = pico_read.split(',')
            #         data[key] = value
            #     except ValueError:
            #         pass
            
            os.system('clear')
            pprint(data)

            # Write data to CSV
            writer.writerow(data)
            file.flush()  # Ensure data is written immediately

        except serial.SerialTimeoutException:
            print("Connection lost.")
        finally:
            s.close()
            s = None
