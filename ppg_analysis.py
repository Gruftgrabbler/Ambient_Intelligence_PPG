import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from tabulate import tabulate
from scipy.interpolate import InterpolatedUnivariateSpline


# TODO Der Algorithmus in dieser Form ist nur in der Lage die Berechnungen auf Daten auszuführen die nur eine einzelne
#  PPG Messung beinhalten. Spätere Versionen sollten in der Lage sein diese auch auf größeren Datenmengen anzuwenden,
#  da in der Praxis aus mehrere Aufnahmen gemacht werden.
#  Man könnte dies so implementieren, dass eine Übergeordnete Klasse die Daten ausliest und die einzelnen PPG Aufnahmen
#  erkennt und trennt. Die seperariten Aufnahmen können dann dem PPGCalculator übergeben werden.
#  Andere Implementierungen wären allerdings auch möglich.

def read_datafile(file_name):
    data = np.loadtxt(file_name, delimiter=',', skiprows=1)
    return data


class PPGCalculator:
    def __init__(self, file_path: str):
        self.data_file = read_datafile(file_path)

        self.time = self.data_file[:, 0] / 1000
        self.sensor_red = self.data_file[:, 1]
        self.sensor_ir = self.data_file[:, 2]

        self.time = self.time - self.time[0]  # normalize time to begin with 0

    def calc_ppg(self, print_data=True, normalize_time: str = 'None'):
        """
        Public function which will be called in order to calc the ppg data from the given signal
        """
        # find baseline, point of time where measurement starts and last peak
        baseline, signal_start = self.calc_baseline(self.sensor_red)
        data_filtered, w, h = self.__filter_data(self.sensor_red)
        last_peak, peaks = self.__find_peaks(data_filtered, baseline)

        # normalize time to begin with starting point or peak of measurement
        if normalize_time == 'start':
            self.time = self.time - self.time[signal_start]
        elif normalize_time == 'peak':
            self.time = self.time - self.time[last_peak]
        else:
            pass

        # Find the point on the ppg curve which is 3 sec ahead of the last maximum (required for Inital-Refill-Time)
        p3_idx = next(
            idx for idx, value in enumerate(self.time[last_peak:]) if value > self.time[last_peak] + 3) + last_peak
        p3_time = self.time[p3_idx]

        # calculate initial-refill time
        # approximate line through last peak and p3
        delta_y = self.sensor_red[p3_idx] - self.sensor_red[last_peak]
        delta_x = self.time[p3_idx] - self.time[last_peak]
        line_amplitude = delta_y / delta_x * (self.time - self.time[last_peak]) + self.sensor_red[last_peak]

        # TODO REFACTOR THIS SHITTY CODE BELOW
        # remove all entries before last_peak
        line_amplitude = line_amplitude[int(last_peak):]
        # find first point of intersection between the approximated line and baseline
        baseline_line_intersection_idx = next(idx for idx, value in enumerate(line_amplitude) if
                                              value - baseline < 0)  # schnittpunkt zwischen line und baseline
        # remove all entries after intersection
        line_amplitude = line_amplitude[:baseline_line_intersection_idx]
        line_time = self.time[int(last_peak):last_peak + baseline_line_intersection_idx]
        line = [line_time, line_amplitude]
        # calculate initial-refill time
        initial_filling_time = line_time[-1] - line_time[0]

        # calculate half-refill time
        threshold_half_refill = baseline + (self.sensor_red[last_peak] - baseline) / 2
        idx_half_refill = next(
            idx for idx, value in enumerate(self.sensor_red[last_peak:]) if value < threshold_half_refill) + last_peak

        time_half_refill = self.time[idx_half_refill]
        amplitude_half_refill = self.sensor_red[idx_half_refill]
        half_refill_time = time_half_refill - self.time[last_peak]

        # find first point of intersection between measured signal (sensor_red) and baseline after decline of the curve
        timeidx_end_intersection = next(
            idx for idx, value in enumerate(self.sensor_red[last_peak:]) if value < baseline) + last_peak
        time_end_intersection = self.time[timeidx_end_intersection]
        amplitude_end_intersection = self.sensor_red[timeidx_end_intersection]

        venous_refill_time = time_end_intersection - self.time[last_peak]
        venous_pump_capacity = (self.sensor_red[last_peak] - baseline) / baseline * 100  # Angabe in [%]

        # calc_venous_pump_function
        x = np.array(self.time[last_peak:timeidx_end_intersection])
        y = (np.array(self.sensor_red[last_peak:timeidx_end_intersection]) - baseline) / baseline * 100
        venous_pump_function = scipy.integrate.trapz(y, x)
        # ToDo: delete after peer-review
        # plt.plot(x,y)
        # plt.grid()
        # plt.show()

        if print_data:
            '''
            print("\nBaseline: \t\t\t\t" + str(self.sensor_red[signal_start]))
            print("Signal Starting idx: \t" + str(signal_start))
            print("Signal Starting Time: \t" + str(self.time[signal_start]))

            print("\nLast peak idx: \t\t\t" + str(last_peak))
            print("Last peak Time: \t\t" + str(self.time[last_peak]))
            print("Last peak Amplitude: \t" + str(data_filtered[last_peak]))

            print("\n3s Kurvenabfall idx : \t\t" + str(p3_idx))
            print("3s Kurvenabfall Time: \t\t" + str(p3_time))
            print("3s Kurvenabfall Amplitude: \t" + str(self.sensor_red[p3_idx]))

            print("\nSignal Ending idx: \t\t" + str(timeidx_end_intersection))
            print("Signal Ending Time: \t" + str(self.time[timeidx_end_intersection]))

            print("\nHalf-refill Time idx: \t\t" + str(idx_half_refill))
            print("Half-refill Time: \t\t" + str(time_half_refill))
            print("Half-refill Time Amplitude: " + str(amplitude_half_refill))

            print("\nVenous refill time T_0  : " + str(venous_refill_time))
            print("Half-refill time T_50\t: " + str(half_refill_time))
            print("Initial filling time T_i: missing")
            print("Venous pump capacity V_0: " + str(venous_pump_capacity))
            print("Venous pump function F_0: str(venous_pump_function)")
            '''

            print(tabulate([['Baseline', baseline],
                            ['Signal Starting idx', signal_start],
                            ['Signal Starting Time', self.time[signal_start]],
                            ['', ],
                            ['Last peak idx', last_peak],
                            ['Last peak Time', self.time[last_peak]],
                            ['Last peak Amplitude', data_filtered[last_peak]],
                            ['', ],
                            ['3s Kurvenabfall idx', p3_idx],
                            ['3s Kurvenabfall Time', p3_time],
                            ['3s Kurvenabfall Amplitude', self.sensor_red[p3_idx]],
                            ['', ],
                            ['Signal Ending idx', timeidx_end_intersection],
                            ['Signal Ending Time', self.time[timeidx_end_intersection]],
                            ['', ],
                            ['Half-refill time idx', idx_half_refill],
                            ['Half-refill timepoint', time_half_refill],
                            ['Half-refill time Amplitude', amplitude_half_refill],
                            ['', ],
                            ['Venous refill time T_0 (s)', venous_refill_time],
                            ['Half-refill time T_50 (s)', half_refill_time],
                            ['Initial filling time T_i (s)', initial_filling_time],
                            ['Venous pump capacity V_0 (%)', venous_pump_capacity],
                            ['Venous pump function F_0 (%s)', venous_pump_function],
                            ], headers=['Parameter', 'Value'], tablefmt="grid", floatfmt=".3f"))

        self.plot_data(baseline, last_peak, peaks, signal_start, p3_idx, line, data_filtered, None)

        return 0

    def __filter_data(self, sensor_data, sampling_rate=20, order=4, lowpass_cutoff=3):
        nyq = sampling_rate / 2
        sos = scipy.signal.butter(order, lowpass_cutoff / nyq, btype='low', analog=False, output='sos')
        w, h = scipy.signal.sosfreqz(sos, worN=1500)  # Filter Frequency Response
        filtered_data = scipy.signal.sosfiltfilt(sos, sensor_data)
        return filtered_data, w, h

    @staticmethod
    def __calc_gradient(self, sensor_data):
        gradient = np.gradient(sensor_data, axis=0)
        return gradient

    def __find_peaks(self, signal, baseline: int, print_data=True):
        # find all peaks of the signal
        peaks, _ = scipy.signal.find_peaks(signal, height=baseline + 10, threshold=1, distance=1, prominence=500)
        last_peak = peaks[-1]  # save the last peak in a special variable
        peaks = peaks[:-1]  # remove last peak from the peaks list

        return int(last_peak), peaks

    # ToDo
    def calc_initial_refill_time(self):
        pass

    def calc_baseline(self, sensor_data, print_data=True):
        starting_threshold = -50
        gradient = self.__calc_gradient(self, sensor_data)
        # ToDo: review before code deletion: if more precise location of baseline is necessary
        # timeidx_start = next(idx for idx, value in enumerate(gradient) if value < starting_threshold)
        # # find more precise element in gradient values below -40 to use as starting point of our measurement
        # starting_threshold_precise = min(gradient[:timeidx_start - 5])
        signal_start = int(next(idx for idx, value in enumerate(gradient) if value < starting_threshold))

        baseline = sensor_data[signal_start]

        return baseline, signal_start

    def plot_data(self, baseline: int, last_peak: int, peaks: int, signal_start: int, intersection: int, line,
                  filtered_red, gradient, plot_ir=False, plot_red_filter=True, plot_derivation=False):
        # Dynamic Plot Nummering
        num_subplots = 1 + sum([plot_ir, plot_red_filter, plot_derivation])
        plot_rows = 2
        plot_cols = num_subplots // plot_rows + num_subplots % plot_rows
        plot_index = 1
        # FIXME RealLy needed?
        params = {'mathtext.default': 'regular',
                  'axes.titlesize': 16,
                  'axes.labelsize': 14,
                  'font.family': 'sans-serif',
                  'font.sans-serif': 'Tahoma'
                  }  # mathematische Achsenbeschriftungen
        plt.rcParams.update(params)
        if plot_ir:
            plt.subplot(plot_rows, plot_cols, plot_index)
            plt.plot(self.time, self.sensor_ir, label='ir readings')
            plt.grid()
            plt.legend()
            plot_index += 1
        # Plot RED Readings
        ax_red = plt.subplot(plot_rows, plot_cols, plot_index)
        plt.plot(self.time, self.sensor_red, c='r', label='red readings')
        plt.plot(self.time, np.full((len(self.time)), baseline), '--')
        plt.grid()
        plt.legend()
        plot_index += 1
        # Plot Measurements Points
        plt.plot(self.time[signal_start], baseline, 'go', label='Measurement start')
        plt.plot(self.time[intersection], self.sensor_red[intersection], 'bo',
                 label='3s Kurvenabfall')  # FIXME Last Peak + 3s
        plt.plot(self.time[peaks], self.sensor_red[peaks], 'x', c='b')  # plot peaks
        plt.plot(self.time[last_peak], self.sensor_red[last_peak], 'x', c='g')  # plot last peaks

        plt.plot(line[0], line[1], '--')

        if plot_red_filter:
            ax_red_filter = plt.subplot(plot_rows, plot_cols, plot_index, sharex=ax_red)
            plt.plot(self.time, filtered_red, c='y', label='Red Filtered')
            plt.plot(self.time, np.full((len(self.time)), baseline), '--')
            plt.plot(self.time[peaks], filtered_red[peaks], 'x')  # plot peaks
            plt.plot(self.time[last_peak], filtered_red[last_peak], 'x', c='r')  # plot last peaks
            plt.grid()
            plt.legend()
            plot_index += 1

        if plot_derivation:
            plt.subplot(plot_rows, plot_cols, plot_index)
            plt.plot(self.time, gradient, c='k', label='Red Derivation')
            plot_index += 1

        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    # TODO Implement Argument Parser
    #  Argument welche Plots angezeigt werden sollen
    #  Argument welche Datei ausgelesen werden soll

    PLOT_IR = False
    PLOT_RED_FILTER = True
    PLOT_DERIVATION = False

    PATH = 'readings/good_readings/'
    FILE = 'reading_26-01-2022_16-17-03.csv'
    file_path = PATH + FILE

    ppg = PPGCalculator(file_path)
    ppg.calc_ppg()
