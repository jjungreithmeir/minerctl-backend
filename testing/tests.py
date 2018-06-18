import json
import requests
from assertions import assert_valid_schema
import pytest


def test_get_info(sess):
    # Do whatever is necessary to create a user here…

    response = sess.get('http://localhost:12345/info')
    json_data = response.json()

    assert_valid_schema(json_data, 'info.json')

@pytest.fixture
def sess():
    container_conn = 'http://localhost:12345'
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=10)
    sess.mount('http://', adapter)
    return sess
