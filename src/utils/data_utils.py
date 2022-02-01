import numpy as np


class Data:
    def __init__(self, sensor_red: np.ndarray, sensor_ir: np.ndarray, time: np.ndarray):
        self.red = sensor_red
        self.ir = sensor_ir
        self.time = time - time[0]


def read_datafile(file_name: str) -> Data:
    data_read = np.loadtxt(file_name, delimiter=",", skiprows=1)
    _data = Data(
        sensor_red=data_read[:, 1],
        sensor_ir=data_read[:, 2],
        time=data_read[:, 0] / 1000,
    )
    return _data
