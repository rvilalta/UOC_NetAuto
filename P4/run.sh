#!/bin/bash

# 1. Compilar el programa P4
p4c-bm2-ss --arch v1model \
           --std p4-16 \
           simple_router.p4 \
           -o simple_router.json

if [ $? -ne 0 ]; then
    echo "Error: la compilacio de simple_router.p4 ha fallat."
    exit 1
fi

echo "Compilacio completada. Fitxer generat: simple_router.json"

# 2. Desplegar el switch de BMv2 en segon pla amb la config resultant
#    Com a exemple, l'executem manualment.
simple_switch --log-console \
              --no-p4 \
              simple_router.json \
              &

BMV2_PID=$!

echo "BMv2 switch (PID: $BMV2_PID)."

# 3. Executar Mininet amb la nostra topologia
sudo python3 topo.py

# 4. Quan sortim de Mininet, tanquem BMv2
echo "Aturant BMv2..."
kill $BMV2_PID
