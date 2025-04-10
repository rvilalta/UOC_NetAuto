## Laboratori sobre Xarxes Sensibles al Temps amb Mininet ##

### Exercici 1: Priorització de Trànsit amb tc ###

En aquest exercici, explorarem com tc (traffic control) permet prioritzar el trànsit en una xarxa simulada amb Mininet.

#### Configuració de la Xarxa ####

Crearem una xarxa lineal simple amb dos hosts i un switch:

```console
sudo mn --topo=linear,2 --link tc
```

#### Generació de Trànsit ####

Simularem trànsit normal i trànsit sensible al temps amb \texttt{iperf}:

1. Trànsit normal (UDP)
```console
sudo mn
h1 iperf -s -u -p 5001
```

2. Trànsit sensible al temps (UDP, 1 Mbps)

```console
sudo mn
h2 iperf -c 10.0.0.1 -u -p 5002 -b 1M -t 10
```

#### Priorització amb tc  ####

Utilitzarem tc per donar prioritat al trànsit sensible al temps:

```console
h2 tc qdisc add dev h2-eth0 root handle 1: prio
h2 tc filter add dev h2-eth0 parent 1: protocol ip u32 match ip sport 5002 0xffff flowid 1:1
h2 tc qdisc add dev h2-eth0 parent 1:1 handle 10: netem delay 1ms
```

#### Anàlisi ####

Observa com la latència del trànsit sensible al temps es manté baixa i consistent, fins i tot amb trànsit de fons. Experimenta canviant els paràmetres de tc per veure com afecten la priorització.

### Exercici 2: Simulació de Planificació de Trànsit ###

En aquest exercici, simularem un escenari on el trànsit crític es planifica per garantir una entrega determinista.

#### Configuració de la Xarxa ####

Utilitzarem la mateixa configuració de xarxa que a l'Exercici 1.

#### Generació de Trànsit Crític ####

Simularem trànsit crític periòdic amb iperf:

```console
sudo mn
h1 iperf -s -u -p 5001 -i 1
```

#### Generació de Trànsit de Fons #### 

Simularem trànsit de fons que pot interferir amb el trànsit crític:

```console
sudo mn
h2 iperf -c 10.0.0.1 -u -p 5002 -b 500K
```

#### Planificació amb tc #### 

Utilitzarem tc per planificar el trànsit crític:

```console
h1 tc qdisc add dev h1-eth0 root handle 1: prio
h1 tc filter add dev h1-eth0 parent 1: protocol ip u32 match ip sport 5001 0xffff flowid 1:1
h1 tc qdisc add dev h1-eth0 parent 1:1 handle 10: netem rate 1M delay 1ms
```

#### Anàlisi ####

Observa com el trànsit crític manté una latència consistent i previsible, independentment del trànsit de fons. Investiga com canviar els paràmetres de tc per simular diferents algoritmes de planificació.

### Exercici 3: Simulació de Time-Aware Shaper (TAS) ###

#### Objectiu ####

Simular un aspecte de TAS, un component clau de TSN, per garantir la transmissió en temps determinista.

#### Configuració ####

```console
sudo mn --topo=linear,2 --link tc
```

#### Trànsit ####
1. Trànsit crític (períodic)
```console
sudo mn
h1 iperf -s -u -p 5001 -i 0.1
```

2. Trànsit de fons
```console
sudo mn
h2 iperf -c 10.0.0.1 -p 5002
```

#### Simulació de TAS amb tc ####

```console
h1 tc qdisc add dev h1-eth0 root handle 1: prio
h1 tc filter add dev h1-eth0 parent 1: protocol ip u32 match ip sport 5001 0xffff flowid 1:1
h1 tc qdisc add dev h1-eth0 parent 1:1 handle 10: netem rate 1M delay 1ms
```

#### Anàlisi ####

Observa com el trànsit crític manté una latència consistent i previsible, independentment del trànsit de fons. Ajusta \texttt{netem} per simular diferents horaris.


