#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Mon Apr 20 19:20:34 2015
This program currently works to just bring in data and parse it
into something meaningful.
Plots real time Magnetometer data (HMC5983)
USED with the Arduino HMC_5983_LOG.ino code
Data is coming in at 230400 baud as comma separated data formatted by the Arduino.
CHECK OUT https://gist.github.com/turbinenreiter/7898985
for more details on how to plot serial data in PyQTgraph
Also, Check out   www.pyqtgraph.org
@author: rtb 9/27/2015
"""
import csv
import os

from pyqtgraph import Qt
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import sys
import serial
import codecs
import ctypes
import platform
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import time as t

def make_dpi_aware():
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

make_dpi_aware()

# initialize plot window
app = QtGui.QApplication([])

p=pg.plot()
p.setWindowTitle('Live Plot from Serial')
p.setInteractive(True)
# setting plot window background color to white
p.setBackground('w')
p.showGrid(x = True, y = True, alpha = 0.3)
p.setLabel('bottom', 'Time', 's')
p.setXRange(-10, 0)

# initialize variables for plotting
# Plot in chunks, adding one new plot curve for every 100 samples
chunkSize = 100
# Remove chunks after we have 20
maxChunks = 20
startTime = pg.ptime.time()
ptr = 0
data1 = np.empty((chunkSize + 1, 2))
data2 = np.empty((chunkSize + 1, 2))
data3 = np.empty((chunkSize + 1, 2))
curves1 = []
curves2 = []
curves3 = []
# curve1 = p.plot(pen=(255, 0, 0), name="Red millis curve")
curve2 = p.plot(pen=(0, 255, 0), name="Green sensor_red curve")
curve3 = p.plot(pen=(0, 0, 255), name="Blue sensor_ir curve")

# csv file path
DIRECTORY = 'readings/'  # Path of directory where data is been stored
FILE_NAME = 'reading_' + t.strftime('%d-%m-%Y_%H-%M-%S') + '.csv'  # name of the CSV file generated
FILE_PATH = DIRECTORY + FILE_NAME

# initialize serial connection
# ToDo: implement auto detection
ser = serial.Serial('COM16', 9600, timeout=1)  # open first serial port
ser.close()
ser.open()

print('Connected {} to port {} with baud rate{}.'.format(ser.name, ser.port, ser.baudrate))

ser.flush()
ser.reset_input_buffer()

def update():
    global p, ptr, curve1, data1, curves1, curve2, data2, curves2, curve3, data3, curves3
    line = codecs.decode((ser.readline()))

    DataArray = line.split(',')

    #  TODO Add filter to remove invalid data
    # Filter all non digit characters from the serial reading
    #i: int = 0
    #for _ in DataArray:
    #    DataArray[i] = "".join(filter(str.isdigit, DataArray[i]))
    #    i += 1

    if len(DataArray) > 2:
        millis = int(DataArray[0])
        sensor_red = int(DataArray[1])
        sensor_ir = int(DataArray[2])

        print('Millis={}\t Red={}\t IR={}'.format(millis, sensor_red, sensor_ir))

        with open(FILE_PATH, 'a', newline='') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow([millis, sensor_red, sensor_ir])

        now = pg.ptime.time()
        #for c in curves1:
        #    c.setPos(-(now - startTime), 0)
        for c in curves2:
            c.setPos(-(now - startTime), 0)
        for c in curves3:
            c.setPos(-(now - startTime), 0)

        i = ptr % chunkSize
        if i == 0:
            #curve1 = p.plot(pen=(0, 255, 0), name="Green millis curve")
            curve2 = p.plot(pen=(255, 0, 0), name="Red sensor_red curve")
            curve3 = p.plot(pen=(0, 0, 255), name="Blue sensor_ir curve")

            #curves1.append(curve1)
            curves2.append(curve2)
            curves3.append(curve3)

            last1 = data1[-1]
            last2 = data2[-1]
            last3 = data3[-1]

            #data1 = np.empty((chunkSize + 1, 2))
            data2 = np.empty((chunkSize + 1, 2))
            data3 = np.empty((chunkSize + 1, 2))

            #data1[0] = last1
            data2[0] = last2
            data3[0] = last3

            #while len(curves1) > maxChunks:
            #    c = curves1.pop(0)
            #    p.removeItem(c)
            while len(curves2) > maxChunks:
                c = curves2.pop(0)
                p.removeItem(c)
            while len(curves3) > maxChunks:
                c = curves3.pop(0)
                p.removeItem(c)

        else:
            #curve1 = curves[-1]
            curve2 = curves2[-1]
            curve3 = curves3[-1]

        #data1[i + 1, 0] = now - startTime
        data2[i + 1, 0] = now - startTime
        data3[i + 1, 0] = now - startTime

        #data1[i + 1, 1] = int(millis)
        data2[i + 1, 1] = int(sensor_red)
        data3[i + 1, 1] = int(sensor_ir)

        #curve1.setData(x=data[:i + 2, 0], y=data[:i + 2, 1])
        curve2.setData(x=data2[:i + 2, 0], y=data2[:i + 2, 1])
        curve3.setData(x=data3[:i + 2, 0], y=data3[:i + 2, 1])

        ptr += 1

        app.processEvents()

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)


# erzeugt .csv-Datei falls sie noch nicht vorhanden ist und initialisiert erste Spalte mit dem header
def createNewCSV(file_path):
    # CREATE TARGET DIRECTORY IF NECESSARY
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)

    with open(file_path, 'w', newline='') as outfile:
        header = ['Millis', 'Red', 'IR']

        csv_writer = csv.DictWriter(outfile, fieldnames=header)
        csv_writer.writeheader()

    print('File created: ' + file_path)
    outfile.close()


if __name__ == '__main__':
    createNewCSV(FILE_PATH)
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
