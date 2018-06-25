from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from mocking.mock_controller import Controller

MOCK = Controller()
APP = Flask(__name__)
APP.config['JWT_ALGORITHM'] = 'RS256'
with open('config/jwtRS256.key.pub', 'rb') as file:
    APP.config['JWT_PUBLIC_KEY'] = file.read()

JWT = JWTManager(APP)
API = Api(APP)
PARSER = reqparse.RequestParser()

class Info(Resource):
    @jwt_required
    def get(self):
        return {'firmware_version': MOCK.info_fw_version}

class Temperature(Resource):
    @jwt_required
    def get(self):
        MOCK.randomize_variables()
        return {'measurements': MOCK.temp_measurements,
                'target': MOCK.temp_target,
                'sensor_id': MOCK.temp_sensor_id,
                'external': MOCK.temp_external}
    def patch(self):
        args = PARSER.parse_args()
        MOCK.temp_target = args['target']
        MOCK.temp_sensor_id = args['sensor_id']
        MOCK.temp_external = args['external']
        return '', 200

class Filtration(Resource):
    @jwt_required
    def get(self):
        MOCK.randomize_variables()
        return {'pressure_diff': MOCK.filter_pressure_diff,
                'status_ok': MOCK.filter_status_ok,
                'threshold': MOCK.filter_threshold}
    def patch(self):
        args = PARSER.parse_args()
        MOCK.filter_threshold = args['threshold']
        return '', 200

class Ventilation(Resource):
    @jwt_required
    def get(self):
        MOCK.randomize_variables()
        return {'min_rpm': MOCK.fans_min_rpm,
                'max_rpm': MOCK.fans_max_rpm,
                'rpm': MOCK.fans_rpm}

    def patch(self):
        args = PARSER.parse_args()
        MOCK.fans_min_rpm = args['min_rpm']
        MOCK.fans_max_rpm = args['max_rpm']
        return '', 200

class Operation(Resource):
    @jwt_required
    def get(self):
        resp = {'active_mode': MOCK.active_mode}
        if MOCK.active_mode == 'gpu':
            resp['ontime'] = MOCK.op_gpu_ontime
            resp['offtime'] = MOCK.op_gpu_offtime
        elif MOCK.active_mode == 'asic':
            resp['restime'] = MOCK.op_asic_restime
        return resp

    def patch(self):
        args = PARSER.parse_args()
        MOCK.active_mode = args['active_mode']
        if MOCK.active_mode == 'gpu':
            MOCK.op_gpu_ontime = args['ontime']
            MOCK.op_gpu_offtime = args['offtime']
        if MOCK.active_mode == 'asic':
            MOCK.op_asic_restime = args['restime']
        return '', 200

class MinerController(Resource):
    @jwt_required
    def get(self):
        args = PARSER.parse_args()
        miner_id = int(args['id'])
        return {'running': MOCK.miners[miner_id]}

    def patch(self):
        args = PARSER.parse_args()
        action = args['action']
        miner_id = args['id']
        if action == 'on' or action == 'register':
            # new miners are turned on by default
            MOCK.miners[miner_id] = True
        elif action == 'off':
            MOCK.miners[miner_id] = False
        elif action == 'toggle':
            MOCK.miners[miner_id] = not MOCK.miners[miner_id]
        elif action == 'deregister':
            MOCK.miners[miner_id] = None
        elif action == 'reset':
            # TODO reset action
            pass
        else:
            return '', 400

        return '', 200

class PID(Resource):
    @jwt_required
    def get(self):
        return {'proportional': MOCK.pid_proportional,
                'integral': MOCK.pid_integral,
                'derivative': MOCK.pid_derivative,
                'bias': MOCK.pid_bias}
    def put(self):
        args = PARSER.parse_args()
        MOCK.pid_proportional = args['proportional']
        MOCK.pid_integral = args['integral']
        MOCK.pid_derivative = args['derivative']
        MOCK.pid_bias = args['bias']
        return '', 200

