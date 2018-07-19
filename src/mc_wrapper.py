import serial
import time

SET_ACTIONS = {None: -1, False: 0, True: 1}
GET_ACTIONS = {SET_ACTIONS[None]: None,
               SET_ACTIONS[False]: False,
               SET_ACTIONS[True]: True}
CMD_DICT = {
    'info_fw_version': 'fw',
    'temp_target': 'targettemp',
    'temp_sensor_id': 'sensor',
    'temp_external': 'external',
    'filter_pressure_diff': 'pressure',
    'filter_status_ok': 'filter', # TODO this could be a potential error source as it was a bool once
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
    'op_asic_restime': 'restime'
}

class MinerIterator:
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
    def __init__(self, length):
        self._length = int(_read("?maxminers"))
    def __len__(self):
        return self._length
    def __getitem__(self, key):
        state = int(_read("?miner {}".format(key)))
        return GET_ACTIONS[state]
    def __setitem__(self, key, value):
        print("!miner {} {}".format(key, SET_ACTIONS[value]))
        _write("!miner {} {}".format(key, SET_ACTIONS[value]))
    def __iter__(self):
        #TODO fix iterator
        return MinerIterator(self._miners).__iter__()
    def serialize(self):
        states = []
        for miner in range(self._length):
            state = int(_read("?miner {}".format(miner)))
            states.append(GET_ACTIONS[state])
        return states

# TODO change parameters based on config file
SERIAL = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

def _read(cmd):
    _write(cmd)
    while not SERIAL.in_waiting:
        time.sleep(.1)
    return SERIAL.read(SERIAL.in_waiting).decode('utf-8').strip()

def _write(cmd):
    resp_len = SERIAL.write(bytes(cmd + '\n', encoding='utf-8'))
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
            # TODO add direct access to miners
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
            return bool(_read("?{}".format(name)))
        else:
            return int(_read("?{}".format(CMD_DICT[name])))
