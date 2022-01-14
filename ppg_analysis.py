import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.cbook as cbook

# Plot Parameters
params = {'mathtext.default': 'regular',
          'axes.titlesize': 16,
          'axes.labelsize': 14,
          'font.family': 'sans-serif',
          'font.sans-serif': 'Tahoma'
          }  # mathematische Achsenbeschriftungen
plt.rcParams.update(params)

file = 'readings/good_readings/data1.csv'
# list_of_files = glob.glob('C:/Users/Philipp Witulla/PycharmProjects/AmbientIntellicence/Sensordaten/*.csv')
# * means all if need specific format then *.csv
# latest_file = max(list_of_files, key=os.path.getctime)
print(file)


def read_datafile(file_name):
    # the skiprows keyword is for skipping the csv header
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    return data


data1 = read_datafile(file)

# Plot Axis
time = data1[:, 0]
sensor_red = data1[:, 1]
sensor_ir = data1[:, 2]

# Filter data
# Digital Highpass Filter at 5 Hz (4th Order Butterworth Filter)
# Digital Lowpass Filter at 0.3Hz (Remove DC-Offset - 4th Order Butterworth Filter)
num_poles = 4
nyq = 10
low_cut_freq = 0.3 / nyq
high_cut_freq = 5 / nyq
b, a = signal.butter(num_poles, [low_cut_freq, high_cut_freq], btype='band')
filtered_red = signal.lfilter(b, a, sensor_red)

#


# tests how to set markers in the plot
markers_on = [60000, 62000]

# Create Plot
# fig, axs = plt.subplots(2)
# ax1 = axs[0]
fig = plt.figure(111)

ax1 = fig.add_subplot(111)

ax1.set_title("MAX30102 Serial Readings")
ax1.set_xlabel('Time $(ms)$')
ax1.set_ylabel('Amplitude')

ax1.plot(time, sensor_red, c='r', label='Red')
ax1.plot(time, sensor_ir, c='b', label='IR')
ax1.plot(time, filtered_red, c='g', label='Red Filterd', markevery=markers_on)

leg = ax1.legend()
plt.grid()
plt.tight_layout()

plt.legend()
plt.show()
