from netmiko import ConnectHandler
from jinja2 import Template

devices = {
    'S1': {
        'device_type': 'cisco_ios',
        'host': '172.31.23.3',
        'username': 'admin',
        'key_file': 'key/ipa3_key',
    },
    'R1': {
        'device_type': 'cisco_ios',
        'host': '172.31.23.4',
        'username': 'admin',
        'key_file': 'key/ipa3_key',
    },
    'R2': {
        'device_type': 'cisco_ios',
        'host': '172.31.23.5',
        'username': 'admin',
        'key_file': 'key/ipa3_key',
    }
}

s1_data = {
    'vlan_id': 101,
    'vlan_name': 'CONTROL_DATA_PLANE',
    'access_ports': ['GigabitEthernet0/1', 'GigabitEthernet0/3'],
    'vty_permit_nets': ['172.31.23.0 0.0.0.15', '10.30.6.0 0.0.1.255']
}

r1_data = {
    'router_id': '1.1.1.1',
    'ospf_networks': [
        '172.31.3.0 0.0.0.255',
        '172.31.223.0 0.0.0.3',
        '1.1.1.1 0.0.0.0'
    ],
    'vty_permit_nets': ['172.31.23.0 0.0.0.15', '10.30.6.0 0.0.1.255'],
    'block_mgmt_intf': 'GigabitEthernet0/1'
}

r2_data = {
    'router_id': '2.2.2.2',
    'ospf_networks': [
        '172.31.223.0 0.0.0.3',
        '172.31.123.0 0.0.0.255',
        '2.2.2.2 0.0.0.0'
    ],
    'nat_acl_nets': [
        '172.31.3.0 0.0.0.255',
        '172.31.123.0 0.0.0.255',
        '172.31.223.0 0.0.0.255'
    ],
    'vty_permit_nets': ['172.31.23.0 0.0.0.15', '10.30.6.0 0.0.1.255'],
    'block_mgmt_intfs': ['GigabitEthernet0/1', 'GigabitEthernet0/2']
}

s1_template_str = """
vlan {{ vlan_id }}
 name {{ vlan_name }}
exit
{% for port in access_ports %}
interface {{ port }}
 switchport mode access
 switchport access vlan {{ vlan_id }}
exit
{% endfor %}
ip access-list standard VTY_ACCESS
{% for net in vty_permit_nets %}
 permit {{ net }}
{% endfor %}
exit
line vty 0 15
 access-class VTY_ACCESS in
exit
"""

r1_template_str = """
no ip route 0.0.0.0 0.0.0.0 172.31.23.1
router ospf 1 vrf control-data
 router-id {{ router_id }}
{% for net in ospf_networks %}
 network {{ net }} area 0
{% endfor %}
exit
ip access-list extended BLOCK_MGMT
 deny ip any 172.31.23.0 0.0.0.15
 permit ip any any
exit
interface {{ block_mgmt_intf }}
 ip access-group BLOCK_MGMT in
exit
ip access-list standard VTY_ACCESS
{% for net in vty_permit_nets %}
 permit {{ net }}
{% endfor %}
exit
line vty 0 4
 access-class VTY_ACCESS in
exit
"""

r2_template_str = """
no ip route 0.0.0.0 0.0.0.0 172.31.23.1
ip domain lookup
ip name-server vrf control-data 8.8.8.8
ip dns view vrf control-data default
ip dns server
router ospf 1 vrf control-data
 router-id {{ router_id }}
{% for net in ospf_networks %}
 network {{ net }} area 0
{% endfor %}
 default-information originate always
exit
ip access-list extended BLOCK_MGMT
 deny ip any 172.31.23.0 0.0.0.15
 permit ip any any
exit
{% for intf in block_mgmt_intfs %}
interface {{ intf }}
 ip nat inside
 ip access-group BLOCK_MGMT in
exit
{% endfor %}
interface GigabitEthernet0/3
 vrf forwarding control-data
 ip address dhcp
 no shutdown
 ip nat outside
exit
ip route vrf control-data 0.0.0.0 0.0.0.0 GigabitEthernet0/3 dhcp
ip access-list standard NAT_ACL
{% for net in nat_acl_nets %}
 permit {{ net }}
{% endfor %}
exit
ip nat inside source list NAT_ACL interface GigabitEthernet0/3 vrf control-data overload
ip access-list standard VTY_ACCESS
{% for net in vty_permit_nets %}
 permit {{ net }}
{% endfor %}
exit
line vty 0 4
 access-class VTY_ACCESS in
exit
"""

def deploy_config(device_info, template_str, config_data, device_name):
    try:
        template = Template(template_str)
        rendered_config = template.render(config_data)
        config_commands = [line.strip() for line in rendered_config.splitlines() if line.strip()]

        print(f"Connecting to {device_name}...")
        net_connect = ConnectHandler(**device_info)
        
        output = net_connect.send_config_set(config_commands)
        print(f"--- Output from {device_name} ---")
        print(output)
        
        net_connect.save_config()
        net_connect.disconnect()
        print(f"{device_name} configured successfully!\n")
    except Exception as e:
        print(f"Error configuring {device_name}: {e}\n")

deploy_config(devices['S1'], s1_template_str, s1_data, "S1")
deploy_config(devices['R1'], r1_template_str, r1_data, "R1")
deploy_config(devices['R2'], r2_template_str, r2_data, "R2")