# data_logger.py
"""
    This is a sligthly enhanced data logger which connects automatically to an arduino/esp32.
    It reads from the serial port and saves the data to a csv file with a time stamp in the name, so no previously
    recorded data can be lost.
    The use of this script is to log data from a PPG sensor like MAX30102.
    So the expected readings are in the format:
    millis, red, ir, sanmple_num

    Any other format won't work at the moment, but this will be updated in the future.

    You will need serial and its dependencies installed in your python enviroment to be able to use it.
    For more informations please refer to: https://pyserial.readthedocs.io/en/latest/pyserial.html#installation
"""

import serial
import serial.tools.list_ports
import platform
import sys
import os
import time

# TODO Use the python CSV Library

# TODO This script has to be implemented in a general way so that it's execution is independent of the transferred data

# CSV ENCODING
# TIME, RED, IR, NUM_SAMPLE

# USER INITIALISATION

DIRECTORY = 'readings/'  # Path of directory where data is been stored
FILE_NAME = 'reading_' + time.strftime('%d-%m-%Y_%H-%M-%S') + '.csv'  # name of the CSV file generated
FILE_PATH = DIRECTORY + FILE_NAME

baud = 9600  # arduino runs at 9600 baud
samples = 10  # how many samples to collect
PRINT_DATA = True
BOTH_LED = True  # False: Only Red sends data, True: Both LED's sends data

# AUTO CONNECT ARDUINO / ESP32

ports = list(serial.tools.list_ports.comports())
ser = None

for port in ports:
    # MAC OS
    if platform.system() == "Darwin":
        # This code prefers ESP32 over arduino on macos
        if "CP2104" in port.description:
            print("ESP 32 Detected.")
            ser = serial.Serial(port.device, baudrate=baud)
            break
        if 'USB VID:PID=2341:0043' in port.hwid:
            print("Arduino Uno detected")
            ser = serial.Serial(port.device, baudrate=baud)
            break

    # WINDOWS
    if platform.system() == "win32":
        # TODO Implement Windows Auto Connect
        pass

if not ser:
    print("No device found!")
    sys.exit()

# CREATE TARGET DIRECTORY IF NECESSARY
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

# INITIALIZE SERIAL CONNECTION

print('Connected {} to port {} with baud rate.'.format(ser.name, ser.port, ser.baudrate))

line = 0  # start at 0 because our header is 0 (not real data)

file = open(FILE_PATH, "w")
print('Created File with filename:', FILE_PATH)
file.write('Millis,Red,IR,sample\n')  # TODO Do not hardcore the csv row headers

# reset data values
red = 0
ir = 0
ser.flush()
ser.reset_input_buffer()
# ser.write(0)  # reset the arduino
while line <= samples:

    # getData = ser.readline().decode()
    getData = ser.readline().decode()

    #  TODO Add filter to remove invalid data

    data1 = getData.split(sep=',')

    # Filter all non digit characters from the serial reading
    i: int = 0
    for _ in data1:
        data1[i] = "".join(filter(str.isdigit, data1[i]))
        i += 1

    # Just in case something went wrong and the first received data portion is not valid
    try:
        millis = data1[0]
        red = data1[1]
        ir = data1[2]
        sample = data1[3]
    except IndexError:
        # if an IndexError occurs there was likely a transmission error
        continue

    write_data = str(millis) + ',' + str(red) + ',' + str(ir) + ',' + str(sample)
    file.write(write_data + "\n")  # write data with a newline

    if PRINT_DATA:
        print('Millis={}, Red={}, IR={}, sample={}'.format(millis, red, ir, sample))

    line = line + 1

print("Collection of {} samples completed!".format(samples))
file.close()
