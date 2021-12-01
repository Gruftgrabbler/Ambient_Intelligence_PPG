import serial
import serial.tools.list_ports
import platform
import sys
import os
import time

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
        if "CP2104" in port.description:
            print("ESP 32 Detected.")
            ser = serial.Serial(port.device, baudrate=baud)
        if 'USB VID:PID=2341:0043' in port.hwid:
            print("Arduino Uno detected")
            ser = serial.Serial(port.device, baudrate=baud)

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
file.write("Red, IR \n")

# reset data values
red = 0
ir = 0
ser.flush()
ser.reset_input_buffer()

while line <= samples:
    # incoming = ser.read(9999)
    # if len(incoming) > 0:
    getData = str(ser.readline())
    data = getData.split(sep=",")

    # Just in case something went wrong and the first received data portion is not valid
    try:
        # Truncate the data strings so that just the blank numbers are content of the variables
        red = data[0][6:]
        if BOTH_LED:
            ir = data[1][3:-5]
    except IndexError:
        continue

    write_data = str(red) + ", " + str(ir)
    file.write(write_data + "\n")  # write data with a newline

    if PRINT_DATA:
        print("Red={}, IR={}".format(red, ir))

    line = line + 1

print("Collection of {} samples completed!".format(samples))
file.close()
