import serial
import time
from src.config_reader import ConfigReader

# mapping True = 1, False = 0, None = 255 for miner states
SET_ACTIONS = {None: 255, False: 0, True: 1}
GET_ACTIONS = {SET_ACTIONS[None]: None,
               SET_ACTIONS[False]: False,
               SET_ACTIONS[True]: True}
"""
This dict is used to translate variable names to their respective serial cmds.
In an ideal world this would not be necessary but as this project/app grew over
the course of two months some design flaws are to be expected (which does not
mean that they can not be fixed).
"""
CMD_DICT = {
    'info_fw_version': 'fw',
    'temp_target': 'targettemp',
    'temp_sensor_id': 'sensor',
    'temp_external': 'external',
    'filter_pressure_diff': 'pressure',
    'filter_status_ok': 'filter',
    'filter_threshold': 'threshold',
    'fans_min_rpm': 'minrpm',
    'fans_max_rpm': 'maxrpm',
    'fans_rpm': 'rpm',
    '_max_number_of_miners': 'maxminers',
    'pid_proportional': 'pidp',
    'pid_integral': 'pidi',
    'pid_derivative': 'pidd',
    'pid_bias': 'pidb',
    'op_gpu_ontime': 'ontime',
    'op_gpu_offtime': 'offtime',
    'op_asic_restime': 'restime',
    'commit_frequency': 'frequency'
}

class MinerIterator:
    """
    WARNING! Previously the MinerList was just realized as a simple list of
    bool & None values. However, after coupling the list to the mc
    (thus leading to the creation of MinerList), the container functionality
    had to be replicated. As far as I understand iterators it is currently not
    possible to replicate the iterator assignment functionality.
    (eg for miner in MinerList(120): miner = True)
    Therefore, you can only read values with the iterator, if you want to set
    them you have to access them by their respective indices.
    """
    def __init__(self, miners):
        self._miners = miners
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._miners):
            raise StopIteration
        val = GET_ACTIONS[self._miners[self._index]]
        self._index += 1
        return val

class MinerList:
    """
    This container acts like a simple list, but instead of variable values it is
    hooked into the serial interface to get up-to-date information and set
    values blazingly fast. Wow! Such speed! (to be honest, it is quite slow...)
    """
    def __init__(self, length):
        self._length = int(_read("?maxminers"))
    def __len__(self):
        return self._length
    def __getitem__(self, key):
        """
        Returns the current bool/None state of the miner.

        :returns: bool or None
        """
        state = int(_read("?miner {}".format(key)))
        return GET_ACTIONS[state]
    def __setitem__(self, key, value):
        _write("!miner {} {}".format(key, SET_ACTIONS[value]))
    def __iter__(self):
        return MinerIterator(self._miners).__iter__()
    def serialize(self):
        states = []
        for miner in range(self._length):
            state = int(_read("?miner {}".format(miner)))
            states.append(GET_ACTIONS[state])
        return states
    def get_all(self):
        resp = _read("?miners")
        miner_list = []
        for miner in resp.split(', '):
            miner_list.append(GET_ACTIONS[int(miner)])
        return miner_list

CFG_RDR = ConfigReader(path='config/config.ini')
SERIAL = serial.Serial(CFG_RDR.get_attr('serial_port'),
                       CFG_RDR.get_attr('baudrate'),
                       timeout=1)

def _read(cmd):
    """
    Read whole serial interface buffer.

    :returns: stripped str
    """
    _write(cmd)
    while not SERIAL.in_waiting:
        time.sleep(.1)
    return SERIAL.read(SERIAL.in_waiting).decode('utf-8').strip()

def _write(cmd, line_ending='\n'):
    """
    Write message to the serial interface as byte stream.

    :returns: number of bytes written
    """
    resp_len = SERIAL.write(bytes(cmd + line_ending, encoding='utf-8'))
    return resp_len

class Microcontroller:
    def __init__(self):
        self.info_fw_version = None
        self.temp_measurements = None
        self.temp_target = None
        self.temp_sensor_id = None
        self.temp_external = None
        self.filter_pressure_diff = None
        self.filter_status_ok = None
        self.filter_threshold = None
        self.fans_min_rpm = None
        self.fans_max_rpm = None
        self.fans_rpm = None
        self.active_mode = None
        # TODO correctly init this
        self._max_number_of_miners = 120
        self.miners = MinerList(120)

        self.pid_proportional = None
        self.pid_integral = None
        self.pid_derivative = None
        self.pid_bias = None
        self.op_gpu_ontime = None
        self.op_gpu_offtime = None
        self.op_asic_restime = None
        self.commit = None
        self.commit_frequency = None

    def __setattr__(self, name, value):
        if value is None or name.startswith("_"):
            return None
        if name == "active_mode":
            mode_id = None
            if value == "gpu":
                mode_id = 0
            elif value == "asic":
                mode_id = 1
            _write("!mode {}".format(mode_id))
        elif name == "miners":
            object.__setattr__(self, name, value)
        elif name == "commit":
            _read("!commit")
        else:
            _write("!{} {}".format(CMD_DICT[name], value))

    def __getattribute__(self, name):
        if name == "temp_measurements":
            # original format: 0:15, 1:22, 2:33
            measurements = _read("?temps")
            output = dict()
            for items in measurements.split(", "):
                temp = items.split(":")
                output[int(temp[0])] = temp[1]
            return output
        elif name == "active_mode":
            mode_id = int(_read("?mode"))
            modes = ["gpu", "asic"]
            return modes[mode_id]
        elif name == "miners":
            return object.__getattribute__(self, name)
        elif name == "info_fw_version":
            return _read("?{}".format(CMD_DICT[name]))
        elif name == "filter_status_ok":
            return bool(_read("?{}".format(CMD_DICT[name])))
        else:
            return int(_read("?{}".format(CMD_DICT[name])))
