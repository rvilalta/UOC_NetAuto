## EXEMPLE RYU I MININET ##
Primer, cal instal·lar les dependències:  
$ sudo apt-get install python3-ryu mininet openvswitch-switch

En una finestra de terminal, arrenquem el controlador Ryu amb la nostra aplicació:  
$ ryu-manager --verbose SimpleFlowApp.py

En una altra finestra, engeguem l’entorn Mininet amb l’script anterior o bé amb alguna comanda tipus:  
$ sudo python3 topo_mininet.py

Un cop iniciat Mininet, podem fer proves de connectivitat (ping, netcat, iperf, etc.) entre h1, h2 i h3 per comprovar com el trànsit és gestionat d’acord amb les regles de flux instal·lades.
mininet> h1 ping h2


