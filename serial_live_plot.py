import serial
import matplotlib.pyplot as plt
import numpy as np
plt.ion()
fig=plt.figure()


i=0
x=list()
y=list()
ser = serial.Serial('COM16',9600)
ser.close()
ser.open()
while True:

    data1 = ser.readline()
    print(data1.decode())

    data_string = data1.decode()
    if len(data_string.split(',')) <3:
        continue

    millis = data_string.split(',')[0]
    red = data_string.split(',')[1]
    ir = data_string.split(',')[2]

    plt.scatter(i, float(red))
    plt.scatter(millis, float(ir))
    i += 1
    plt.show()
    plt.pause(0.001)  # Note this correction