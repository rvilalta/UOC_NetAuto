##Ansible per a l'automatització de xarxes
###Preparació de l'entorn

Instruccions per UBUNTU 22.04
Per començar, instal·la Ansible al teu sistema:

```console
$ sudo apt update && sudo apt install ansible -y
```

Si fas servir un entorn virtual:

```console
$ pip install ansible
```

Com que no tenim accés a un dispositiu real, farem servir un entorn de xarxa emulada. A continuació es presenten dues opcions:

####Opció 1: Ús d'un contenidor Docker com a dispositiu de xarxa simulat
Executa un contenidor Linux senzill que actuarà com a dispositiu de xarxa:

```console
$ docker run -d --name ansible-network \
    -h network-device \
    --network=bridge \
    ubuntu:latest sleep infinity
```
####Opció 2: Ús de Cisco DevNet Sandbox
Cisco ofereix un entorn en línia (\textit{sandbox}) per fer proves amb Ansible. T’hi pots connectar via SSH i utilitzar Ansible per automatitzar configuracions.

###Configuració de l'inventari d'Ansible
Crea un fitxer d’inventari (\texttt{hosts.ini}) per definir els dispositius a gestionar:

```
[network_devices]
network-device ansible_host=localhost ansible_connection=ssh ansible_user=root ansible_password=password
```

###Creació d'un Playbook d'Ansible
Un \textit{playbook} defineix les tasques d'automatització. Crea un fitxer anomenat \texttt{configure.yml}:

```
- name: Configure network device
  hosts: network_devices
  gather_facts: no
  tasks:
    - name: Ensure hostname is set
      ansible.builtin.shell: echo "network-device" > /etc/hostname
```

###Execució del Playbook
Executa el \textit{playbook} amb:

```console
$ ansible-playbook -i hosts.ini configure.yml
```

###Exemples addicionals de Playbook

####Exemple 1: Instal·lació d’un paquet
Instal·la un paquet en un node gestionat:

```
- name: Install Nginx
  hosts: network_devices
  tasks:
    - name: Install Nginx package
      ansible.builtin.apt:
        name: nginx
        state: present
```

####Exemple 2: Copiar un fitxer de configuració
Copia un fitxer al node gestionat:

```
- name: Deploy Configuration File
  hosts: network_devices
  tasks:
    - name: Copy file to device
      ansible.builtin.copy:
        src: ./config.cfg
        dest: /etc/network/config.cfg
```

###Verificació de la configuració
Comprova si la configuració s’ha aplicat correctament:

```console
$ docker exec -it ansible-network cat /etc/hostname
```
