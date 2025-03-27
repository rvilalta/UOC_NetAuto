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
