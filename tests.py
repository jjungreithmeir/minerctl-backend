import random
import sys
import requests
import pytest
# for some strange unexplainable reason I need to add the current folder to the
# sys.path
sys.path.append('.')
from testing.assertions import assert_valid_schema, assert_same_dict_content

CONNECTION = 'http://localhost:12345'

def test_assert_same_dict_content_true():
    a = random.randint(0, 100)
    b = random.randint(0, 100)
    c = random.randint(0, 100)

    expected = {'a': a, 'b': b, 'c': c}
    given = {'a': a, 'b': b, 'c': c, 'd': 4}
    assert assert_same_dict_content(expected, given)

def test_assert_same_dict_content_false():
    a = random.randint(0, 100)
    b = random.randint(0, 100)
    c = random.randint(0, 100)

    expected = {'a': a, 'b': b, 'c': c}
    given = {'a': a, 'b': b, 'c': -1, 'd': 4}
    assert assert_same_dict_content(expected, given) == False

def test_get_info(session):
    resp = session.get(CONNECTION + '/info').json()
    assert_valid_schema(resp, 'info.json')

def test_get_temperature(session):
    resp = session.get(CONNECTION + '/temp').json()
    assert_valid_schema(resp, 'temp.json')

def test_patch_temperature(session):
    rand_target = random.randint(20, 30)
    rand_sensor_id = random.randint(0, 4)
    rand_external = random.randint(20, 50)
    data = {'target': rand_target, 'sensor_id': rand_sensor_id,
            'external': rand_external}
    session.patch(CONNECTION + '/temp', data=data)
    resp = session.get(CONNECTION + '/temp').json()
    assert assert_same_dict_content(data, resp)

def test_get_filtration(session):
    resp = session.get(CONNECTION + '/filter').json()
    assert_valid_schema(resp, 'filter.json')

def test_patch_filtration(session):
    rand_threshold = random.randint(1000, 2000)
    data = {'threshold': rand_threshold}
    session.patch(CONNECTION + '/filter', data=data)
    resp = session.get(CONNECTION + '/filter').json()
    assert assert_same_dict_content(data, resp)

def test_get_ventilation(session):
    resp = session.get(CONNECTION + '/fans').json()
    assert_valid_schema(resp, 'fans.json')

def test_patch_ventilation(session):
    rand_min_rpm = random.randint(1, 20)
    rand_max_rpm = random.randint(21, 100)
    data = {'min_rpm': rand_min_rpm, 'max_rpm': rand_max_rpm}
    session.patch(CONNECTION + '/fans', data=data)
    resp = session.get(CONNECTION + '/fans').json()
    assert assert_same_dict_content(data, resp)

def test_get_operation(session):
    resp = session.get(CONNECTION + '/mode').json()
    assert_valid_schema(resp, 'operation.json')

def test_patch_operation_gpu(session):
    mode = 'gpu'
    rand_ontime = random.randint(50, 1000)
    rand_offtime = random.randint(50, 1000)
    data = {'active_mode': mode, 'ontime': rand_ontime, 'offtime': rand_offtime}
    session.patch(CONNECTION + '/mode', data=data)
    resp = session.get(CONNECTION + '/mode').json()
    assert assert_same_dict_content(data, resp)

def test_patch_operation_asic(session):
    mode = 'asic'
    rand_restime = random.randint(50, 1000)
    data = {'active_mode': mode, 'restime': rand_restime}
    session.patch(CONNECTION + '/mode', data=data)
    resp = session.get(CONNECTION + '/mode').json()
    assert assert_same_dict_content(data, resp)

def test_get_PID(session):
    resp = session.get(CONNECTION + '/pid').json()
    assert_valid_schema(resp, 'pid.json')

