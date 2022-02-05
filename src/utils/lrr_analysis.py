from typing import Tuple

import numpy as np


def calc_initial_refill_time(
    signal: np.ndarray, time: np.ndarray, last_peak: int, baseline: int
) -> Tuple[list[np.ndarray], float, int, float]:
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

    :param signal:
    :param time:
    :param baseline:
    :param last_peak:
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
