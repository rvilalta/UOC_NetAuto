#!/bin/sh

# Exemple de regles iptables senzilles
# Esborrem regles anteriors
iptables -F
iptables -X

# Politica per defecte: acceptar
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Bloquegem transit entrant al port 80
iptables -A INPUT -p tcp --dport 80 -j DROP

# Permetem transit entrant al port 443
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# (Afegir regles segons necessitats)
echo "Regles iptables aplicades amb exit."

# Mantenim el contenidor actiu
tail -f /dev/null