class Config(Resource):
    """
    This class seems a bit hacky but it is actually really useful for
    centralized views such as a /settings page which shows all configurable
    options and/or allows setting values with a single request.
    """
    @jwt_required
    def get(self):
        MOCK.randomize_variables()
        return {'fw_version': MOCK.info_fw_version,
                'measurements': MOCK.temp_measurements,
                'target': MOCK.temp_target,
                'sensor_id': MOCK.temp_sensor_id,
                'external': MOCK.temp_external,
                'pressure_diff': MOCK.filter_pressure_diff,
                'status_ok': MOCK.filter_status_ok,
                'threshold': MOCK.filter_threshold,
                'min_rpm': MOCK.fans_min_rpm,
                'max_rpm': MOCK.fans_max_rpm,
                'rpm': MOCK.fans_rpm,
                'active_mode': MOCK.active_mode,
                'proportional': MOCK.pid_proportional,
                'integral': MOCK.pid_integral,
                'derivative': MOCK.pid_derivative,
                'bias': MOCK.pid_bias,
                'ontime': MOCK.op_gpu_ontime,
                'offtime': MOCK.op_gpu_offtime,
                'restime': MOCK.op_asic_restime,
                'miners': MOCK.miners}

    def patch(self):
        args = PARSER.parse_args()
        MOCK.temp_target = args['target']
        MOCK.temp_sensor_id = args['sensor_id']
        MOCK.temp_external = args['external']
        MOCK.filter_threshold = args['threshold']
        MOCK.fans_min_rpm = args['min_rpm']
        MOCK.fans_max_rpm = args['max_rpm']
        MOCK.active_mode = args['active_mode']
        MOCK.pid_proportional = args['proportional']
        MOCK.pid_integral = args['integral']
        MOCK.pid_derivative = args['derivative']
        MOCK.pid_bias = args['bias']
        MOCK.op_gpu_ontime = args['ontime']
        MOCK.op_gpu_offtime = args['offtime']
        MOCK.op_asic_restime = args['restime']
        return '', 200

def prepare_app():
    PARSER.add_argument('target', type=int, help='target temperature')
    PARSER.add_argument('sensor_id', type=int, help='id of main \
                        temperature measurement sensor')
    PARSER.add_argument('external', type=int, help='external temperature \
                        (e.g. miner temperature)')

    PARSER.add_argument('threshold', type=int, help='pressure difference\
                        threshold at which the filter is to be changed')

    PARSER.add_argument('min_rpm', type=int, help='minimum fan rpm')
    PARSER.add_argument('max_rpm', type=int, help='maximimum fan rpm')

    PARSER.add_argument('active_mode',
                        help="operational mode = 'gpu' or 'asic'")
    PARSER.add_argument('ontime', type=int, help='gpu mode - ontime')
    PARSER.add_argument('offtime', type=int, help='gpu mode - offtime')
    PARSER.add_argument('restime', type=int, help='asic mode - restime')

    PARSER.add_argument('proportional', type=int, help='PID P value')
    PARSER.add_argument('integral', type=int, help='PID I value')
    PARSER.add_argument('derivative', type=int, help='PID D value')
    PARSER.add_argument('bias', type=int, help='PID bias value')

    PARSER.add_argument('action', help="miner action like 'toggle'")
    PARSER.add_argument('id', type=int, help='miner id')

    API.add_resource(Info, '/info', methods=['GET'])
    API.add_resource(Temperature, '/temp', methods=['GET', 'PATCH'])
    API.add_resource(Filtration, '/filter', methods=['GET', 'PATCH'])
    API.add_resource(Ventilation, '/fans', methods=['GET', 'PATCH'])
    API.add_resource(Operation, '/mode', methods=['GET', 'PATCH'])
    API.add_resource(MinerController, '/miner', methods=['GET', 'PATCH'])
    API.add_resource(PID, '/pid', methods=['GET', 'PUT'])
    API.add_resource(Config, '/cfg', methods=['GET', 'PATCH'])

    return APP

def create_app(host='127.0.0.1', port='12345'):
    app = prepare_app()
    app.run(host=host, port=port)

if __name__ == '__main__':
    create_app()
