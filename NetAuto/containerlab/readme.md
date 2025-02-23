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
Per il·lustrar-ho, proposem una topologia senzilla (5 routers) amb:
* P1: router de tronc, sense clients directes.
* PE1 i PE2: routers d'accés a clients (PE = Provider Edge).
* CE1 i CE2: routers/hosts de client, connectats cadascun a un PE.

     CE1 --(VRF)-- PE1 --- P1 --- PE2 --(VRF)-- CE2



Per a label switching al nucli Linux, cal activar al host (amfitrió):
```console
sudo sysctl -w net.mpls.conf.eth0.input=1
sudo sysctl -w net.mpls.platform_labels=100000
sudo sysctl -w net.ipv4.ip_forward=1
```
També es recomana habilitar el forwarding IPv4 de forma permanent (per exemple, editant/etc/sysctl.conf). Si uses Kernel més modern, assegura't que tingui suport MPLS compilat.

Un cop la topologia estigui ``desplegada'':
```console
$ containerlab deploy -t l3vpn.clab.yml
```

Accedirem a cada contenidor (P1, PE1, PE2, CE1, CE2) i configurarem FRR segons el rol.

A títol d'exemple, proposem:

\begin{itemize}
    \item \textbf{Adreces a la troncal (PE1--P1--PE2)}: 
    \begin{itemize}
        \item PE1: \texttt{eth1} = 10.0.1.1/24
        \item P1: \texttt{eth1} = 10.0.1.2/24 (cap a PE1), \texttt{eth2} = 10.0.2.2/24 (cap a PE2)
        \item PE2: \texttt{eth1} = 10.0.2.1/24
    \end{itemize}
    \item \textbf{Accés a client A (CE1--PE1)}:
    \begin{itemize}
        \item CE1: \texttt{eth1} = 192.168.1.2/24
        \item PE1: \texttt{eth2} = 192.168.1.1/24 (per VRF \texttt{CLIENTA})
    \end{itemize}
    \item \textbf{Accés a client B (CE2--PE2)}:
    \begin{itemize}
        \item CE2: \texttt{eth1} = 192.168.2.2/24
        \item PE2: \texttt{eth2} = 192.168.2.1/24 (per VRF \texttt{CLIENTB})
    \end{itemize}
\end{itemize}

\subsection{Router P1 (núvol proveïdor)}
El \emph{router} P1 fa només funcions de \emph{tronc MPLS}. Necessita:
\begin{enumerate}
  \item Assignar IPs a \texttt{eth1} i \texttt{eth2}.
  \item Configurar un IGP (exemple OSPF o IS-IS) o BGP interior, per tal que hi hagi \emph{reachability} entre PE1 i PE2.
  \item Habilitar \texttt{mpls} i \texttt{ldp}.
\end{enumerate}

Exemple de configuració a P1 (via \texttt{vtysh}):
\begin{minted}{text}
configure terminal
!
interface eth1
 ip address 10.0.1.2/24
!
interface eth2
 ip address 10.0.2.2/24
!
router ospf
 network 10.0.1.0/24 area 0
 network 10.0.2.0/24 area 0
!
mpls label protocol ldp
router mpls ldp
 ! El router-id es pot basar en l'adreça principal (p.ex. 2.2.2.2)
 ! o configurat explicitament
end
write
\end{minted}

Amb això, P1 intercanviarà etiquetes MPLS amb PE1 i PE2 via LDP (sempre que ells també tinguin LDP habilitat).

