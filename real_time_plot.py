#!/usr/bin/env python

# NOTE THIS FILE IS NOT WORKING RIGHT NOW. I STILL HAVE TO IMPLEMENT THE DATA READING IN GET_SERIAL_DATA

"""
A likely universal file to first auto connect to an arduino or esp32 on windows and macos machines,
read the serial transmitted data on a separate thread, plot the data in real time with the help of matplotlib and
of cause save the data to a csv file in order to process it later.

The use case of this file is to plot and save data from a PPG sensor like MAX30102, but can be used with other
sensors as well. If you would like to use it on other data sources simply adjust/overwrite the __get_serial_data method.

@author: David Witulla
Sources and Guides which helped to program this code:
PySerial Documentation: https://pyserial.readthedocs.io/en/latest/index.html
Plotting Real Time Serial Data: https://thepoorengineer.com/en/arduino-python-plot/
Matplotlib FunctionAnimation Tutorial: https://www.youtube.com/watch?v=Ercd-Ip5PfQ

GLOBAL TODO's

TODO Implement Keyboard Interrupt stop
"""

import sys
from threading import Thread
import serial
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import serial.tools.list_ports
import platform


class PortScanner:
    @staticmethod
    def scan():
        """
        Query through all Serial ports and try to find a matching Arduino or ESP32 device
        Works on both Windows and macOS
        NOTE: It doesnt connect to the port, it's just return the ports address
        :return: the port of the connected device
        """
        print('Query serial ports in order to find an Arduino or ESP32.')
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            # MAC OS
            if platform.system() == "Darwin":
                if "CP2104" in port.description:
                    print("ESP 32 Detected at {}.".format(port.device))
                    return port.device

            # WINDOWS
            if platform.system() == "Windows":
                # TODO Implement Windows Auto Connect
                if "CP210" in port.description:
                    print("ESP 32 Detected at {}.".format(port.device))
                    return port.device

        print('No Serial device found!')
        sys.exit()


class DataCollector:
    def __init__(self, port: str, baud_rate: int, plot_len: int):
        # Some attribute declarations
        self.__thread = None
        self.__isReceiving: bool = False
        self.__isRunning: bool = True

        self.__plot_timer: int = 0
        self.__previous_timer: int = 0

        self.__plot_len = plot_len

        # the raw data arrays are holding all the acquired information.
        # TODO it should be refactored in a way that those data is immediately written to a csv file in
        #  order to save some RAM and prevent a slow down of the process.
        self.__raw_data_red = []  # List of integers holding the red data for the animation function to grab
        self.__raw_data_ir = []  # List of integers holding the red data for the animation function to grab

        # Stores the received data here to save it into a c
        self.csv_data = []

        # This variable holds the given data in a FIFO
        # TODO Add additional queues for red and ir data
        self.__data_queue_red = collections.deque([0] * plot_len, maxlen=plot_len)
        self.__data_queue_ir = collections.deque([0] * plot_len, maxlen=plot_len)

        # Connect to Serial Port
        try:
            self.__serial_connection = serial.Serial(port=port, baudrate=baud_rate)
            print('Connection established at {}'.format(self.__serial_connection.port))
        except:
            print('Failed to connect with {} at {} baud.'.format(port, baud_rate))
            sys.exit()

    def start_reading(self):
        """
        Starts a new thread witch is continuously reading the serial data
        """
        if self.__thread is None:
            self.__thread = Thread(target=self.__background_thread, daemon=True)
            self.__thread.start()
            # Block till we start receiving values
            while not self.__isReceiving:
                time.sleep(0.1)  # Sleep for 100ms

    def __background_thread(self):
        """
        Run the data collection and store the given data in
        :return:
        """
        # Give some buffer time for retrieving data
        time.sleep(1.0)  # Sleep 1 second

        # TODO Add reset command for the mcu here

        self.__serial_connection.reset_input_buffer()
        self.__serial_connection.flush()
        while self.__isRunning:
            # TODO REFACTOR THIS METHOD
            # Read the Serial Data
            get_data = self.__serial_connection.readline().decode()

            # Data should be in the millis,ir,red,samples format
            data = get_data.split(sep=',')

            # The length of the data array should always be 4
            # FIXME This is bullshit
            if len(data) < 4:
                continue

            # Filter all non digit characters from the serial reading
            i = 0
            for _ in data:
                data[i] = "".join(filter(str.isdigit, data[i]))
                i += 1

            # Separate the data into different variables
            try:
                red = int(data[1])
                ir = int(data[2])
            except:
                continue

            self.__raw_data_red.append(red)
            self.__raw_data_ir.append(ir)
            self.__isReceiving = True

            # TODO Add sys.args to enable/disable printing
            print_data = 'RED= ' + str(red) + ', IR= ' + str(ir)
            print(print_data)

    def get_serial_data(self, frame, lines, lineValueText, line_label, timeText):
        """
        :frame: For some reason this parameter has to be included for matplotlib doing its job
        :lines: TODO
        :lineValueText: TODO
        """
        # Calculate the exact plot interval
        current_timer = time.perf_counter()
        # the first readings will be erroneous
        self.__plot_timer = int((current_timer - self.__previous_timer) * 1000)
        self.__previous_timer = current_timer
        timeText.set_text('Plot Interval = ' + str(self.__plot_timer) + 'ms')

        # Get data and separate it into red and ir data
        cur_data_red: int = self.__raw_data_red.pop()
        cur_data_ir: int = self.__raw_data_ir.pop()

        self.__data_queue_red.append(cur_data_red)
        self.__data_queue_ir.append(cur_data_red)
        lines.set_data(range(self.__plot_len), self.__data_queue_red)
        lineValueText.set_text('[' + line_label + '] = ' + str(cur_data_red))

        # TODO Append the current data to the csv
        # self.csvData.append(self.data[-1])

    def close(self):
        """
        Close connection to serial device and stop the running thread.
        Additionally save the recorded data into a csv file.
        """
        self.__isRunning = False
        self.__thread.join()
        self.__serial_connection.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csv_data)
        # df.to_csv('path-to-csv-file.csv')


