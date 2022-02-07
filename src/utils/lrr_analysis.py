from typing import Tuple, List

import numpy as np


def calc_initial_refill_time(
    signal: np.ndarray, time: np.ndarray, last_peak: int, baseline: int
) -> Tuple[List[np.ndarray], float, int, float]:
    """
    Calculate the initial refill time from the given PPG signal. It represents the time from the last recorded peak
    in the signal down to baseline crossing a point on the curve which is 3 seconds after the last peak.

    :param signal: red or infrared data signal, depending on which data you want to use
    :type signal: np.ndarray
    :param time: time stemp data which belongs to the given signal
    :type time: np.ndarray
    :param last_peak: time_index of the last peak in the given signal
    :type last_peak: int
    :param baseline: baseline of the given signal
    :type baseline: int
    :return:    line - approximation from last_peak down to baseline,
                initial_filling_time - Calculated initial refill time in seconds,
                p3_idx - signal index of the signal point 3 seconds after the last peak
                p3_time - time stemp of the signal point 3 seconds after the last peak
    :rtype: List[np.ndarray], float, int, float
    """
    # Find the point on the ppg curve which is 3 sec ahead of the last maximum
    # (required for Initial-Refill-Time)
    p3_idx = (
        next(
            idx
            for idx, value in enumerate(time[last_peak:])
            if value > time[last_peak] + 3
        )
        + last_peak
    )
    p3_time = time[p3_idx]

    # calculate initial-refill time
    # approximate line through last peak and p3
    delta_y = signal[p3_idx] - signal[last_peak]
    delta_x = time[p3_idx] - time[last_peak]
    line_amplitude = delta_y / delta_x * (time - time[last_peak]) + signal[last_peak]

    # remove all entries before last_peak
    line_amplitude = line_amplitude[int(last_peak) :]

    # find first point of intersection between the approximated line and baseline
    baseline_line_intersection_idx = next(
        idx for idx, value in enumerate(line_amplitude) if value - baseline < 0
    )  # schnittpunkt zwischen line und baseline
    # remove all entries after intersection
    line_amplitude = line_amplitude[:baseline_line_intersection_idx]
    line_time = time[int(last_peak) : last_peak + baseline_line_intersection_idx]
    line = [line_time, line_amplitude]

    # calculate initial-refill time
    initial_filling_time = line_time[-1] - line_time[0]
    return line, initial_filling_time, p3_idx, p3_time


def calc_half_refill_time(
    signal: np.ndarray, time: np.ndarray, baseline: int, last_peak: int
) -> Tuple[float, int, float]:
    """
    Calculate the half refill time from the given PPG signal. It represents the time where the amplitude of the
    decaying signal crosses a point where its amplitude is only the half of the last peaks amplitude.

    :param signal: signal which is going to be analysed
    :type signal: np.ndarray
    :param time: time stemp data of the given signal
    :type time: np.ndarray
    :param baseline: baseline of the given signal
    :type baseline: int
    :param last_peak: last peak of the givens signal ppg meassurement (time index)
    :type last_peak: int
    :return:    half-refill-time - calculated medcial time information
                half-refill-idx - index of the 50% crossing
                half-refill-amp - amplitude of the 50% crossing
    :rtype:
    """

    threshold_half_refill = baseline + (signal[last_peak] - baseline) / 2
    half_refill_idx = (
        next(
            idx
            for idx, value in enumerate(signal[last_peak:])
            if value < threshold_half_refill
        )
        + last_peak
    )

    time_half_refill = time[half_refill_idx]
    half_refill_amp = signal[half_refill_idx]
    half_refill_time = time_half_refill - time[last_peak]
    return half_refill_time, half_refill_idx, half_refill_amp


def calc_full_refill_time(
    signal: np.ndarray, time: np.ndarray, baseline: int, last_peak: int
) -> Tuple[float, float, float, int]:
    """
    Find the intersection between the signal and the baseline after decline of the curve
    Return full_refill_time: Time between the last peak and the intersection
    Return time_end_intersection: Time of the intersection between signal and baseline
    Return amplitude_end_intersection: Amplitude of the signal at intersection point

    :param signal: signal which is going to be analysed
    :param time: time stemp data of the given signal
    :param baseline: baseline of the given signal
    :param last_peak: last peak of the given signal
    :return:
    """

    timeidx_end_intersection = (
        next(idx for idx, value in enumerate(signal[last_peak:]) if value < baseline)
        + last_peak
    )
    time_end_intersection = time[timeidx_end_intersection]
    amplitude_end_intersection = signal[timeidx_end_intersection]
    full_refill_time = time_end_intersection - time[last_peak]
    return (
        full_refill_time,
        time_end_intersection,
        amplitude_end_intersection,
        timeidx_end_intersection,
    )
