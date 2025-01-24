## EXEMPLE RYU I MININET ##
Instruccions per UBUNTU 22.04

Primer, cal instal·lar les dependències:  
```console
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt-get install virtualenv python3.9 python3.9-distutils
$ virtualenv -p`which python3.9` ryu-python3.9-venv
$ source ryu-python3.9-venv/bin/activate
```

Dins entorn virtual:
```console
$ echo $VIRTUAL_ENV 
$ pip install ryu
$ pip uninstall eventlet
$ pip install eventlet==0.30.2
$ ryu-manager --help
```

En una finestra de terminal, arrenquem el controlador Ryu amb la nostra aplicació: 
```console
$ ryu-manager --verbose SimpleFlowApp.py
```

En una altra finestra, engeguem l’entorn Mininet amb l’script anterior o bé amb alguna comanda tipus:  
```console
$ sudo python3 topo_mininet.py
```

Un cop iniciat Mininet, podem fer proves de connectivitat (ping, netcat, iperf, etc.) entre h1, h2 i h3 per comprovar com el trànsit és gestionat d’acord amb les regles de flux instal·lades.

```console
mininet> h1 ping h2
```


