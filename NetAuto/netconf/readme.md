## Programabilitat basada en models i gestió de xarxa ##
En aquesta secció farem ús de clients NETCONF (p. ex., ncclient) per consultar o actualitzar configuracions de dispositius.

### Configuració de l'entorn ###
Per començar, instal·leu `ncclient` al vostre entorn Python:

```console
$ pip install ncclient
```

Com que no tenim accés a un dispositiu real, utilitzarem un servidor NETCONF emulat. A continuació, es presenten diverses opcions:

#### Opció 1: Servidor NETCONF d'OpenDaylight (Docker) ####
Per executar un servidor NETCONF d'OpenDaylight, utilitzeu Docker:

```console
$ docker run -d --name odl-netconf \
    -p 830:830 \
    opendaylight/netconf
```

Això iniciarà un servidor NETCONF d'OpenDaylight al port 830.

#### Opció 2: Cisco DevNet Sandbox ####
Cisco ofereix un *sandbox* gratuït en línia amb un dispositiu habilitat per NETCONF. Connecteu-vos-hi utilitzant:

```
host = "sandbox-iosxe-latest-1.cisco.com"
port = 830
username = "developer"
password = "C1sco12345"
```

#### Opció 3: Emulador NETCONF FRINX UniConfig ####
FRINX UniConfig proporciona un emulador NETCONF contenidoritzat. Executeu-lo amb:

```console
$ docker run -d --name frinx-netconf \
    -p 8181:8181 -p 8182:8182 -p 830:830 \
    frinx/uniconfig
```

#### Opció 4: Consola NETCONF de YANG Suite ####
Instal·leu `yangsuite` i executeu un servei NETCONF local:

```console
$ pip install yangsuite
$ netconf-console --port 830
```

### Connexió a un servidor NETCONF emulat ###
Utilitzeu el següent script en Python per establir una sessió NETCONF:

```
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
```

### Recuperació de dades de configuració ###
Per obtenir la configuració en execució del dispositiu emulat, utilitzeu:

```
filter = "<filter><interfaces/></filter>"
config = m.get_config(source='running', filter=('subtree', filter))
print(config.xml)
```

### Modificació de la configuració del dispositiu ###
Per actualitzar la configuració d'un dispositiu, utilitzeu:

```
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
```

### Tancament de la connexió ###
Tanqueu sempre la sessió quan hàgiu acabat:

```
m.close_session()
```
