import random

class Controller:
    """
    This class acts as a dumb wrapper for currently non-existing
    microcontroller.
    TODO Currently this class is most likely broken and needs to be fixed to
    act as a mock for mc_wrapper.
    """

    def __init__(self):
        self.info_fw_version = '0.0.1'

        self.temp_measurements = {0: random.randint(40, 45),
                                  1: random.randint(38, 47),
                                  2: random.randint(42, 55)}
        self.temp_target = 45
        self.temp_sensor_id = 2
        self.temp_external = 32

        self.filter_pressure_diff = random.randint(1425, 1450)
        self.filter_status_ok = False
        self.filter_threshold = 1423

        self.fans_min_rpm = 5
        self.fans_max_rpm = 80
        self.fans_rpm = random.randint(50, 65)

        self.active_mode = 'gpu'

        # internal max
        self._max_number_of_miners = 120
        self.miners = []
        for miner in range(self._max_number_of_miners):
            self.miners.append(random.random() > 0.1)

        # simulate missing rigs
        self.miners[99] = None
        self.miners[12] = None
        self.miners[30] = None
        self.miners[44] = None

        self.pid_proportional = 1
        self.pid_integral = 20
        self.pid_derivative = 5
        self.pid_bias = 12

        self.op_gpu_ontime = 100
        self.op_gpu_offtime = 200

        self.op_asic_restime = 1200

    def randomize_variables(self):
        """
        Mocking changes in variables.
        """
        for i in range(120):
            if i > self._max_number_of_miners:
                self.miners.append(None)

        self.temp_measurements = {0: random.randint(40, 45),
                                  1: random.randint(38, 47),
                                  2: random.randint(42, 55)}
        self.filter_pressure_diff = random.randint(1425, 1450)
        self.fans_rpm = random.randint(50, 65)
