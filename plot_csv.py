import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import glob
import os

import scipy.signal
from scipy import signal

params = {'mathtext.default': 'regular',
          'axes.titlesize': 16,
          'axes.labelsize': 14,
          'font.family': 'sans-serif',
          'font.sans-serif': 'Tahoma'
          }  # mathematische Achsenbeschriftungen
plt.rcParams.update(params)

PATH = 'readings/good_readings/'
FILE = 'data3.csv'
latest_file = PATH + FILE


# list_of_files = glob.glob( 'C:/Users/Philipp
# Witulla/PycharmProjects/Ambient_Intelligence_PPG/good_readings/reading_14-01-2022_11-53-52.csv')  # glob.glob(
# 'C:/Users/Philipp Witulla/PycharmProjects/Ambient_Intelligence_PPG/readings/*.csv') # * means all if need specific
# format then *.csv latest_file = max(list_of_files, key=os.path.getctime) print(latest_file)


def read_datafile(file_name):
    # the skiprows keyword is for skipping the csv header
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    return data


data1 = read_datafile(latest_file)

time = data1[:, 0] / 1000
sensor_red = data1[:, 1]
sensor_ir = data1[:, 2]

# normalize time to begin with 0
time = time - time[0]

# Filter data
# Digital Highpass Filter at 5 Hz (4th Order Butterworth Filter)
# Digital Lowpass Filter at 0.3Hz (Remove DC-Offset - 4th Order Butterworth Filter)
sampling_rate = 20
num_poles = 4
nyq = sampling_rate / 2
highpass_cutoff = 0.3 / nyq  # NOT USED ATM
lowpass_cutoff = 3 / nyq  # 3 Hz
# b, a = signal.butter(num_poles, [low_cut_freq, high_cut_freq], btype='band')  # , fs=sampling_rate)
# filtered_red = signal.lfilter(b, a, sensor_red)
# sos = signal.butter(num_poles, [low_cut_freq, high_cut_freq], btype='band', analog=False, output='sos')
sos = signal.butter(num_poles, lowpass_cutoff, btype='low', analog=False, output='sos')  # filter coefficients
w, h = signal.sosfreqz(sos, worN=1500)  # Filter Frequency Response
filtered_red = signal.sosfiltfilt(sos, sensor_red)

# Create Derivation of signal
# dx = 50
gradient_red = np.gradient(sensor_red, axis=0)

# find baseline
# find first element in gradient values below -40 to use as starting point of our measurement
starting_threshold = -50
timeidx_start = next(idx for idx, value in enumerate(gradient_red) if value < starting_threshold)
# find more precise element in gradient values below -40 to use as starting point of our measurement
starting_threshold_precise = min(gradient_red[:timeidx_start - 5])
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

# find all peaks of the signal
peaks, _ = scipy.signal.find_peaks(filtered_red, height=baseline + 10, threshold=1, distance=1,
                                   prominence=500)
last_peak = peaks[-1]  # save the last peak in a special variable
peaks = peaks[:-1]  # remove last peak from the peaks list
# find maximum
# idx_last_peak = 406  # FIXME Delete this line
time_last_peak = time[last_peak]  # FIXME Delete this line

amplitude_last_peak = sensor_red[last_peak]
print("\nlast peak idx: \t\t\t" + str(last_peak))
print("last peak Time: \t\t" + str(time_last_peak))
print("last peak Amplitude: \t" + str(amplitude_last_peak))

# find point after 3s Kurvenabfall
idx_3s_kurvenabfall = next(
    idx for idx, value in enumerate(time[last_peak:]) if value > time_last_peak + 3) + last_peak
time_3s_kurvenabfall = time[idx_3s_kurvenabfall]
amplitude_3s_kurvenabfall = sensor_red[idx_3s_kurvenabfall]

# approximate line through last peak
delta_y = sensor_red[idx_3s_kurvenabfall] - sensor_red[last_peak]
delta_x = time[idx_3s_kurvenabfall] - time[last_peak]
line_approx = delta_y / delta_x * (time - time[last_peak]) + sensor_red[last_peak]
abschneidepunkt = int(last_peak)
line_approx = line_approx[abschneidepunkt:]
time_abschneidepunkt = time[abschneidepunkt:]
# schnittpunkt_baseline = next(idx for idx, value in enumerate(line_approx) if value == baseline)
i = 0
for _ in line_approx:
    if line_approx[i] <= baseline:
        break
    i += 1
line_approx = line_approx[:i]

print("\n3s Kurvenabfall idx : \t\t" + str(idx_3s_kurvenabfall))
print("3s Kurvenabfall Time: \t\t" + str(time_3s_kurvenabfall))
print("3s Kurvenabfall Amplitude: \t" + str(amplitude_3s_kurvenabfall))

