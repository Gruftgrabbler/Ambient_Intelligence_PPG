import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import glob
import os
import peakutils
from scipy import signal

params = {'mathtext.default': 'regular',
          'axes.titlesize': 16,
          'axes.labelsize': 14,
          'font.family' : 'sans-serif',
          'font.sans-serif' : 'Tahoma'
          }        # mathematische Achsenbeschriftungen
plt.rcParams.update(params)

list_of_files = glob.glob('C:/Users/Philipp Witulla/PycharmProjects/Ambient_Intelligence_PPG/good_readings/reading_14-01-2022_11-53-52.csv')  # glob.glob('C:/Users/Philipp Witulla/PycharmProjects/Ambient_Intelligence_PPG/readings/*.csv') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)

def read_datafile(file_name):
    # the skiprows keyword is for skipping the csv header
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    return data

data1 = read_datafile(latest_file)

time = data1[:, 0]/1000
sensor_red = data1[:, 1]
sensor_ir = data1[:, 2]

# calculate baseline y values
baseline_values = peakutils.baseline(sensor_red)

# Filter data
# Digital Highpass Filter at 5 Hz (4th Order Butterworth Filter)
# Digital Lowpass Filter at 0.3Hz (Remove DC-Offset - 4th Order Butterworth Filter)
sampling_rate = 20
num_poles = 2
nyq = sampling_rate / 2
low_cut_freq = 0.3 / nyq
high_cut_freq = 5 / nyq
#b, a = signal.butter(num_poles, [low_cut_freq, high_cut_freq], btype='band')  # , fs=sampling_rate)
#filtered_red = signal.lfilter(b, a, sensor_red)
sos = signal.butter(num_poles, [low_cut_freq, high_cut_freq], btype='band', analog=False, output='sos')  # , fs=sampling_rate)
filtered_red = signal.sosfiltfilt(sos, sensor_red)

# Create Derivation of signal
gradient_red = np.gradient(sensor_red, axis=0)

# find first element in gradient values below -40 to use as starting point of our measurement
starting_threshold = -40
timeidx_start = next(idx for idx, value in enumerate(gradient_red) if value < starting_threshold)      # ToDo: hardcoding überdenken

print(" Signal Starting idx: " + str(timeidx_start) + " Signal Starting Time: " + str(time[timeidx_start]))
print("Baseline: " + str(sensor_red[timeidx_start]))

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_title("MAX30102 Serial Readings")
ax1.set_xlabel('Time $(s)$')
ax1.set_ylabel('Amplitude')

ax1.plot(time,sensor_red, c='r', label='Red')
ax1.plot(time,filtered_red, c='y', label='Red Filtered')
ax1.axhline(sensor_red[timeidx_start], c='g', label='Red Baseline')
ax1.plot(time,gradient_red, c='k', label='Red Derivation')
ax1.plot(time,sensor_ir, c='b', label='IR')

leg = ax1.legend()
plt.grid()
plt.tight_layout()

plt.show()