class RealTimePlot:
    """
    A class which holds the matplotlib animation. It is calling the get_serial_data method from the Data Collector
    to acquire its data.
    """

    def __init__(self, serial_device: DataCollector):
        self.__serial_device = serial_device

    def make_figure(self, x_min: int, x_max: int, y_min: int, y_max: int, interval: int):
        """
        :param x_min: minimum value of x in the animation graph
        :param x_max: maximum value of x in the animation graph
        :param y_min: minimum value of y in the animation graph
        :param y_max: maximum value of y in the animation graph
        :param interval: The interval in witch serial_device_get_data is called [ms]
            when its called fast the data acquisition will be more fluid,
            but it strongly increases the load on the CPU. Experiment with some values.
        """

        x_limit = (x_min, x_max)
        y_limit = (float(y_min - (y_max - y_min) / 10), float(y_max + (y_max - y_min) / 10))

        fig = plt.figure()

        ax = plt.axes(xlim=x_limit,
                      ylim=y_limit)
        ax.set_title('Arduino Serial INPUT')
        ax.set_xlabel('time')
        ax.set_ylabel('Serial Readings')

        line_label = 'Line Label'
        time_text = ax.text(0.50, 0.95, '', transform=ax.transAxes)
        lines = ax.plot([], [], label=line_label)[0]
        line_value_text = ax.text(0.50, 0.90, '', transform=ax.transAxes)

        # fargs contains a tuple with all parameters the get_serial_data functions need to know
        fargs = (lines, line_value_text, line_label, time_text)
        anim = animation.FuncAnimation(
            fig, func=self.__serial_device.get_serial_data, fargs=fargs, interval=interval)

        anim.save()
        plt.legend(loc='upper left')
        plt.show()

        # The code below is executed when the user closes the animation window
        # Close the thread and finish execution
        self.__serial_device.close()
        sys.exit()


def main():
    # USER INITIALISATION
    baud = 9600  # arduino runs at 9600 baud

    # Period at which the plot animation updates [ms]
    # A high value decreases CPU load
    plot_interval = 100
    max_plot_len = 1000

    # TODO Auto Scale Axis
    # Plot Axis configuration

    x_min = 0
    x_max = max_plot_len
    y_min = 64000
    y_max = 70000

    # CONNECT TO SERIAL PORT
    port = PortScanner.scan()

    ser = DataCollector(port=port, baud_rate=baud, plot_len=max_plot_len)
    print("Start reading")
    ser.start_reading()

    real_time_plotter = RealTimePlot(serial_device=ser)
    real_time_plotter.make_figure(x_min, x_max, y_min, y_max, interval=plot_interval)


if __name__ == '__main__':
    main()
