from netmiko import ConnectHandler

def backup_config(ip, username, password):
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
    }
    connection = ConnectHandler(**device)
    running_config = connection.send_command("show running-config")
    with open(f"{ip}_backup.txt", "w") as backup_file:
        backup_file.write(running_config)
    connection.disconnect()

if __name__ == "__main__":
    backup_config("192.168.1.10", "admin", "adminpass")