# find point of half-refill time (Zeitintervall zwischen Kurvenmaximum und dem Zeitpunkt wo Kurvenabfall die halbe Amplitude von R_max unterschreitet)
threshold_half_refill = baseline + (amplitude_last_peak - baseline) / 2
idx_half_refill = next(
    idx for idx, value in enumerate(sensor_red[last_peak:]) if value < threshold_half_refill) + last_peak
time_half_refill = time[idx_half_refill]
amplitude_half_refill = sensor_red[idx_half_refill]
half_refill_time = time_half_refill - time_last_peak
print("\nHalf-refill time idx: \t\t" + str(idx_half_refill))
print("Half-refill timepoint: \t\t" + str(time_half_refill))
print("Half-refill time Amplitude: " + str(amplitude_half_refill))

# find end of Kurvenabfall (= Schnittpunkt von sensor_red mit baseline)
timeidx_ende_kurvenabfall = next(
    idx for idx, value in enumerate(sensor_red[last_peak:]) if value < baseline) + last_peak
time_ende_kurvenabfall = time[timeidx_ende_kurvenabfall]
amplitude_ende_kurvenabfall = sensor_red[timeidx_ende_kurvenabfall]
print("\nSignal Ending idx: \t\t" + str(timeidx_ende_kurvenabfall))
print("Signal Ending Time: \t" + str(time[timeidx_ende_kurvenabfall]))

# find venous refill time (= Zeitintervall zwischen Kurvenmaximum nach Belastungsstop und Ende des Kurvenabfalls)
venous_refill_time = time_ende_kurvenabfall - time_last_peak
venous_pump_capacity = (amplitude_last_peak - baseline) / baseline * 100  # Angabe in [%]
print("\nVenous refill time T_0  : " + str(venous_refill_time))
print("Half-refill time T_50\t: " + str(half_refill_time))
print("Initial filling time T_i: missing")
print("Venous pump capacity V_0: " + str(venous_pump_capacity))
print("Venous pump function F_0: missing")


# ToDo: Berechne Gerade durch last_peak und 3s_Kurvenabfall und den Schnittpunkt der Gerade mit der Baseline für initiale Auffüllzeit

def plot_data(plot_ir=False, plot_red_filter=True, plot_derivation=False):
    # Dynamic Plot Nummering
    num_subplots = sum([plot_ir, plot_red_filter, plot_derivation]) + 1
    plot_rows = 2
    plot_cols = num_subplots // plot_rows + num_subplots % plot_rows
    plot_index = 1

    if plot_ir:
        plt.subplot(plot_rows, plot_cols, plot_index)
        plt.plot(time, sensor_ir, label='ir readings')
        plt.grid()
        plt.legend()
        plot_index += 1

    # Plot RED Readings
    ax_red = plt.subplot(plot_rows, plot_cols, plot_index)
    plt.plot(time, sensor_red, c='r', label='red readings')
    plt.plot(time, np.full((len(time)), baseline), '--')
    plt.grid()
    plt.legend()
    plot_index += 1

    # Plot Measurements Points
    plt.plot(time_signal_start, baseline, 'go', label='Measurement start')
    plt.plot(time_3s_kurvenabfall, amplitude_3s_kurvenabfall, 'bo', label='3s Kurvenabfall')  # FIXME Last Peak + 3s
    plt.plot(time[peaks], sensor_red[peaks], 'x', c='b')  # plot peaks
    plt.plot(time[last_peak], sensor_red[last_peak], 'x', c='g')  # plot last peaks
    plt.plot(time_abschneidepunkt[:i], line_approx, '--')

    if plot_red_filter:
        ax_red_filter = plt.subplot(plot_rows, plot_cols, plot_index, sharex=ax_red)
        plt.plot(time, filtered_red, c='y', label='Red Filtered')
        plt.plot(time, np.full((len(time)), baseline), '--')
        plt.plot(time[peaks], filtered_red[peaks], 'x')  # plot peaks
        plt.plot(time[last_peak], filtered_red[last_peak], 'x', c='r')  # plot last peaks
        plt.grid()
        plt.legend()
        plot_index += 1

    if plot_derivation:
        plt.subplot(plot_rows, plot_cols, plot_index)
        plt.plot(time, gradient_red, c='k', label='Red Derivation')
        plot_index += 1

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # TODO Implement Argument Parser
    PLOT_IR = False
    PLOT_RED_FILTER = True
    PLOT_DERIVATION = False

    plot_data(PLOT_IR, PLOT_RED_FILTER, PLOT_DERIVATION)