\subsection{Router PE1}
PE1 és un \emph{router d'accés}, per tant:
\begin{itemize}
  \item \textbf{Troncal}: \texttt{eth1 = 10.0.1.1/24} (cap a P1).
  \item \textbf{Accés client A}: \texttt{eth2 = 192.168.1.1/24}, però dins la VRF \texttt{CLIENTA}.
\end{itemize}

Cal configurar:
\begin{enumerate}
    \item IP i LDP a la interfície troncal (\texttt{eth1}).
    \item VRF \texttt{CLIENTA} i assignar \texttt{eth2} a la VRF.
    \item Sessió BGP \emph{VPNv4} amb \texttt{PE2} (entre ells es veuen via P1).
    \item Sessió BGP amb \texttt{CE1} (address-family ipv4 en VRF \texttt{CLIENTA}) o un protocol que escullis (p.\,ex. OSPF).
\end{enumerate}

Exemple:
\begin{minted}{text}
configure terminal
!
interface eth1
 ip address 10.0.1.1/24
!
router ospf
 network 10.0.1.0/24 area 0
!
mpls label protocol ldp
router mpls ldp
 ! router-id 1.1.1.1 (opcional)
!
! Definició VRF
vrf CLIENTA
 vni 10
exit-vrf
!
interface eth2 vrf CLIENTA
 ip address 192.168.1.1/24
!
! BGP Global
router bgp 65000
 bgp router-id 1.1.1.1
 ! Sessió BGP interior (o IBGP) amb l'adreça de loopback / IP del PE2
 neighbor 10.0.2.1 remote-as 65000
 update-source eth1
 ! Activa VPNv4
 address-family vpnv4
  neighbor 10.0.2.1 activate
  neighbor 10.0.2.1 send-community extended
 exit-address-family

 ! VRF CLIENTA
 address-family ipv4 vrf CLIENTA
  redistribute connected
 exit-address-family
end
write
\end{minted}

En aquest exemple, s’ha usat \texttt{router bgp 65000} tant a PE1 com a PE2 (IBGP), i la troncal va per la xarxa 10.0.x.x. L’\emph{address-family vpnv4} és la que permet compartir rutes de VRF entre PE1 i PE2, transportant etiquetes MPLS.

\subsection{Router PE2}
A \textbf{PE2} passa el mateix concepte, però amb la VRF \texttt{CLIENTB}:
\begin{minted}{text}
configure terminal
!
interface eth1
 ip address 10.0.2.1/24
!
router ospf
 network 10.0.2.0/24 area 0
!
mpls label protocol ldp
router mpls ldp
 ! router-id 2.2.2.2 (opcional)
!
vrf CLIENTB
 vni 20
exit-vrf
!
interface eth2 vrf CLIENTB
 ip address 192.168.2.1/24
!
router bgp 65000
 bgp router-id 2.2.2.2
 neighbor 10.0.1.1 remote-as 65000
 update-source eth1
 address-family vpnv4
  neighbor 10.0.1.1 activate
  neighbor 10.0.1.1 send-community extended
 exit-address-family

 address-family ipv4 vrf CLIENTB
  redistribute connected
 exit-address-family
end
write
\end{minted}

\subsection{Routers CE (CE1 i CE2)}
Els routers CE poden tenir configuracions senzilles. Poden fer:
\begin{itemize}
    \item BGP amb la VRF del PE.
    \item OSPF o estàtic: Depèn de l'escenari.
\end{itemize}
Imaginem que CE1 fa BGP amb PE1 (AS 65010), i CE2 fa BGP amb PE2 (AS 65020). O bé tots dins del mateix AS, etc. Aquí un exemple ràpid de \texttt{CE1}:

\begin{minted}{text}
configure terminal
interface eth1
 ip address 192.168.1.2/24

router bgp 65010
 bgp router-id 10.10.10.1
 neighbor 192.168.1.1 remote-as 65000
 network 192.168.1.0/24
end
write
\end{minted}

A \texttt{CE2}, quelcom similar (fent BGP amb \texttt{192.168.2.1}).

\subsection{Verificacions bàsiques}
Un cop fet tot això:

1. Comprovar l’estat de LDP a P1, PE1, PE2:
  \begin{minted}{text}
  show mpls ldp neighbor
  show mpls ldp bindings
  show mpls forwarding
  \end{minted}

  \item Comprovar la IGP (OSPF, IS-IS, etc.) per veure si hi ha rutes internes a la troncal.
  \begin{minted}{text}
  show ip ospf neighbor
  show ip route
  \end{minted}

  \item Comprovar BGP \emph{vpnv4} entre PE1 i PE2:
  \begin{minted}{text}
  show bgp vpnv4 summary
  show bgp vpnv4
  \end{minted}

  \item Comprovar BGP o OSPF entre CE i PE a cada VRF:
  \begin{minted}{text}
  show bgp ipv4 vrf CLIENTA summary
  show bgp ipv4 vrf CLIENTA
  show bgp ipv4 vrf CLIENTB summary
  \end{minted}

  \item Finalment, provar \texttt{ping} entre CE1 i CE2 (si la idea és que formin part d’una mateixa VPN) o verificar que cadascun arriba a la seva xarxa corresponent.
\end{enumerate}
