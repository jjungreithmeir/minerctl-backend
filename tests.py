import json
import requests
import random
import pytest
import sys
# for some strange unexplainable reason I need to add the current folder to the
# sys.path
sys.path.append('.')
from testing.assertions import assert_valid_schema
from controller import create_app

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

def test_get_config(session):
    resp = session.get(CONNECTION + '/cfg').json()
    assert_valid_schema(resp, 'config.json')

def test_get_miner(session):
    resp = session.get(CONNECTION + '/miner?id=' + \
                       str(random.randint(0, 120))).json()
    assert_valid_schema(resp, 'miner_controller.json')

@pytest.fixture
def session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    session.mount('http://', adapter)
    return session
