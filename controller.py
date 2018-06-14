import types
from mocking.mock_controller import Controller
from flask import Flask
from flask_restful import Resource, Api, abort, reqparse

APP = Flask(__name__)
API = Api(APP)

MOCK = Controller()

PARSER = reqparse.RequestParser()
PARSER.add_argument('target', type=int, help='target temperature')
PARSER.add_argument('sensor_id', type=int, help='id of main temperature measurement sensor')
PARSER.add_argument('external', type=int, help='external temperature (e.g. miner temperature)')

PARSER.add_argument('threshold', type=int, help='pressure difference threshold at which the filter is to be changed')

PARSER.add_argument('rel_min_rpm', type=int, help='minimum fan rpm')
PARSER.add_argument('rel_max_rpm', type=int, help='maximimum fan rpm')
PARSER.add_argument('abs_min_rpm', type=int, help='minimum fan rpm')
PARSER.add_argument('abs_max_rpm', type=int, help='maximimum fan rpm')

PARSER.add_argument('active_mode', type=int, help='operational mode. 0 = gpu, 1 = fpga, 2 = testing')
PARSER.add_argument('ontime', type=int, help='gpu mode - ontime')
PARSER.add_argument('offtime', type=int, help='gpu mode - offtime')
PARSER.add_argument('restime', type=int, help='fpga mode - restime')

PARSER.add_argument('proportional', type=int, help='PID P value')
PARSER.add_argument('integral', type=int, help='PID I value')
PARSER.add_argument('deriative', type=int, help='PID D value')
PARSER.add_argument('bias', type=int, help='PID bias value')

PARSER.add_argument('number_of_miners', type=int, help='number of miners')

class Info(Resource):
    def get(self):
        return {'firmware_version': MOCK.info_fw_version,
                'number_of_miners': MOCK.number_of_miners} # TODO add database connection
    def put(self):
        args = PARSER.parse_args()
        MOCK.number_of_miners = args['number_of_miners']
        return '', 200

class Temperature(Resource):
    def get(self):
        return {'measurements': MOCK.temp_measurements,
                'target': MOCK.temp_target,
                'sensor_id': MOCK.temp_sensor_id,
                'external': MOCK.temp_external}
    def put(self, target, sensor_id, external):
        args = PARSER.parse_args()
        MOCK.temp_target = args['target']
        MOCK.temp_sensor_id = args['sensor_id']
        MOCK.temp_external = args['external']
        return '', 200

class Filtration(Resource):
    def get(self):
        return {'pressure_diff': MOCK.filter_pressure_diff,
                'status_ok': MOCK.filter_status_ok,
                'threshold': MOCK.filter_threshold}
    def put(self):
        args = PARSER.parse_args()
        MOCK.filter_threshold = args['threshold']
        return '', 200

class Ventilation(Resource):
    def get(self, scale):
        if scale == 'abs':
            return {'min_rpm': MOCK.fans_abs_min_rpm,
                    'max_rpm': MOCK.fans_abs_max_rpm,
                    'rpm': MOCK.fans_abs_rpm}
        elif scale == 'rel':
            return {'min_rpm': MOCK.fans_rel_min_rpm,
                    'max_rpm': MOCK.fans_rel_max_rpm,
                    'rpm': MOCK.fans_rel_rpm}
        else:
            abort(400, message="Invalid request parameter")

    def put(self, mode):
        args = PARSER.parse_args()
        if mode == 'abs' or mode == 'rel':
            MOCK.fans_abs_min_rpm = args['min_rpm']
            MOCK.fans_abs_max_rpm = args['max_rpm']
            return '', 200
        else:
            abort(400, message="Invalid request parameter")

class Operation(Resource):
    def get(self):
        resp = {'active_mode': MOCK.active_mode}
        if MOCK.active_mode == 0 or MOCK.active_mode == 2: # GPU mode
            resp['ontime'] = MOCK.op_gpu_ontime
            resp['offtime'] = MOCK.op_gpu_ontime
        if MOCK.active_mode == 1 or MOCK.active_mode == 2: # FPGA mode
            resp['restime'] = MOCK.op_fpga_restime
        if MOCK.active_mode < 0 and MOCK.active_mode > 2:
            abort(400, message="Invalid request parameter")
        return resp

    def put(self):
        args = PARSER.parse_args()
        MOCK.active_mode = args['active_mode']
        if MOCK.active_mode == 0 or MOCK.active_mode == 2: # GPU mode
            MOCK.op_gpu_ontime = args['ontime']
            MOCK.op_gpu_ontime = args['offtime']
        if MOCK.active_mode == 1 or MOCK.active_mode == 2: # FPGA mode
            MOCK.op_fpga_restime == args['restime']
        return '', 200

