def check_compliance(config_output):
    required_lines = [
        "aaa new-model",
        "ip access-list extended BLOCKED_TRAFFIC",
    ]
    
    compliance_results = []
    
    for line in required_lines:
        if line not in config_output:
            compliance_results.append(f"Compliance check failed: missing '{line}'")
        else:
            compliance_results.append(f"OK: '{line}' found")

    return compliance_results

# Exemple d'ús
config_output = """
aaa new-model
interface GigabitEthernet0/1
 ip address 192.168.1.1 255.255.255.0
!
line vty 0 4
 transport input ssh
"""

results = check_compliance(config_output)
for result in results:
    print(result)
