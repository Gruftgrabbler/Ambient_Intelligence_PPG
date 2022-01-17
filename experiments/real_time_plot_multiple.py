#!/usr/bin/env python

from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import copy


class serialPlot:
    def __init__(self, serialPort='/dev/ttyUSB0', serialBaud=38400, plotLength=100, dataNumBytes=2, numPlots=1):
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        self.rawData = bytearray(numPlots * dataNumBytes)
        self.dataType = None
        if dataNumBytes == 2:
            self.dataType = 'h'  # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = 'f'  # 4 byte float
        self.data = []
        self.privateData = None  # for storing a copy of the data so all plots are synchronized
        for i in range(numPlots):  # give an array for each type of data and store them in a list
            self.data.append(collections.deque([0] * plotLength, maxlen=plotLength))
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0

        print('Trying to connect to: ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serialPort, serialBaud, timeout=4)
            print('Connected to ' + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serialPort) + ' at ' + str(serialBaud) + ' BAUD.')

    def readSerialStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            while self.isReceiving != True:
                time.sleep(0.1)

    def getSerialData(self, frame, lines, lineValueText, lineLabel, timeText, pltNumber):
        if pltNumber == 0:  # in order to make all the clocks show the same reading
            currentTimer = time.perf_counter()
            self.plotTimer = int((currentTimer - self.previousTimer) * 1000)  # the first reading will be erroneous
            self.previousTimer = currentTimer
        self.privateData = copy.deepcopy(
            self.rawData)  # so that the 3 values in our plots will be synchronized to the same sample time
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
        data = self.privateData[(pltNumber * self.dataNumBytes):(self.dataNumBytes + pltNumber * self.dataNumBytes)]
        value, = struct.unpack(self.dataType, data)
        self.data[pltNumber].append(value)  # we get the latest data point and append it to our array
        lines.set_data(range(self.plotMaxLength), self.data[pltNumber])
        lineValueText.set_text('[' + lineLabel + '] = ' + str(value))

    def backgroundThread(self):  # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')


def makeFigure(xLimit, yLimit, title):
    xmin, xmax = xLimit
    ymin, ymax = yLimit
    fig = plt.figure()
    ax = plt.axes(xlim=(xmin, xmax), ylim=(int(ymin - (ymax - ymin) / 10), int(ymax + (ymax - ymin) / 10)))
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Accelerometer Output")
    return fig, ax


def main():
    portName = '/dev/cu.usbserial-01D96591'
    baudRate = 9600
    maxPlotLength = 100  # number of points in x-axis of real time plot
    dataNumBytes = 4  # number of bytes of 1 data point
    numPlots = 3  # number of plots in 1 graph
    s = serialPlot(portName, baudRate, maxPlotLength, dataNumBytes, numPlots)  # initializes all required variables
    s.readSerialStart()  # starts background thread

    # plotting starts below
    pltInterval = 50  # Period at which the plot animation updates [ms]
    lineLabelText = ['X', 'Y', 'Z']
    title = ['X Acceleration', 'Y Acceleration', 'Z Acceleration']
    xLimit = [(0, maxPlotLength), (0, maxPlotLength), (0, maxPlotLength)]
    yLimit = [(-1, 1), (-1, 1), (-1, 1)]
    style = ['r-', 'g-', 'b-']  # linestyles for the different plots
    anim = []
    for i in range(numPlots):
        fig, ax = makeFigure(xLimit[i], yLimit[i], title[i])
        lines = ax.plot([], [], style[i], label=lineLabelText[i])[0]
        timeText = ax.text(0.50, 0.95, '', transform=ax.transAxes)
        lineValueText = ax.text(0.50, 0.90, '', transform=ax.transAxes)

        anim_ = animation.FuncAnimation(fig, s.getSerialData,
                                        fargs=(lines, lineValueText, lineLabelText[i], timeText, i),
                                        interval=pltInterval)
        anim.append(anim_)
        anim_.save()
        plt.legend(loc="upper left")

    plt.show()

    s.close()


if __name__ == '__main__':
    main()
