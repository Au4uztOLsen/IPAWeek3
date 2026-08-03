import os
import re
from netmiko import ConnectHandler

try:
    import ntc_templates
    os.environ["NET_TEXTFSM"] = os.path.join(os.path.dirname(ntc_templates.__file__), "templates")
except ImportError:
    pass

devices = {
    'S1': {
        'device_type': 'cisco_ios',
        'host': '172.31.23.3',
        'username': 'admin',
        'key_file': 'key/ipa3_key',
        'pc_ports': ['GigabitEthernet0/1'],
        'fallback_cdp': []
    },
    'R1': {
        'device_type': 'cisco_ios',
        'host': '172.31.23.4',
        'username': 'admin',
        'key_file': 'key/ipa3_key',
        'pc_ports': ['GigabitEthernet0/1'],
        'fallback_cdp': [('GigabitEthernet0/2', 'R2', 'G0/1')]
    },
    'R2': {
        'device_type': 'cisco_ios',
        'host': '172.31.23.5',
        'username': 'admin',
        'key_file': 'key/ipa3_key',
        'pc_ports': [],
        'wan_ports': ['GigabitEthernet0/3'],
        'fallback_cdp': [('GigabitEthernet0/1', 'R1', 'G0/2')]
    }
}

def shorten_intf(intf_name):
    if not intf_name:
        return ""
    clean = intf_name.replace(" ", "")
    clean = re.sub(r'^(GigabitEthernet|Gig|Gi)', 'G', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^(FastEthernet|Fas|Fa)', 'Fa', clean, flags=re.IGNORECASE)
    return clean

def parse_cdp_neighbors(cdp_data):
    results = []
    if isinstance(cdp_data, list):
        for item in cdp_data:
            dev = item.get('destination_host') or item.get('neighbor') or item.get('device_id') or ""
            local = item.get('local_interface') or item.get('local_port') or ""
            remote = item.get('neighbor_interface') or item.get('port_id') or ""
            if dev and local and remote:
                results.append((local, dev.split('.')[0], remote))
        return results

    if isinstance(cdp_data, str):
        lines = cdp_data.strip().splitlines()
        header_found = False
        for line in lines:
            if 'Device ID' in line or 'Device-ID' in line:
                header_found = True
                continue
            if header_found and line.strip() and not line.startswith('-'):
                match = re.search(
                    r'^(\S+?)(?:\.\S+)?\s+([A-Za-z]+\s*\d+(?:/\d+)*)\s+\d+\s+.*?\s+([A-Za-z]+\s*\d+(?:/\d+)*)$',
                    line.strip()
                )
                if match:
                    results.append((match.group(2), match.group(1), match.group(3)))
    return results

def configure_descriptions():
    for dev_name, dev_info in devices.items():
        print(f"Connecting to {dev_name}...")
        conn = ConnectHandler(
            device_type=dev_info['device_type'],
            host=dev_info['host'],
            username=dev_info['username'],
            key_file=dev_info['key_file']
        )
        
        config_cmds = []
        configured_intfs = set()
        
        try:
            cdp_raw = conn.send_command("show cdp neighbors", use_textfsm=True)
            cdp_list = parse_cdp_neighbors(cdp_raw)
            for local_intf, remote_dev, remote_intf in cdp_list:
                remote_short = shorten_intf(remote_intf)
                desc = f"Connect to {remote_short} of {remote_dev}"
                config_cmds.extend([
                    f"interface {local_intf}",
                    f"description {desc}",
                    "exit"
                ])
                configured_intfs.add(local_intf)
        except Exception as e:
            print(f"CDP Warning on {dev_name}: {e}")

        for local_intf, remote_dev, remote_intf in dev_info.get('fallback_cdp', []):
            if local_intf not in configured_intfs:
                remote_short = shorten_intf(remote_intf)
                desc = f"Connect to {remote_short} of {remote_dev}"
                config_cmds.extend([
                    f"interface {local_intf}",
                    f"description {desc}",
                    "exit"
                ])
                configured_intfs.add(local_intf)

        for pc_port in dev_info.get('pc_ports', []):
            config_cmds.extend([
                f"interface {pc_port}",
                "description Connect to PC",
                "exit"
            ])

        for wan_port in dev_info.get('wan_ports', []):
            config_cmds.extend([
                f"interface {wan_port}",
                "description Connect to WAN",
                "exit"
            ])

        if config_cmds:
            output = conn.send_config_set(config_cmds)
            print(f"--- Output from {dev_name} ---")
            print(output)
            conn.save_config()
            
        conn.disconnect()

if __name__ == "__main__":
    configure_descriptions()