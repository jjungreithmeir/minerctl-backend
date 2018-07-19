"""
Small collection of classes that map JSON resources. The name of each class
method corresponds to the HTTP request method name. To define the names of the
endpoints one simply has to add the resource in the `prepare_app` function
"""
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from src.mc_wrapper import Microcontroller
from src.config_reader import ConfigReader

MC = Microcontroller()
APP = Flask(__name__)
APP.config['JWT_ALGORITHM'] = 'RS256'
CFG_RDR = ConfigReader(path='config/config.ini')
with open(CFG_RDR.get_attr('public_key_file_location'), 'rb') as file:
    APP.config['JWT_PUBLIC_KEY'] = file.read()

JWT = JWTManager(APP)
API = Api(APP)
PARSER = reqparse.RequestParser()

class Info(Resource):
    @jwt_required
    def get(self):
        return {'firmware_version': MC.info_fw_version}

class Temperature(Resource):
    @jwt_required
    def get(self):
        return {'measurements': MC.temp_measurements,
                'target': MC.temp_target,
                'sensor_id': MC.temp_sensor_id,
                'external': MC.temp_external}
    def patch(self):
        args = PARSER.parse_args()
        MC.temp_target = args['target']
        MC.temp_sensor_id = args['sensor_id']
        MC.temp_external = args['external']
        return '', 200

class Filtration(Resource):
    @jwt_required
    def get(self):

        return {'pressure_diff': MC.filter_pressure_diff,
                'status_ok': MC.filter_status_ok,
                'threshold': MC.filter_threshold}
    def patch(self):
        args = PARSER.parse_args()
        MC.filter_threshold = args['threshold']
        return '', 200

class Ventilation(Resource):
    @jwt_required
    def get(self):

        return {'min_rpm': MC.fans_min_rpm,
                'max_rpm': MC.fans_max_rpm,
                'rpm': MC.fans_rpm}

    def patch(self):
        args = PARSER.parse_args()
        MC.fans_min_rpm = args['min_rpm']
        MC.fans_max_rpm = args['max_rpm']
        return '', 200

class Operation(Resource):
    @jwt_required
    def get(self):
        resp = {'active_mode': MC.active_mode}
        if MC.active_mode == 'gpu':
            resp['ontime'] = MC.op_gpu_ontime
            resp['offtime'] = MC.op_gpu_offtime
        elif MC.active_mode == 'asic':
            resp['restime'] = MC.op_asic_restime
        return resp

    def patch(self):
        args = PARSER.parse_args()
        MC.active_mode = args['active_mode']
        if MC.active_mode == 'gpu':
            MC.op_gpu_ontime = args['ontime']
            MC.op_gpu_offtime = args['offtime']
        if MC.active_mode == 'asic':
            MC.op_asic_restime = args['restime']
        return '', 200

class MinerController(Resource):
    @jwt_required
    def get(self):
        args = PARSER.parse_args()
        miner_id = int(args['id'])
        return {'running': MC.miners[miner_id]}

    def patch(self):
        args = PARSER.parse_args()
        action = args['action']
        miner_id = args['id']
        if action == 'on' or action == 'register':
            # new miners are turned on by default
            MC.miners[miner_id] = True
        elif action == 'off':
            MC.miners[miner_id] = False
        elif action == 'toggle':
            MC.miners[miner_id] = not MC.miners[miner_id]
        elif action == 'deregister':
            MC.miners[miner_id] = None
        elif action == 'reset':
            # TODO reset action
            pass
        else:
            return '', 400

        return '', 200

class PID(Resource):
    @jwt_required
    def get(self):
        return {'proportional': MC.pid_proportional,
                'integral': MC.pid_integral,
                'derivative': MC.pid_derivative,
                'bias': MC.pid_bias}
    def put(self):
        args = PARSER.parse_args()
        MC.pid_proportional = args['proportional']
        MC.pid_integral = args['integral']
        MC.pid_derivative = args['derivative']
        MC.pid_bias = args['bias']
        return '', 200

class Config(Resource):
    """
    This class seems a bit hacky but it is actually really useful for
    centralized views such as a /settings page which shows all configurable
    options and/or allows setting values with a single request.
    """
    @jwt_required
    def get(self):

        return {'fw_version': MC.info_fw_version,
                'measurements': MC.temp_measurements,
                'target': MC.temp_target,
                'sensor_id': MC.temp_sensor_id,
                'external': MC.temp_external,
                'pressure_diff': MC.filter_pressure_diff,
                'status_ok': MC.filter_status_ok,
                'threshold': MC.filter_threshold,
                'min_rpm': MC.fans_min_rpm,
                'max_rpm': MC.fans_max_rpm,
                'rpm': MC.fans_rpm,
                'active_mode': MC.active_mode,
                'proportional': MC.pid_proportional,
                'integral': MC.pid_integral,
                'derivative': MC.pid_derivative,
                'bias': MC.pid_bias,
                'ontime': MC.op_gpu_ontime,
                'offtime': MC.op_gpu_offtime,
                'restime': MC.op_asic_restime,
                'miners': MC.miners.get_all()}

    def patch(self):
        args = PARSER.parse_args()
        MC.temp_target = args['target']
        MC.temp_sensor_id = args['sensor_id']
        MC.temp_external = args['external']
        MC.filter_threshold = args['threshold']
        MC.fans_min_rpm = args['min_rpm']
        MC.fans_max_rpm = args['max_rpm']
        MC.active_mode = args['active_mode']
        MC.pid_proportional = args['proportional']
        MC.pid_integral = args['integral']
        MC.pid_derivative = args['derivative']
        MC.pid_bias = args['bias']
        MC.op_gpu_ontime = args['ontime']
        MC.op_gpu_offtime = args['offtime']
        MC.op_asic_restime = args['restime']
        return '', 200

def prepare_app():
    """
    Adding parser arguments and setting up resources.
    """
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
    """
    Currently this flask API is only running single threaded as parallel access to the Microcontroller class breaks the communication with the serial interface. In future version an additonal microservice, such as a RPC service which handles the requests to the serial interface would probably be ideal, as this workaround leads to severe performance decreases.
    """
    app = prepare_app()
    app.run(host=host, port=port, threaded=False)

if __name__ == '__main__':
    create_app()
