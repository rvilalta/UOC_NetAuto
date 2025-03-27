# Exemple de CNF: Firewall amb iptables

En aquest exemple proposarem una CNF que faci tasques de *firewall* utilitzant **iptables**. L'objectiu és veure com podem encapsular regles de seguretat dins un contenidor i executar-les en un *pod* de Kubernetes amb privilegis suficients per manipular la taula de filtrat.

---

## Estructura de fitxers

Crearem una estructura similar a:

```plaintext
firewall-cnf/
-- Dockerfile
-- scripts/
    -- firewall.sh
-- k8s/
    -- deployment.yaml
    -- service.yaml
```

## Script de configuració de firewall (firewall.sh)
Podem definir un script molt bàsic que afegeixi algunes regles iptables. Per exemple, bloquejar el port 80 i permetre només el port 443.
```
#!/bin/sh

# Exemple de regles iptables senzilles
# Esborrem regles anteriors
iptables -F
iptables -X

# Politica per defecte: acceptar
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Bloquegem trànsit entrant al port 80
iptables -A INPUT -p tcp --dport 80 -j DROP

# Permetem trànsit entrant al port 443
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# (Afegir regles segons necessitats)
echo "Regles iptables aplicades amb exit."

# Mantenim el contenidor actiu
tail -f /dev/null
```

## Dockerfile
Creem un Dockerfile que instal·li la utilitat iptables, copiï l’script i l'executi en engegar el contenidor:
```
FROM ubuntu:22.04

# iptables
RUN apt-get update && \
    apt-get install -y iptables && \
    apt-get clean

# Copiem l'script de firewall
COPY scripts/firewall.sh /usr/local/bin/firewall.sh
RUN chmod +x /usr/local/bin/firewall.sh

# Executem l'script
CMD ["/usr/local/bin/firewall.sh"]
```


