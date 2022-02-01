import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from tabulate import tabulate
from scipy.interpolate import InterpolatedUnivariateSpline


def read_datafile(file_name):
    data_read = np.loadtxt(file_name, delimiter=',', skiprows=1)
    _data = Data(
        sensor_red=data_read[:, 1],
        sensor_ir=data_read[:, 2],
        time=data_read[:, 0] / 1000
    )
    return _data


def filter_signal(signal, sampling_rate=20, order=4, lowpass_cutoff=3):
    nyq = sampling_rate / 2
    sos = scipy.signal.butter(order, lowpass_cutoff / nyq, btype='low', analog=False, output='sos')
    w, h = scipy.signal.sosfreqz(sos, worN=1500)  # Filter Frequency Response
    filtered_data = scipy.signal.sosfiltfilt(sos, signal)
    return filtered_data, w, h


class Data:
    def __init__(self, sensor_red, sensor_ir, time):
        self.red = sensor_red
        self.ir = sensor_ir
        self.time = time - time[0]


class PPGCalculator:
    def __init__(self, sensor_data: Data, print_data=True, plot_data=False):
        self.print_data = print_data
        self.plot_data = plot_data

        self.data = sensor_data
        self.data_dict = None

    class Baseline:
        def __init__(self, signal):
            self.baseline, self.signal_start = self.calc(signal)

        def calc(self, signal, threshold=-50):
            gradient = np.gradient(signal, axis=0)
            signal_start = int(next(idx for idx, value in enumerate(gradient) if value < threshold))
            baseline = signal[signal_start]
            return baseline, signal_start

    class Peaks:
        def __init__(self, signal, baseline):
            self.last_peak, self.peaks = self.calc(signal, baseline)

        @staticmethod
        def calc(signal, baseline):
            """
            Calculate the time stems of all peaks of the given signal above the baseline.
            Return: Last Peak as int, all other peaks as np.list
            """
            peaks, _ = scipy.signal.find_peaks(signal, height=baseline + 10, threshold=1, distance=1, prominence=500)
            last_peak = peaks[-1]  # save the last peak in a special variable
            peaks = peaks[:-1]  # remove last peak from the peaks list
            return int(last_peak), peaks

    class InitialRefillTime:
        def __init__(self, signal, time, last_peak: int, baseline: int):
            self.line, self.time, self.p3_index, self.p3_time = self.calc(signal, time, last_peak, baseline)

        @staticmethod
        def calc(signal, time, last_peak: int, baseline: int):
            # Find the point on the ppg curve which is 3 sec ahead of the last maximum (required for Inital-Refill-Time)
            p3_idx = next(
                idx for idx, value in enumerate(time[last_peak:]) if value > time[last_peak] + 3) + last_peak
            p3_time = time[p3_idx]

            # calculate initial-refill time
            # approximate line through last peak and p3
            delta_y = signal[p3_idx] - signal[last_peak]
            delta_x = time[p3_idx] - time[last_peak]
            line_amplitude = delta_y / delta_x * (time - time[last_peak]) + signal[last_peak]

            # remove all entries before last_peak
            line_amplitude = line_amplitude[int(last_peak):]

            # find first point of intersection between the approximated line and baseline
            baseline_line_intersection_idx = next(idx for idx, value in enumerate(line_amplitude) if
                                                  value - baseline < 0)  # schnittpunkt zwischen line und baseline
            # remove all entries after intersection
            line_amplitude = line_amplitude[:baseline_line_intersection_idx]
            line_time = time[int(last_peak):last_peak + baseline_line_intersection_idx]
            line = [line_time, line_amplitude]

            # calculate initial-refill time
            initial_filling_time = line_time[-1] - line_time[0]
            return line, initial_filling_time, p3_idx, p3_time

    class HalfRefillTime:
        def __init__(self, signal, time, last_peak: int, baseline: int):
            self.time, self.idx, self.amplitude = self.calc(signal, time, baseline, last_peak)

        @staticmethod
        def calc(signal, time, baseline: int, last_peak: int):
            threshold_half_refill = baseline + (signal[last_peak] - baseline) / 2
            half_refill_idx = next(
                idx for idx, value in enumerate(signal[last_peak:]) if
                value < threshold_half_refill) + last_peak

            time_half_refill = time[half_refill_idx]
            half_refill_amp = signal[half_refill_idx]
            half_refill_time = time_half_refill - time[last_peak]
            return half_refill_time, half_refill_idx, half_refill_amp

    class FullRefillTime:
        def __init__(self, signal, time, baseline: int, last_peak: int):
            self.refill_time, self.intersection_time, self.intersection_amplitude, self.intersection_time_index, \
                = self.calc(signal, time, baseline, last_peak)

        def calc(self, signal, time, baseline: int, last_peak: int):
            """
            Find the intersection between the signal and the baseline after decline of the curve
            Return full_refill_time: Time between the last peak and the intersection
            Return time_end_intersection: Time of the intersection between signal and baseline
            Return amplitude_end_intersection: Amplitude of the signal at intersection point
            """

            timeidx_end_intersection = next(
                idx for idx, value in enumerate(signal[last_peak:]) if value < baseline) + last_peak
            time_end_intersection = time[timeidx_end_intersection]
            amplitude_end_intersection = signal[timeidx_end_intersection]
            full_refill_time = time_end_intersection - time[last_peak]
            return full_refill_time, time_end_intersection, amplitude_end_intersection, timeidx_end_intersection

    def calc_ppg(self):
        baseline = PPGCalculator.Baseline(self.data.red)
        # self.data.time = self.data.time - baseline.signal_start

        signal_filtered, w, h = filter_signal(self.data.red)
        peaks = PPGCalculator.Peaks(signal_filtered, baseline.baseline)
        initial_refill_time = PPGCalculator.InitialRefillTime(self.data.red, self.data.time, peaks.last_peak,
                                                              baseline.baseline)
        half_refill_time = PPGCalculator.HalfRefillTime(self.data.red, self.data.time, peaks.last_peak,
                                                        baseline.baseline)
        full_refill_time = PPGCalculator.FullRefillTime(self.data.red, self.data.time, baseline.baseline,
                                                        peaks.last_peak)

        venous_pump_capacity = (self.data.red[peaks.last_peak] - baseline.baseline) / baseline.baseline * 100

        x_np = np.array(self.data.time[peaks.last_peak:full_refill_time.intersection_time_index])
        y_np = (np.array(self.data.red[
                         peaks.last_peak:full_refill_time.intersection_time_index])
                - baseline.baseline) / baseline.baseline * 100
        venous_pump_function = scipy.integrate.trapz(y_np, x_np)

        # Store all calculated data in a dictonary structre.
        self.data_dict = {'baseline': baseline.baseline,
                          'signal_start': baseline.signal_start,
                          'signal_start_time': self.data.time[baseline.signal_start],
                          'last_peak_index': peaks.last_peak,
                          'last_peak_time': self.data.time[peaks.last_peak],
                          'last_peak_amp': signal_filtered[peaks.last_peak],
                          'peaks_time_indizes': peaks.peaks,
                          'p3_index': initial_refill_time.p3_index,
                          'p3_time': initial_refill_time.p3_time,
                          'p3_amp': self.data.red[initial_refill_time.p3_index],
                          'line_approx': initial_refill_time.line,
                          'initial_refill_time': initial_refill_time.time,
                          'signal_end_time': full_refill_time.intersection_time,
                          'signal_end_amp': full_refill_time.intersection_amplitude,
                          'half_refill_index': half_refill_time.idx,
                          'half_refill_time': half_refill_time.time,
                          'half_refill_amp': half_refill_time.amplitude,
                          'full_refill_time': full_refill_time.refill_time,
                          'full_refill_amp': full_refill_time.intersection_amplitude,
                          'venous_pump_capacity': venous_pump_capacity,
                          'venous_pump_function': venous_pump_function,
                          'signal_filtered': signal_filtered,
                          }

    def print_ppg(self):
        print(tabulate([
                        ['Algorithm specific parameters'],
                        ['Baseline', self.data_dict['baseline']],
                        # ['Signal Starting idx', self.data_dict['signal_start']],
                        ['Signal Starting Time', self.data_dict['signal_start_time']],
                        ['Signal Ending Time', self.data_dict['signal_end_time']],
                        ['Signal Ending Amplitude', self.data_dict['signal_end_amp']],
                        ['P3 Index', self.data_dict['p3_index']],
                        ['P3 Time', self.data_dict['p3_time']],
                        ['P3 Amplitude', self.data_dict['p3_amp']],
                        ['Half-Refill Idx', self.data_dict['half_refill_index']],
                        ['Half-Refill Amplitude', self.data_dict['half_refill_amp']],
                        ['', ],
                        ['Medical Parameters'],
                        ['Initial-Refill Time T_i(s)', self.data_dict['initial_refill_time']],
                        ['Half-Refill Time T_50(s)', self.data_dict['half_refill_time']],
                        ['Venous Filling Time T_0(s)', self.data_dict['full_refill_time']],
                        ['Venous pump capacity V_0 (%)', self.data_dict['venous_pump_capacity']],
                        ['Venous pump function F_0 (%s)', self.data_dict['venous_pump_function']],
                        ], headers=['Parameter', 'Value'], tablefmt="grid", floatfmt=".3f"))

    def plot_ppg_calc(self, plot_ir=False, plot_red_filter=False, plot_derivation=False):
        num_subplots = 1 + sum([plot_ir, plot_red_filter, plot_derivation])
        plot_rows = 2
        plot_cols = num_subplots // plot_rows + num_subplots % plot_rows
        plot_index = 1

        if plot_ir:
            plt.subplot(plot_rows, plot_cols, plot_index)
            plt.plot(self.data.time, self.data.ir, label='ir readings')
            plt.grid()
            plt.legend()
            plot_index += 1

        # Plot RED Readings
        ax_red = plt.subplot(plot_rows, plot_cols, plot_index)
        plt.plot(self.data.time, self.data.red, c='r', label='red readings')
        plt.plot(self.data.time, np.full((len(self.data.time)), self.data_dict['baseline']), '--')
        plt.grid()
        plt.legend()

        # Plot Measurements Points
        plt.plot(self.data_dict['signal_start_time'], self.data_dict['baseline'], 'go', label='Measurement start')
        plt.plot(self.data_dict['p3_time'], self.data_dict['p3_amp'], 'bo',
                 label='3s Kurvenabfall')  # FIXME Last Peak + 3s
        plt.plot(self.data_dict['last_peak_time'], self.data_dict['last_peak_amp'], 'x', c='b')  # plot peaks
        # TODO Plot all other peaks
        plt.plot(self.data_dict['line_approx'][0], self.data_dict['line_approx'][1], '--')

        if plot_red_filter:
            plot_index += 1
            ax_red_filter = plt.subplot(plot_rows, plot_cols, plot_index, sharex=ax_red)
            plt.plot(self.data.time, self.data_dict['signal_filtered'], c='y', label='Red Filtered')
            plt.plot(self.data.time, np.full((len(self.data.time)), self.data_dict['baseline']), '--')
            plt.plot(self.data.time[self.data_dict['peaks_time_indizes']],
                     self.data_dict['signal_filtered'][self.data_dict['peaks_time_indizes']], 'x')  # plot peaks
            plt.plot(self.data.time[self.data_dict['last_peak_index']],
                     self.data_dict['signal_filtered'][self.data_dict['last_peak_index']], 'x',
                     c='r')  # plot last peaks
            plt.grid()
            plt.legend()
            plot_index += 1

        if plot_derivation:
            plt.subplot(plot_rows, plot_cols, plot_index)
            plt.plot(self.time, gradient, c='k', label='Red Derivation')
            plot_index += 1

        plt.tight_layout()
        plt.show()

    def plot_ppg_raw(self):
        plt.plot(self.data.time, self.data.red, c='r', label='red readings')
        plt.tight_layout()
        plt.grid()
        plt.show()


def main():
    file = 'readings/good_readings/data3.csv'
    data = read_datafile(file)
    ppg = PPGCalculator(data)
    ppg.calc_ppg()
    ppg.print_ppg()
    ppg.plot_ppg_calc(plot_red_filter=True)


if __name__ == '__main__':
    main()
