## Laboratori sobre Xarxes Sensibles al Temps amb Mininet ##

### Exercici 1: Priorització de Trànsit amb tc ###

En aquest exercici, explorarem com tc (traffic control) permet prioritzar el trànsit en una xarxa simulada amb Mininet.

#### Configuració de la Xarxa ####

Crearem una xarxa lineal simple amb dos hosts i un switch:

```console
sudo mn --topo=linear,2 --link tc
# apareix el prompt "mininet>"
```

#### Generació de Trànsit ####

Simularem trànsit normal i trànsit sensible al temps amb \texttt{iperf}:

```console
# mininet> h1 iperf -s -u -p 5001             # servidor UDP (trànsit normal)
# -- en un altre terminal del CLI --
mininet> h2 iperf -c 10.0.0.1 -u -p 5002 -b 1M -t 10   # client UDP 1 Mbps (trànsit TSN)
```

#### Priorització amb tc  ####

Utilitzarem tc per donar prioritat al trànsit sensible al temps:

```console
mininet> h2 tc qdisc add dev h2-eth0 root handle 1: prio
mininet> h2 tc filter add dev h2-eth0 parent 1: protocol ip \
              u32 match ip sport 5002 0xffff flowid 1:1
mininet> h2 tc qdisc add dev h2-eth0 parent 1:1 handle 10: netem delay 1ms
```

#### Anàlisi ####

Observa com la latència del flux TSN es manté estable malgrat el trànsit de fons. Prova de variar la taxa (-b) o el retard de netem.

### Exercici 2: Simulació de Planificació de Trànsit ###

En aquest exercici, simularem un escenari on el trànsit crític es planifica per garantir una entrega determinista.

#### Configuració de la Xarxa ####

Utilitzarem la mateixa configuració de xarxa que a l'Exercici 1.

#### Generació de Trànsit Crític ####

Simularem trànsit crític periòdic amb iperf:

```console
# Reinicia la xarxa per a un nou escenari
sudo mn --topo linear,2 --link tc
```

#### Generació de Trànsit de Fons #### 

Simularem trànsit de fons que pot interferir amb el trànsit crític:

```console
# mininet> h1 iperf -s -u -p 5001 -i 1          # trànsit crític periòdic
# -- altre terminal --
mininet> h2 iperf -c 10.0.0.1 -u -p 5002 -b 500K  # trànsit de fons
```

#### Planificació amb tc #### 

Utilitzarem tc per planificar el trànsit crític:

```console
mininet> h1 tc qdisc add dev h1-eth0 root handle 1: prio
mininet> h1 tc filter add dev h1-eth0 parent 1: protocol ip \
              u32 match ip sport 5001 0xffff flowid 1:1
mininet> h1 tc qdisc add dev h1-eth0 parent 1:1 handle 10: \
              netem rate 1M delay 1ms
```

### Exercici 3: Simulació de Time-Aware Shaper (TAS) ###

#### Objectiu ####

Simular un aspecte de TAS, un component clau de TSN, per garantir la transmissió en temps determinista.

#### Configuració ####

```console
# Torna a arrencar Mininet
sudo mn --topo linear,2 --link tc
```

#### Trànsit ####

```console
# mininet> h1 iperf -s -u -p 5001 -i 0.1        # flux crític
# -- altre terminal --
mininet> h2 iperf -c 10.0.0.1 -p 5002           # trànsit de fons (TCP)
```

#### Simulació de TAS amb tc ####

```console
mininet> h1 tc qdisc add dev h1-eth0 root handle 1: prio
mininet> h1 tc filter add dev h1-eth0 parent 1: protocol ip \
              u32 match ip sport 5001 0xffff flowid 1:1
# Afegim una finestra de 1 ms cada 10 ms (exemple simplificat)
mininet> h1 tc qdisc add dev h1-eth0 parent 1:1 handle 10: \
              tbf rate 1M burst 10k latency 1ms
```

#### Anàlisi ####

Mesura el temps d’arribada dels paquets al receptor per comprovar que el flux crític
només es transmet a les finestres programades. 

