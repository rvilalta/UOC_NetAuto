## P4 tutorial ##

Install P4 compiler:
```console
$ source /etc/lsb-release
$ echo "deb http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${DISTRIB_RELEASE}/ /" | sudo tee /etc/apt/sources.list.d/home:p4lang.list
$ curl -fsSL https://download.opensuse.org/repositories/home:p4lang/xUbuntu_${DISTRIB_RELEASE}/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/home_p4lang.gpg > /dev/null
$ sudo apt-get update
$ sudo apt install p4lang-p4c
```

Compile P4 program:
```console
p4c-bm2-ss --arch v1model --std p4-16 simple_router.p4 -o simple_router.json
```

Run mininet topology:
```console
sudo python3 topo.py --json simple_router.json --behavioral-exe simple_switch --switch-config /dev/null --cli-message /dev/null
```

Inside mininet configure h1 and h2:
```console
h1 arp -i eth0 -s 10.0.1.10 00:04:00:00:00:00
h2 arp -i eth0 -s 10.0.0.10 00:04:00:00:00:01
h1 ping h2
```

Ping is not working. We need to configure our switch.
In another window, we run program to configure our P4 switch:
```console
simple_switch_CLI --thrift-port 9090
```

We run the following commands to our simple_switch_CLI window:
```console
table_add MyIngress.ipv4_lpm ipv4_forward 10.0.1.10/32 => 00:04:00:00:00:01 2
table_add MyIngress.ipv4_lpm ipv4_forward 10.0.0.10/32 => 00:04:00:00:00:00 1
```

PING IS RUNNING :-)
We can trace it, using:
```console
sudo tcpdump -i s1-eth1 -e -n
sudo tcpdump -i s1-eth2 -e -n
```
```
