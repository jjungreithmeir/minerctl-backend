import json
import requests
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

@pytest.fixture
def session():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    session.mount('http://', adapter)
    return session
