#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import serial

app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('live plot from serial')
curve = p.plot()

data_array = [0]
ser = serial.Serial("/dev/cu.usbserial-01D96591", 9600)


def update():
    global curve, data_array
    get_data = ser.readline().decode()
    data = get_data.split(',')

    data_array.append(int(data[0]))
    xdata = np.array(data, dtype='float64')
    curve.setData(xdata)
    app.processEvents()


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec()
