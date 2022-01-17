import os
import csv
import time
import warnings
#import serial
import serial.tools.list_ports

file_path = "Sensordaten/"
file_name = time.strftime("%Y%m%d-%H%M%S") + '.csv'

arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    #if 'Arduino' in p.description
    #if 'USB-SERIAL' in p.description
    if 'Silicon Labs CP210x' in p.description
]
if not arduino_ports:
    raise IOError("No Arduino found")
if len(arduino_ports) > 1:
    warnings.warn('Multiple Arduinos found - using the first')

Arduino = serial.Serial(arduino_ports[0], 9600)         # initialisiert ersten gefundenen Arduino mit Baud-Rate 9600
Arduino.flush()
Arduino.reset_input_buffer()

if not os.path.exists(file_path):
    os.makedirs(file_path)

with open(file_path + file_name, 'w', newline='') as outfile:
    fieldnames = ['time', 'sensor1', 'sensor2']

    csv_writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    csv_writer.writeheader()

# start_time = int(round(time.time() * 1000))         # start_time = time.time()

while True:
    while (Arduino.inWaiting() == 0):
        pass
    try:

        data1 = Arduino.readline()
        dataarray = data1.decode().rstrip().split(',')
        #Arduino.reset_input_buffer()

        # current_time = int(round(time.time() * 1000)) - start_time  # time.time() - start_time
        millis = float(dataarray[0])
        sensor_red = float(dataarray[1])
        sensor_ir = float(dataarray[2])

        print(millis, ",", sensor_red, ",", sensor_ir)

        with open(file_path + file_name, 'a', newline='') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow([millis, sensor_red, sensor_ir])
    except(KeyboardInterrupt, SystemExit,IndexError,ValueError):
        pass

    outfile.close()
