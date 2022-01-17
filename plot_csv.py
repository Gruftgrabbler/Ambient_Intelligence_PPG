import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import glob
import os
from scipy import signal

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
sensor_red = data1[:, 1]
sensor_ir = data1[:, 2]

# normalize time to begin with 0 
time = time-time[0]

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


# find baseline
# find first element in gradient values below -40 to use as starting point of our measurement
starting_threshold = -50
timeidx_start = next(idx for idx, value in enumerate(gradient_red) if value < starting_threshold)
# find more precise element in gradient values below -40 to use as starting point of our measurement
starting_threshold_precise = min(gradient_red[:timeidx_start-5])
timeidx_start_precise = next(idx for idx, value in enumerate(gradient_red) if value < starting_threshold)

baseline = sensor_red[timeidx_start_precise]
time_signal_start = time[timeidx_start_precise]

# normalize time to begin with starting point of measurement
# time = time-time_signal_start
# time_signal_start = 0

print("\nBaseline: \t\t\t\t" + str(sensor_red[timeidx_start_precise]))
# print("\nstarting_threshold_precise: " + str(starting_threshold_precise) + "\ntime_start: " + str(time[timeidx_start]) + "\ttime_start_precise: " + str(time[timeidx_start_precise]))
print("\nSignal Starting idx: \t" + str(timeidx_start_precise))
print("Signal Starting Time: \t" + str(time[timeidx_start_precise]))

# find maximum
idx_last_peak = 1523  # 406  # 1523      #   manually defined # ToDo: get idx with peak detection algorithm
time_last_peak = time[idx_last_peak]
amplitude_last_peak = sensor_red[idx_last_peak]
print("\nlast peak idx: \t\t\t" + str(idx_last_peak))
print("last peak Time: \t\t" + str(time_last_peak))
print("last peak Amplitude: \t" + str(amplitude_last_peak))

# find point after 3s Kurvenabfall
idx_3s_kurvenabfall = next(idx for idx, value in enumerate(time[idx_last_peak:]) if value > time_last_peak+3) + idx_last_peak
time_3s_kurvenabfall = time[idx_3s_kurvenabfall]
amplitude_3s_kurvenabfall = sensor_red[idx_3s_kurvenabfall]
print("\n3s Kurvenabfall idx : \t\t" + str(idx_3s_kurvenabfall))
print("3s Kurvenabfall Time: \t\t" + str(time_3s_kurvenabfall))
print("3s Kurvenabfall Amplitude: \t" + str(amplitude_3s_kurvenabfall))

# find point of half-refill time (Zeitintervall zwischen Kurvenmaximum und dem Zeitpunkt wo Kurvenabfall die halbe Amplitude von R_max unterschreitet)
threshold_half_refill = baseline + (amplitude_last_peak-baseline)/2
idx_half_refill = next(idx for idx, value in enumerate(sensor_red[idx_last_peak:]) if value < threshold_half_refill) + idx_last_peak
time_half_refill = time[idx_half_refill]
amplitude_half_refill = sensor_red[idx_half_refill]
half_refill_time = time_half_refill - time_last_peak
print("\nHalf-refill time idx: \t\t" + str(idx_half_refill))
print("Half-refill timepoint: \t\t" + str(time_half_refill))
print("Half-refill time Amplitude: " + str(amplitude_half_refill))

# find end of Kurvenabfall (= Schnittpunkt von sensor_red mit baseline)
timeidx_ende_kurvenabfall = next(idx for idx, value in enumerate(sensor_red[idx_last_peak:]) if value < baseline) + idx_last_peak
time_ende_kurvenabfall = time[timeidx_ende_kurvenabfall]
amplitude_ende_kurvenabfall = sensor_red[timeidx_ende_kurvenabfall]
print("\nSignal Ending idx: \t\t" + str(timeidx_ende_kurvenabfall))
print("Signal Ending Time: \t" + str(time[timeidx_ende_kurvenabfall]))

# find venous refill time (= Zeitintervall zwischen Kurvenmaximum nach Belastungsstop und Ende des Kurvenabfalls)
venous_refill_time = time_ende_kurvenabfall - time_last_peak
venous_pump_capacity = (amplitude_last_peak-baseline)/baseline * 100  # Angabe in [%]
print("\nVenous refill time T_0  : " + str(venous_refill_time))
print("Half-refill time T_50\t: " + str(half_refill_time))
print("Initial filling time T_i: missing")
print("Venous pump capacity V_0: " + str(venous_pump_capacity))
print("Venous pump function F_0: missing")


# ToDo: Berechne Gerade durch last_peak und 3s_Kurvenabfall und den Schnittpunkt der Gerade mit der Baseline für initiale Auffüllzeit



fig = plt.figure()
ax1 = fig.add_subplot(111)

ax1.set_title("MAX30102 Serial Readings")
ax1.set_xlabel('Time $(s)$')
ax1.set_ylabel('Amplitude')

ax1.plot(time, sensor_red, c='r', label='Red')
#ax1.plot(time, filtered_red, c='y', label='Red Filtered')
ax1.plot(time, np.full((len(time)), baseline), c='g', label='Red Baseline')
#ax1.plot(time, gradient_red, c='k', label='Red Derivation')
ax1.plot(time_signal_start, baseline, 'go', label='Measurement start')
ax1.plot(time_last_peak, amplitude_last_peak, 'yo', label='last peak')
ax1.plot(time_3s_kurvenabfall, amplitude_3s_kurvenabfall, 'yo', label='3s Kurvenabfall')
ax1.plot(time_half_refill, amplitude_half_refill, 'yo', label='half-refill point')
ax1.plot(time_ende_kurvenabfall, baseline, 'ro', label='Measurement end')      # replace baseline with amplitude_ende_kurvenabfall?
#ax1.plot(time, sensor_ir, c='b', label='IR')

leg = ax1.legend(loc='lower right')
plt.grid()
plt.tight_layout()  # top=0.96, bottom=0.068, left=0.049, right=0.992, hspace=0.2, wspace=0.2
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
fig.subplots_adjust(
    top=0.96,
    bottom=0.068,
    left=0.049,
    right=0.992,
    hspace=0.2,
    wspace=0.2
)
plt.show()
