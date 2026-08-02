import paramiko

devices = ['172.31.23.1', '172.31.23.4', '172.31.23.5', '172.31.23.2', '172.31.23.3']

for ip in devices:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip,username='admin',key_filename='key/ipa3_key')

    if ip == devices[0]:
        stdin, stdout, stderr = client.exec_command('show running-config')
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        with open('R0_running_config.txt', 'w', encoding='utf-8') as file:
            file.write(output)
        print("Saved R0 configuration successfully!")
    else:
        stdin, stdout, stderr = client.exec_command('show running-config | include hostname')
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        print(output)

    if errors:
        print(errors)
    
    client.close()