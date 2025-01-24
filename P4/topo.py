#!/usr/bin/env python3

from mininet.net import Mininet
from mininet.node import RemoteController, Host
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import os

class SimpleP4Topo(Topo):
    def build(self):
        # Creem els dos hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        
        # Creem un switch de tipus "legacy" a Mininet per enganxar-ho a BMv2
        s1 = self.addSwitch('s1')  # aquest switch s'executa com a BMv2
        
        # Enllacem cada host al switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)

def run():
    topo = SimpleP4Topo()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Exemple de com afegir rutes (opcional)
    h1.cmd('ip route add default via 10.0.0.254')
    h2.cmd('ip route add default via 10.0.0.254')
    
    # Obrim la CLI per fer proves
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
