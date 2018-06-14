import random

class Controller:
    def __init__(self):
        self.info_fw_version = '0.0.1'

        self.temp_measurements = {0: 45, 1: 42, 2: 35}
        self.temp_target = 45
        self.temp_sensor_id = 3
        self.temp_external = 39

        self.filter_pressure_diff = 1523
        self.filter_status_ok = False
        self.filter_threshold = 1423

        self.fans_abs_min_rpm = 2000
        self.fans_abs_max_rpm = 7000
        self.fans_abs_rpm = 5000
        self.fans_rel_min_rpm = 5
        self.fans_rel_max_rpm = 80
        self.fans_rel_rpm = 50

        self.active_mode = 0

        self.number_of_miners = 120
        self.miners = []
        for miner in range(self.number_of_miners):
            self.miners.append(random.random() > 0.1)

        self.pid_proportional = 1
        self.pid_integral = 20
        self.pid_deriative = 5
        self.pid_bias = 12

        self.op_gpu_ontime = 100
        self.op_gpu_offtime = 200

        self.op_fpga_restime = 1200
