import pytest
from netmiko import ConnectHandler

@pytest.fixture(scope="module")
def r1_conn():
    conn = ConnectHandler(device_type='cisco_ios', host='172.31.23.4', username='admin', key_file='key/ipa3_key')
    yield conn
    conn.disconnect()

@pytest.fixture(scope="module")
def r2_conn():
    conn = ConnectHandler(device_type='cisco_ios', host='172.31.23.5', username='admin', key_file='key/ipa3_key')
    yield conn
    conn.disconnect()

@pytest.fixture(scope="module")
def s1_conn():
    conn = ConnectHandler(device_type='cisco_ios', host='172.31.23.3', username='admin', key_file='key/ipa3_key')
    yield conn
    conn.disconnect()

def test_r1_g02_description(r1_conn):
    output = r1_conn.send_command("show interfaces GigabitEthernet0/2 description")
    assert "Connect to G0/1 of R2" in output

def test_r2_g03_wan_description(r2_conn):
    output = r2_conn.send_command("show interfaces GigabitEthernet0/3 description")
    assert "Connect to WAN" in output

def test_s1_g01_pc_description(s1_conn):
    output = s1_conn.send_command("show interfaces GigabitEthernet0/1 description")
    assert "Connect to PC" in output