import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import butter, lfilter, freqz


# TODO Print FFT of singal

def butter_lowpass(cutoff_freq, fs, order=4):
    """
    Return the filter coefficients of the butterworth lowpass filter
    :param cutoff_freq: -3dB cutoff freq
    :param fs: samplerate of the digital filter
    :param order: order of the filter
    :return: filter coefficients as nominator b and deniminator a
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff_freq / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff_freq, fs, order=4):
    """
    Filters the given signal with a butterworth lowpass filter
    :param data:
    :param cutoff_freq:
    :param fs:
    :param order:
    :return:
    """
    __b, __a = butter_lowpass(cutoff_freq, fs, order=order)
    y = lfilter(__b, __a, data)
    return y


# Create a sinewave with high 1kHz fundamental
sample_rate = 44100  # [Hz ]
freq_fund = 100  # fundamental freq [Hz]
num_periods = 10  # number of fundamental sinewave periods
num_samples = sample_rate * num_periods  # total number of samples

x = np.linspace(0, num_periods / freq_fund, num_samples)

y_fund = np.sin(freq_fund * 2 * np.pi * x)
y_overlapped = y_fund + 0.2 * np.sin(5 * freq_fund * 2 * np.pi * x) + 0.1 * np.sin(10 * freq_fund * 2 * np.pi * x)

# Filter the high frequency content with a 4pole lowpass
cutoff = 150  # [Hz]
order = 6

# get the filter coefficients
b, a = butter_lowpass(cutoff, sample_rate, order)

# filter the signal
y_filtered = butter_lowpass_filter(y_overlapped, cutoff, sample_rate, order)

# Plot frequency respone of filter
plot_rows = 2
plot_cols = 2

W, h = freqz(b, a)  # get the filter response
plt.subplot(plot_rows, plot_cols, 1)
plt.plot(0.5 * sample_rate * W / np.pi, np.abs(h), 'b')  # plot frequency response
plt.plot(cutoff, 0.5 * np.sqrt(2), 'ko')  # create a -3dB dot at cutoff frequency
plt.axvline(cutoff, color='k')  # create a black vertical line right at the cutoff frequency
plt.xlim(0, 2 * cutoff)  # limit x axis to 400 Hz. Otherwise it would go up to nyquist
plt.title("Lowpass Filter Frequency Response", fontsize='small')
plt.xlabel('Frequency [Hz]', fontsize='small')
plt.grid()

plt.subplot(plot_rows, plot_cols, 2)
plt.plot(x, y_fund, 'b-', label='fundamental')
plt.title('Fundamental Sinewave {}Hz'.format(freq_fund), fontsize='small')
plt.xlabel('Time [sec]', fontsize='small')
plt.grid()
# plt.legend()

plt.subplot(plot_rows, plot_cols, 3)
plt.plot(x, y_overlapped, 'g-', linewidth=1, label='overlapped signal')
plt.xlabel('Time [sec]', fontsize='small')
plt.grid()
plt.legend()

plt.subplot(plot_rows, plot_cols, 4)
plt.plot(x, y_filtered, label='filtered signal')
plt.grid()
plt.legend()

plt.show()
