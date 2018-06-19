import json
import requests
import random
from assertions import assert_valid_schema
import pytest


CONNECTION = 'http://localhost:12345'

def test_get_info(session):
    resp = session.get(CONNECTION + '/info').json()
    assert_valid_schema(resp, 'info.json')

def test_get_temperature(session):
    resp = session.get(CONNECTION + '/temp').json()
    assert_valid_schema(resp, 'temp.json')

def test_get_filtration(session):
    resp = session.get(CONNECTION + '/filter').json()
    assert_valid_schema(resp, 'filter.json')

def test_get_ventilation(session):
    resp = session.get(CONNECTION + '/fans').json()
    assert_valid_schema(resp, 'fans.json')

def test_get_operation(session):
    resp = session.get(CONNECTION + '/mode').json()
    assert_valid_schema(resp, 'operation.json')

def test_get_PID(session):
    resp = session.get(CONNECTION + '/pid').json()
    assert_valid_schema(resp, 'pid.json')

def test_get_PID(session):
    resp = session.get(CONNECTION + '/cfg').json()
    assert_valid_schema(resp, 'config.json')

def test_get_miner(session):
    resp = session.get(CONNECTION + '/miner/' + \
                       str(random.randint(0, 120))).json()
    assert_valid_schema(resp, 'miner_controller.json')

@pytest.fixture
def session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    session.mount('http://', adapter)
    return session