class MinerController(Resource):
    def put(self, miner_id, action):
        if action == 'on': # TODO change action based on mode
            MOCK.miners[miner_id] = True
            return '', 200
        elif action == 'off':
            MOCK.miners[miner_id] = False
            return '', 200
        elif action == 'toggle':
            MOCK.miners[miner_id] = not MOCK.miners[id]

        if MOCK.active_mode < 0 and MOCK.active_mode > 2:
            abort(400, message="Invalid request parameter")

        return '', 200

    def get(self, miner_id):
        return {'running': MOCK.miners[miner_id]}

class PID(Resource):
    def get(self):
        return {'proportional': MOCK.pid_proportional,
                'integral': MOCK.pid_integral,
                'deriative': MOCK.pid_deriative,
                'bias': MOCK.pid_bias}
    def put(self):
        args = PARSER.parse_args()
        MOCK.pid_proportional = args['proportional']
        MOCK.pid_integral = args['integral']
        MOCK.pid_deriative = args['deriative']
        MOCK.pid_bias = args['bias']
        return '', 200

class Config(Resource):
    """
    This class seems a bit hacky but it is actually really useful for
    centralized views such as a /settings page which shows all configurable
    options and/or allows setting values with a single request.
    """
    def get(self):
        return {'fw_version': MOCK.info_fw_version,
                'measurements': MOCK.temp_measurements,
                'target': MOCK.temp_target,
                'sensor_id': MOCK.temp_sensor_id,
                'external': MOCK.temp_external,
                'pressure_diff': MOCK.filter_pressure_diff,
                'status_ok': MOCK.filter_status_ok,
                'threshold': MOCK.filter_threshold,
                'abs_min_rpm': MOCK.fans_abs_min_rpm,
                'abs_max_rpm': MOCK.fans_abs_max_rpm,
                'abs_rpm': MOCK.fans_abs_rpm,
                'rel_min_rpm': MOCK.fans_rel_min_rpm,
                'rel_max_rpm': MOCK.fans_rel_max_rpm,
                'rel_rpm': MOCK.fans_rel_rpm,
                'active_mode': MOCK.active_mode,
                'number_of_miners': MOCK.number_of_miners,
                'pid_proportional': MOCK.pid_proportional,
                'pid_integral': MOCK.pid_integral,
                'pid_deriative': MOCK.pid_deriative,
                'pid_bias': MOCK.pid_bias,
                'ontime': MOCK.op_gpu_ontime,
                'offtime': MOCK.op_gpu_offtime,
                'restime': MOCK.op_fpga_restime,
                'miners': MOCK.miners
        }

    def put(self):
        args = PARSER.parse_args()
        MOCK.temp_target = args['target']
        MOCK.temp_sensor_id = args['sensor_id']
        MOCK.temp_external = args['external']
        MOCK.filter_threshold = args['threshold']
        MOCK.fans_abs_min_rpm = args['abs_min_rpm']
        MOCK.fans_abs_max_rpm = args['abs_max_rpm']
        MOCK.active_mode = args['active_mode']
        MOCK.number_of_miners  = args['number_of_miners']
        MOCK.pid_proportional = args['proportional']
        MOCK.pid_integral = args['integral']
        MOCK.pid_deriative = args['deriative']
        MOCK.pid_bias = args['bias']
        #MOCK.op_gpu_ontime = args['ontime']
        #MOCK.op_gpu_offtime = args['offtime']
        #MOCK.op_fpga_restime = args['restime']
        return '', 200

API.add_resource(Info, '/info')
API.add_resource(Temperature, '/temp')
API.add_resource(Filtration, '/filter')
API.add_resource(Ventilation, '/fans/<string:scale>')
API.add_resource(Operation, '/mode')
API.add_resource(MinerController, '/miner/<int:miner_id>/<string:action>',
                 '/miner/<int:miner_id>')
API.add_resource(PID, '/pid')
API.add_resource(Config, '/cfg')

if __name__ == '__main__':
    APP.run(port=12345)