from ncclient import manager

# Substituir per les credencials del dispositiu emulat escollit
host = "localhost"
port = 830
username = "admin"
password = "admin"

with manager.connect(host=host, port=port, username=username, 
                     password=password, hostkey_verify=False) as m:
    print("Connectat al servidor NETCONF!")
    print(m.server_capabilities)


#Recuperació de la configuració en execució
filter = "<filter><interfaces/></filter>"
config = m.get_config(source='running', filter=('subtree', filter))
print(config.xml)

#Actualització de la configuració del dispositiu
config_data = """
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <description>Configurat via NETCONF</description>
        </interface>
    </interfaces>
</config>
"""
m.edit_config(target='running', config=config_data)


# Tancament de la connexió
m.close_session()
