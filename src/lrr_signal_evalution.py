import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapz
from tabulate import tabulate

from src.utils.data_utils import Data, read_datafile
from src.utils.lrr_analysis import (
    calc_full_refill_time,
    calc_half_refill_time,
    calc_initial_refill_time,
)

from src.utils.signal_analysis import (
    calc_signal_peaks,
    filter_signal,
    calc_signal_baseline,
)


class LRRCalculator:

    def __init__(self, sensor_data: Data):
        """
        Initialise the LRRCalculator instance on the given Data
        :param sensor_data: sensor data which is going to be analysed
        :type sensor_data: Data
        """
        self.data = sensor_data
        self.data_dict = None

    def calc_lrr_params(self) -> None:
        """
        This method calculates all LRR related parameters using the utiliy methods from lrr_analysis.py
         and signal_analysis.py.

        initial-regill-time T_i(s)
        half-refill-time T_50(s)
        venous filling time T_0(s)
        Venous pump capacity V_0 (%)
        venous pump function F_0(%s)


        :return: -
        :rtype: None
        """
        baseline, signal_start = calc_signal_baseline(self.data.red)
        # self.data.time = self.data.time - baseline.signal_start

        signal_filtered, _, _ = filter_signal(self.data.red)
        peaks, last_peak = calc_signal_peaks(signal_filtered, baseline)
        line, initial_refill_time, p3_idx, p3_time = calc_initial_refill_time(
            self.data.red, self.data.time, last_peak, baseline
        )
        half_refill_time, half_refill_idx, half_refill_amp = calc_half_refill_time(
            self.data.red, self.data.time, baseline, last_peak
        )
        (
            full_refill_time,
            time_end_intersection,
            amplitude_end_intersection,
            time_idx_end_intersection,
        ) = calc_full_refill_time(self.data.red, self.data.time, baseline, last_peak)

        venous_pump_capacity = (self.data.red[last_peak] - baseline) / baseline * 100

        x_np = np.array(self.data.time[last_peak:time_idx_end_intersection])
        y_np = (
                (np.array(self.data.red[last_peak:time_idx_end_intersection]) - baseline)
                / baseline
                * 100
        )
        venous_pump_function = trapz(y_np, x_np)

        # Store all calculated data in a dictionary structure.
        self.data_dict = {
            "baseline": baseline,
            "signal_start": signal_start,
            "signal_start_time": self.data.time[signal_start],
            "last_peak_index": last_peak,
            "last_peak_time": self.data.time[last_peak],
            "last_peak_amp": signal_filtered[last_peak],
            "peaks_time_indizes": peaks,
            "p3_index": p3_idx,
            "p3_time": p3_time,
            "p3_amp": self.data.red[p3_idx],
            "line_approx": line,
            "initial_refill_time": initial_refill_time,
            "signal_end_time": time_end_intersection,
            "signal_end_amp": amplitude_end_intersection,
            "half_refill_index": half_refill_idx,
            "half_refill_time": half_refill_time,
            "half_refill_amp": half_refill_amp,
            "full_refill_time": full_refill_time,
            "full_refill_amp": amplitude_end_intersection,
            "venous_pump_capacity": venous_pump_capacity,
            "venous_pump_function": venous_pump_function,
            "signal_filtered": signal_filtered,
        }

    def print_lrr_params(self):
        """
        Prints the calculated data on the serial console in a nice table using tabulate.
        :return: -
        :rtype: None
        """
        print(
            tabulate(
                [
                    ["Algorithm specific parameters"],
                    ["Baseline", self.data_dict["baseline"]],
                    # ['Signal Starting idx', self.data_dict['signal_start']],
                    ["Signal Starting Time", self.data_dict["signal_start_time"]],
                    ["Signal Ending Time", self.data_dict["signal_end_time"]],
                    ["Signal Ending Amplitude", self.data_dict["signal_end_amp"]],
                    ["P3 Index", self.data_dict["p3_index"]],
                    ["P3 Time", self.data_dict["p3_time"]],
                    ["P3 Amplitude", self.data_dict["p3_amp"]],
                    ["Half-Refill Idx", self.data_dict["half_refill_index"]],
                    ["Half-Refill Amplitude", self.data_dict["half_refill_amp"]],
                    [
                        "",
                    ],
                    ["Medical Parameters"],
                    [
                        "Initial-Refill Time T_i(s)",
                        self.data_dict["initial_refill_time"],
                    ],
                    ["Half-Refill Time T_50(s)", self.data_dict["half_refill_time"]],
                    ["Venous Filling Time T_0(s)", self.data_dict["full_refill_time"]],
                    [
                        "Venous pump capacity V_0 (%)",
                        self.data_dict["venous_pump_capacity"],
                    ],
                    [
                        "Venous pump function F_0 (%s)",
                        self.data_dict["venous_pump_function"],
                    ],
                ],
                headers=["Parameter", "Value"],
                tablefmt="grid",
                floatfmt=".3f",
            )
        )

    def plot_lrr_graph(
            self, plot_ir=False, plot_red_filter=False, plot_derivation=False):
        """
        Plots the signal, the calculated points and the line approximation on a matplotlib window.
        You can enable additional plots by setting the coresponding variable to True.

        E.g. By plot_lrr_graph(plot_red_filter=True) will also plot the filterd red signal data in a seperate window
        :param plot_ir: decides if ir data should be plotted or not
        :type plot_ir: bool
        :param plot_red_filter: decides if red filter data should be plotted or not
        :type plot_red_filter: bool
        :param plot_derivation: decides if the signal derivation should be plotted or not
        :type plot_derivation: bool
        :return:. -
        :rtype: None
        """
        num_subplots = 1 + sum([plot_ir, plot_red_filter, plot_derivation])
        plot_rows = 2
        plot_cols = num_subplots // plot_rows + num_subplots % plot_rows
        plot_index = 1

        if plot_ir:
            plt.subplot(plot_rows, plot_cols, plot_index)
            plt.plot(self.data.time, self.data.ir, label="ir readings")
            plt.grid()
            plt.legend()
            plot_index += 1

        # Plot RED Readings
        _ = plt.subplot(plot_rows, plot_cols, plot_index)  # ax_red
        plt.plot(self.data.time, self.data.red, c="r", label="red readings")
        plt.plot(
            self.data.time,
            np.full((len(self.data.time)), self.data_dict["baseline"]),
            "--",
        )
        plt.grid()
        plt.legend()

        # Plot Measurements Points
        plt.plot(
            self.data_dict["signal_start_time"],
            self.data_dict["baseline"],
            "go",
            label="Measurement start",
        )
        plt.plot(
            self.data_dict["p3_time"],
            self.data_dict["p3_amp"],
            "bo",
            label="3s Kurvenabfall",
        )  # FIXME Last Peak + 3s
        plt.plot(
            self.data_dict["last_peak_time"],
            self.data_dict["last_peak_amp"],
            "x",
            c="b",
        )  # plot peaks
        # TODO Plot all other peaks
        plt.plot(
            self.data_dict["line_approx"][0], self.data_dict["line_approx"][1], "--"
        )

        if plot_red_filter:
            plot_index += 1
            # ax_red_filter = plt.subplot(plot_rows, plot_cols, plot_index, sharex=ax_red)
            plt.plot(
                self.data.time,
                self.data_dict["signal_filtered"],
                c="y",
                label="Red Filtered",
            )
            plt.plot(
                self.data.time,
                np.full((len(self.data.time)), self.data_dict["baseline"]),
                "--",
            )
            plt.plot(
                self.data.time[self.data_dict["peaks_time_indizes"]],
                self.data_dict["signal_filtered"][self.data_dict["peaks_time_indizes"]],
                "x",
            )  # plot peaks
            plt.plot(
                self.data.time[self.data_dict["last_peak_index"]],
                self.data_dict["signal_filtered"][self.data_dict["last_peak_index"]],
                "x",
                c="r",
            )  # plot last peaks
            plt.grid()
            plt.legend()
            plot_index += 1

        if plot_derivation:
            gradient = np.gradient(self.data.red, axis=0)
            plt.subplot(plot_rows, plot_cols, plot_index)
            plt.plot(self.data.time, gradient, c="k", label="Red Derivation")
            plot_index += 1

        plt.tight_layout()
        plt.show()

    def plot_ppg_raw(self):
        """
        Just plot the recorded data without any calculation results attached.
        """
        plt.plot(self.data.time, self.data.red, c="r", label="red readings")
        plt.tight_layout()
        plt.grid()
        plt.show()


def main():
    file = "documentation/measurement_data/good_readings/data3.csv"
    data = read_datafile(file)
    ppg = LRRCalculator(data)
    ppg.calc_lrr_params()
    ppg.print_lrr_params()
    ppg.plot_lrr_graph(plot_red_filter=True)


if __name__ == "__main__":
    main()
