from typing import Tuple

import numpy as np
from scipy.signal import butter, sosfreqz, sosfiltfilt, find_peaks


def filter_signal(
    signal: np.ndarray, sampling_rate: int = 20, order: int = 4, lowpass_cutoff: int = 3
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    nyq = sampling_rate / 2
    sos = butter(order, lowpass_cutoff / nyq, btype="low", analog=False, output="sos")
    w, h = sosfreqz(sos, worN=1500)  # Filter Frequency Response
    filtered_data = sosfiltfilt(sos, signal)
    return filtered_data, w, h


def calc_signal_baseline(signal: np.ndarray, threshold: int = -50) -> Tuple[float, int]:
    gradient = np.gradient(signal, axis=0)
    signal_start = int(
        next(idx for idx, value in enumerate(gradient) if value < threshold)
    )
    baseline = signal[signal_start]
    return baseline, signal_start


def calc_signal_peaks(signal: np.ndarray, baseline: float) -> Tuple[np.ndarray, int]:
    """
    Calculate the time stems of all peaks of the given signal above the baseline.
    Return: Last Peak as int, all other peaks as np.list

    :param signal:
    :param baseline:
    :return:
    """
    peaks, _ = find_peaks(
        signal, height=baseline + 10, threshold=1, distance=1, prominence=500
    )
    last_peak = peaks[-1]  # save the last peak in a special variable
    peaks = peaks[:-1]  # remove last peak from the peaks list
    return peaks, int(last_peak)
