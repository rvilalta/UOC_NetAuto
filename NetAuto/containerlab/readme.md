## Emulació de xarxes amb containerlab ##
Per instal·lar docker a Ubuntu/Debian, seguim els següents passos:

```console
$ sudo apt-get update
$ sudo apt-get install -y docker.io
$ sudo systemctl enable docker
$ sudo systemctl start docker
$ docker version
```

Podem instal·lar containerlab des del repositori oficial de [containerlab](https://containerlab.dev/install/) amb: 

```console
$ sudo bash -c "$(curl -sL https://get.containerlab.dev)"
$ containerlab version
```

### Desplegar i eliminar la topologia ###

Un cop definit el fitxer de topologia (per exemple, topologia-basic.clab.yml), pots desplegar la xarxa amb:

```console
containerlab deploy -t topologia-basic.clab.yml
```
Aquesta comanda descarrega les imatges Docker (si no hi són), crea els contenidors i les interfícies virtuals, i, finalment, assigna noms i configuracions bàsiques als nodes.

Pots comprovar l’estat amb:
```console
$ containerlab inspect -t topologia-basic.clab.yml
```

Quan vulguis eliminar la topologia:
```console
$ containerlab destroy -t topologia-basic.clab.yml
```
\section{Exemple de topologia amb múltiples routers}

Suposem que volem una topologia amb 3 routers FRR i 2 hosts, connectats així:

  PC1 --- R1 --- R2 --- R3 --- PC2



```console
containerlab deploy -t topologia-multi.clab.yml
```

### Configuració de FRR (exemple de BGP senzill) ###

Els contenidors que fan servir la imatge (frrouting/frr:latest) permeten configurar protocols de routing dinàmics (BGP, OSPF, IS-IS, etc.). Podem accedir a la CLI de FRR via consola o bé per SSH.
Després de desplegar la topologia, pots accedir a cada contenidor amb Docker:

```console
docker exec -it <nom-del-contenidor> vtysh
```
o

```console
docker exec -it <nom-del-contenidor> bash
```

Comprova el nom de cada contenidor amb la comanda:
```console
$ docker ps
```

A tall d’exemple, podem assignar IPs i configurar BGP a R1, R2, R3. Imaginem:

1. R1:
  * eth1 = 192.168.1.1/24 (cap a PC1)
  * eth2 = 10.0.12.1/24 (cap a R2)
2. R2:
  * eth1 = 10.0.12.2/24 (cap a R1)
  * eth2 = 10.0.23.2/24 (cap a R3)
3. R3:
  * eth1 = 10.0.23.3/24 (cap a R2)
  * eth2 = 192.168.2.1/24 (cap a PC2)

Accedim a R1:
```console
$ docker exec -it topologia-multi-clab-R1 vtysh
```
Exemple de configuració FRR a R1:
```
configure terminal
!
interface eth1
 ip address 192.168.1.1/24
!
interface eth2
 ip address 10.0.12.1/24
!
router bgp 65001
 bgp router-id 1.1.1.1
 neighbor 10.0.12.2 remote-as 65002
 network 192.168.1.0/24
!
end
write
```

Es repeteixen passos similars a R2 i R3, ajustant veïns BGP i adreces IP. Per verificar, fem \texttt{show ip bgp summary} a cada router.

### Configuració d’una L3VPN amb FRR ###


Per muntar una \textbf{L3VPN (BGP VPNv4)} en un entorn de laboratori, cal un escenari amb \textbf{VRFs} i, usualment, l’ús de \textbf{MPLS} a la troncal. Els passos principals són:

\begin{enumerate}
    \item Distingir \emph{PE (Provider Edge)}, \emph{P (Provider)} i \emph{CE (Customer Edge)}.
    \item Els \emph{PE} tindran VRFs associades a cada client i establiran BGP VPNv4 amb altres PE.
    \item Els \emph{P} fan commutació MPLS.
    \item Els \emph{CE} estan connectats als \emph{PE}, normalment amb BGP o un altre protocol per anunciar rutes.
\end{enumerate}

\subsection{Exemple de topologia per a una L3VPN simplificada}

\begin{minted}{yaml}
name: l3vpn-lab

topology:
  nodes:
    P1:
      kind: linux
      image: frrouting/frr:latest
    PE1:
      kind: linux
      image: frrouting/frr:latest
    PE2:
      kind: linux
      image: frrouting/frr:latest
    CE1:
      kind: linux
      image: frrouting/frr:latest
    CE2:
      kind: linux
      image: frrouting/frr:latest

  links:
    - endpoints: ["PE1:eth1", "P1:eth1"]
    - endpoints: ["PE2:eth1", "P1:eth2"]
    - endpoints: ["PE1:eth2", "CE1:eth1"]
    - endpoints: ["PE2:eth2", "CE2:eth1"]
\end{minted}

\subsection{Pas bàsic: activació de MPLS al nucli Linux}

Abans de res, pots activar MPLS a l’amfitrió Linux i als contenidors. Per exemple:

\begin{minted}{bash}
sudo sysctl -w net.mpls.conf.eth0.input=1
sudo sysctl -w net.mpls.platform_labels=100000
sudo sysctl -w net.ipv4.ip_forward=1
\end{minted}

\subsection{Configuració de FRR per a L3VPN}

Un cop tinguis MPLS operatiu:
\begin{itemize}
    \item Habilita \texttt{LDP} (Label Distribution Protocol) o Segment Routing.
    \item Configura \textbf{VRFs} als routers PE i associa-hi les interfícies CE.
    \item Configura el BGP per a:
    \begin{itemize}
        \item \textbf{Address-Family} \texttt{VPNv4} (entre PE).
        \item \textbf{Address-Family} \texttt{IPv4 VRF} (entre PE i CE).
    \end{itemize}
\end{itemize}

Exemple de creació d’una VRF i configuració BGP:

\begin{minted}{text}
configure terminal
vrf CE1
 vni 100
exit-vrf

vrf CE2
 vni 200
exit-vrf

interface eth2 vrf CE1
 ip address 192.168.1.1/24

router bgp 65001
 bgp router-id 1.1.1.1

 address-family ipv4 vrf CE1
  redistribute connected
 exit-address-family

 address-family vpnv4
  neighbor <IP-PE2> activate
  neighbor <IP-PE2> send-community extended
 exit-address-family

end
write
\end{minted}

Es repeteix una configuració semblant a \texttt{PE2}, creant la VRF \texttt{CE2}, etc. Els \texttt{CE} parlen BGP (o un altre protocol) amb el \texttt{PE} dins de la VRF corresponent.
