import serial
import serial.tools.list_ports
import platform

# USER INITIALISATION

baud = 9600  # arduino runs at 9600 baud
samples = 10  # how many samples to collect
fileName = "analog-data.csv"  # name of the CSV file generated
print_data = True

# AUTO CONNECT ARDUINO / ESP32

ports = list(serial.tools.list_ports.comports())

for port in ports:
    # MAC OS
    if platform.system() == "Darwin":
        if "CP2104" in port.description:
            print("ESP 32 Detected.")
            ser = serial.Serial(port.device)

    # WINDOWS
    if platform.system() == "win32":
        # TODO Implement Windows Auto Connect
        pass

# INITIALIZE SERIAL CONNECTION

print('Connected {} to port {}.'.format(ser.name, ser.port))

line = 0  # start at 0 because our header is 0 (not real data)

file = open(fileName, "w")
print('Created File with filename:', fileName)
file.write("Red, IR \n")

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
        ir = data[1][3:-5]
    except IndexError:
        continue

    write_data = str(red + ", " + ir)
    file.write(write_data + "\n")  # write data with a newline

    if print_data:
        print("Red={}, IR={}".format(red, ir))

    line = line + 1

print("Collection of {} samples completed!".format(samples))
file.close()
