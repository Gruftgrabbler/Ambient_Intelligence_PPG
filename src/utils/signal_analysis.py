from typing import Tuple

import numpy as np
from scipy.signal import butter, sosfreqz, sosfiltfilt, find_peaks

"""
    This file contains some utilty signal analysis functions.
"""

def filter_signal(
    signal: np.ndarray, sampling_rate: int = 20, order: int = 4, lowpass_cutoff: int = 3
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Lowpass filter the given signal with the given parameters using a Butterworth Lowpass Filter from scipy.
    Also returns the filter coeeficents in case the filters step response should be plotted.
    :param signal: signal which will be filtered
    :type signal: np.ndarray
    :param sampling_rate: sampling rate of the signal.
    :type sampling_rate: int
    :param order: order of the
    :type order: int
    :param lowpass_cutoff: cutoff frequency in hertz
    :type lowpass_cutoff: int
    :return: filtered signal, w, h
    :rtype: np.ndarray, np.ndarray, np.ndarray
    """
    nyq = sampling_rate / 2
    sos = butter(order, lowpass_cutoff / nyq, btype="low", analog=False, output="sos")
    w, h = sosfreqz(sos, worN=1500)  # Filter Frequency Response
    filtered_data = sosfiltfilt(sos, signal)
    return filtered_data, w, h


def calc_signal_baseline(signal: np.ndarray, threshold: int = -50) -> Tuple[float, int]:
    """
    Calculate the baseline of the given signal. The Baseline will be defined as the  first occurcence where the
    gradient of the signal excesses a certain threshold. This is an important parameter for later LRR calculation.
    Also returns the time stemp where this threshold exceeds.

    NOTE: This function will produce wrong results on heavily noisy data, so be clear that you insert a nice
    clean ppg meassurement.

    :param signal: signal which is going to be analysed
    :type signal: np.ndarray
    :param threshold: threshold of the gradient
    :type threshold: int
    :return: baseline, signal_start
    :rtype: float, int
    """

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

    :param signal: signal which is going to be analysed
    :param baseline: baseline of the signal
    :return: peaks, last_peak
    """
    peaks, _ = find_peaks(
        signal, height=baseline + 10, threshold=1, distance=1, prominence=500
    )
    last_peak = peaks[-1]  # save the last peak in a special variable
    peaks = peaks[:-1]  # remove last peak from the peaks list
    return peaks, int(last_peak)
