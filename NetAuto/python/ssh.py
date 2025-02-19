from netmiko import ConnectHandler

cisco_device = {
    'device_type': 'cisco_ios',
    'ip': '192.168.1.10',
    'username': 'admin',
    'password': 'adminpass',
}

connection = ConnectHandler(**cisco_device)
output = connection.send_command("show ip interface brief")
print(output)
connection.disconnect()
