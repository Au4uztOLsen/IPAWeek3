import re
from netmiko import ConnectHandler

devices = {
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

for dev_name, dev_info in devices.items():
    try:
        print(f"Connecting to {dev_name}...")
        net_connect = ConnectHandler(**dev_info)

        sh_ver = net_connect.send_command('show version')
        uptime_match = re.search(r'uptime is\s+(.*)', sh_ver)
        uptime = uptime_match.group(1) if uptime_match else "Unknown"

        sh_ip_int_brief = net_connect.send_command('show ip interface brief')
        active_interfaces = re.findall(r'(\S+)\s+\S+\s+\S+\s+\S+\s+up\s+up', sh_ip_int_brief)

        print(f"=== {dev_name} Results ===")
        print(f"Uptime: {uptime}")
        print(f"Active Interfaces: {', '.join(active_interfaces) if active_interfaces else 'None'}")
        print("=" * 35 + "\n")

        net_connect.disconnect()

    except Exception as e:
        print(f"Error connecting to {dev_name}: {e}\n")