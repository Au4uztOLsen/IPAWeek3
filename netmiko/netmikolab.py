from netmiko import ConnectHandler

device_s1 = {
    'device_type': 'cisco_ios',
    'host': '172.31.23.3',
    'username': 'admin',
    'key_file': 'key/ipa3_key',
}

device_r1 = {
    'device_type': 'cisco_ios',
    'host': '172.31.23.4',
    'username': 'admin',
    'key_file': 'key/ipa3_key',
}

device_r2 = {
    'device_type': 'cisco_ios',
    'host': '172.31.23.5',
    'username': 'admin',
    'key_file': 'key/ipa3_key',
}

s1_config = [
    'vlan 101',
    'name CONTROL_DATA_PLANE',
    'exit',
    'interface GigabitEthernet0/1',
    'switchport mode access',
    'switchport access vlan 101',
    'exit',
    'interface GigabitEthernet1/1',
    'switchport mode access',
    'switchport access vlan 101',
    'exit',
    
    'ip access-list standard VTY_ACCESS',
    'permit 172.31.23.0 0.0.0.255',
    'permit 10.30.6.0 0.0.1.255',
    'exit',
    'line vty 0 15',
    'access-class VTY_ACCESS in',
    'exit'
]

r1_config = [
    'no ip route 0.0.0.0 0.0.0.0 172.31.23.1',
    'router ospf 1 vrf control-data',
    'router-id 1.1.1.1',
    'network 172.31.3.0 0.0.0.255 area 0',
    'network 172.31.223.0 0.0.0.3 area 0',
    'network 1.1.1.1 0.0.0.0 area 0',
    'exit',
    
    'ip access-list standard VTY_ACCESS',
    'permit 172.31.23.0 0.0.0.255',
    'permit 10.30.6.0 0.0.1.255',
    'exit',
    'line vty 0 4',
    'access-class VTY_ACCESS in',
    'exit'
]

r2_config = [
    'no ip route 0.0.0.0 0.0.0.0 172.31.23.1',
    'ip dns server',
    'ip domain-lookup',
    'ip name-server vrf control-data 8.8.8.8',
    'router ospf 1 vrf control-data',
    'router-id 2.2.2.2',
    'network 172.31.223.0 0.0.0.3 area 0',
    'network 172.31.123.0 0.0.0.255 area 0',
    'network 2.2.2.2 0.0.0.0 area 0',
    'default-information originate always',
    'exit',
    
    'interface GigabitEthernet0/1',
    'ip nat inside',
    'exit',
    'interface GigabitEthernet0/2',
    'ip nat inside',
    'exit',
    'interface GigabitEthernet0/3',
    'vrf forwarding control-data',
    'ip address dhcp',
    'no shutdown',
    'ip nat outside',
    'exit',
    'ip route vrf control-data 0.0.0.0 0.0.0.0 GigabitEthernet0/3 dhcp',
    'ip access-list standard NAT_ACL',
    'permit 172.31.3.0 0.0.0.255',
    'permit 172.31.123.0 0.0.0.255',
    'permit 172.31.223.0 0.0.0.255',
    'exit',
    'ip nat inside source list NAT_ACL interface GigabitEthernet0/3 vrf control-data overload',
    
    'ip access-list standard VTY_ACCESS',
    'permit 172.31.23.0 0.0.0.255',
    'permit 10.30.6.0 0.0.1.255',
    'exit',
    'line vty 0 4',
    'access-class VTY_ACCESS in',
    'exit'
]

def run_netmiko(device_info, config_commands, device_name):
    try:
        net_connect = ConnectHandler(**device_info)
        output = net_connect.send_config_set(config_commands)
        print(output)
        net_connect.save_config()
        net_connect.disconnect()
        print(f"{device_name} configured successfully!\n")
    except Exception as e:
        print(f"Error configuring {device_name}: {e}\n")

run_netmiko(device_s1, s1_config, "S1")
run_netmiko(device_r1, r1_config, "R1")
run_netmiko(device_r2, r2_config, "R2")