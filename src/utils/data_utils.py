import numpy as np


class Data:
    """
    Data Utility Class, which is storing the measured PPG Data readed from the given .csv file
    """
    def __init__(self, sensor_red: np.ndarray, sensor_ir: np.ndarray, time: np.ndarray):
        """
        :param sensor_red: Red Sensor PPG Data
        :type sensor_red: np.ndarray
        :param sensor_ir: Infrared Sensor PPG Data
        :type sensor_ir: np.ndarray
        :param time: Recorded time stemp (ms) of the Sesnor PPG Data
        :type time: np.ndarray
        """
        self.red = sensor_red
        self.ir = sensor_ir
        self.time = time - time[0]


def read_datafile(file_name: str) -> Data:
    """
    Read the given .csv file containing the previously recorded PPG Data.

    DESCRIPTION:
        The .csv file must be in the formatted like: red,ir,time

    :param file_name: file_name of given .csv file
    :type file_name: string
    :return: csv data as Data
    :rtype: Instance of utility class Data
    """
    data_read = np.loadtxt(file_name, delimiter=",", skiprows=1)
    _data = Data(
        sensor_red=data_read[:, 1],
        sensor_ir=data_read[:, 2],
        time=data_read[:, 0] / 1000,
    )
    return _data