def test_put_PID(session):
    rand_pidp = random.randint(0, 10)
    rand_pidi = random.randint(0, 20)
    rand_pidd = random.randint(0, 30)
    rand_pidb = random.randint(0, 40)
    data = {'proportional': rand_pidp, 'integral': rand_pidi,
            'derivative': rand_pidd, 'bias': rand_pidb}
    session.put(CONNECTION + '/pid', data=data)
    resp = session.get(CONNECTION + '/pid').json()
    assert assert_same_dict_content(data, resp)

def test_get_config(session):
    resp = session.get(CONNECTION + '/cfg').json()
    assert_valid_schema(resp, 'config.json')

def test_patch_config(session):
    rand_target = random.randint(20, 30)
    rand_sensor_id = random.randint(0, 4)
    rand_external = random.randint(20, 50)
    rand_threshold = random.randint(1000, 2000)
    rand_min_rpm = random.randint(1, 20)
    rand_max_rpm = random.randint(21, 100)
    mode = 'asic'
    rand_restime = random.randint(50, 1000)
    rand_ontime = random.randint(50, 1000)
    rand_offtime = random.randint(50, 1000)
    rand_pidp = random.randint(0, 10)
    rand_pidi = random.randint(0, 20)
    rand_pidd = random.randint(0, 30)
    rand_pidb = random.randint(0, 40)

    data = {'target': rand_target, 'sensor_id': rand_sensor_id,
            'external': rand_external, 'threshold': rand_threshold,
            'min_rpm': rand_min_rpm, 'max_rpm': rand_max_rpm,
            'proportional': rand_pidp, 'integral': rand_pidi,
            'derivative': rand_pidd, 'bias': rand_pidb,
            'active_mode': mode, 'restime': rand_restime,
            'ontime': rand_ontime, 'offtime': rand_offtime}
    session.patch(CONNECTION + '/cfg', data=data)
    resp = session.get(CONNECTION + '/cfg').json()
    assert assert_same_dict_content(data, resp)

def test_get_miner(session):
    resp = session.get(CONNECTION + '/miner?id=' + \
                       str(random.randint(0, 120))).json()
    assert_valid_schema(resp, 'miner_controller.json')

def test_patch_miner_on(session):
    miner_id = str(random.randint(0, 119))
    action = 'on'
    session.patch(CONNECTION +
                  '/miner?id=' + miner_id + '&' +
                  'action=' + action)
    resp = session.get(CONNECTION + '/miner?id=' + miner_id).json()
    assert assert_same_dict_content({'running': True}, resp)

def test_patch_miner_off(session):
    miner_id = str(random.randint(0, 119))
    action = 'off'
    session.patch(CONNECTION +
                  '/miner?id=' + miner_id + '&' +
                  'action=' + action)
    resp = session.get(CONNECTION + '/miner?id=' + miner_id).json()
    assert assert_same_dict_content({'running': False}, resp)

def test_patch_miner_toggle(session):
    miner_id = str(random.randint(0, 119))
    action = 'toggle'
    init_state = session.get(
        CONNECTION + '/miner?id=' + miner_id).json()['running']
    session.patch(CONNECTION +
                  '/miner?id=' + miner_id + '&' +
                  'action=' + action)
    resp = session.get(CONNECTION + '/miner?id=' + miner_id).json()
    assert assert_same_dict_content({'running': not init_state}, resp)

def test_patch_miner_deregister(session):
    miner_id = str(random.randint(0, 119))
    action = 'deregister'
    session.patch(CONNECTION +
                  '/miner?id=' + miner_id + '&' +
                  'action=' + action)
    resp = session.get(CONNECTION + '/miner?id=' + miner_id).json()
    assert assert_same_dict_content({'running': None}, resp)

def test_patch_miner_on(session):
    miner_id = str(random.randint(0, 119))
    action = 'register'
    session.patch(CONNECTION +
                  '/miner?id=' + miner_id + '&' +
                  'action=' + action)
    resp = session.get(CONNECTION + '/miner?id=' + miner_id).json()
    assert assert_same_dict_content({'running': True}, resp)

@pytest.fixture
def session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    session.mount('http://', adapter)
    return session
