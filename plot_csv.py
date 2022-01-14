import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import glob
import os

params = {'mathtext.default': 'regular',
          'axes.titlesize': 16,
          'axes.labelsize': 14,
          'font.family' : 'sans-serif',
          'font.sans-serif' : 'Tahoma'
          }        # mathematische Achsenbeschriftungen
plt.rcParams.update(params)

list_of_files = glob.glob('C:/Users/Philipp Witulla/PycharmProjects/Ambient_Intelligence_PPG/good_readings/*.csv')  # glob.glob('C:/Users/Philipp Witulla/PycharmProjects/Ambient_Intelligence_PPG/readings/*.csv') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)

def read_datafile(file_name):
    # the skiprows keyword is for skipping the csv header
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    return data

data1 = read_datafile(latest_file)

time = data1[:, 0]/1000
sensor1 = data1[:, 1]
sensor2 = data1[:, 2]

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_title("MAX30102 Serial Readings")
ax1.set_xlabel('Time $(s)$')
ax1.set_ylabel('Amplitude')

ax1.plot(time,sensor1, c='r', label='Red')
ax1.plot(time,sensor2, c='b', label='IR')

leg = ax1.legend()
plt.grid()
plt.tight_layout()

plt.show()