from scapy.all import sniff, IP, TCP, UDP
from collections import defaultdict
from datetime import datetime
import time
import threading

# Aqui guardo las estadisticas de lo que capturo
conteo_ips = defaultdict(int)
conteo_puertos = defaultdict(int)
conteo_protocolos = defaultdict(int)
total_paquetes = 0
inicio = datetime.now()

def procesar_paquete(paquete):
    global total_paquetes

    # Solo me interesan paquetes IP
    if not paquete.haslayer(IP):
        return

    total_paquetes += 1
    ip_origen = paquete[IP].src
    ip_destino = paquete[IP].dst

    # Cuento por IP origen
    conteo_ips[ip_origen] += 1

    # Detecto si es TCP o UDP y cuento el puerto destino
    if paquete.haslayer(UDP):
        conteo_protocolos['UDP'] += 1
        puerto = paquete[UDP].dport
        conteo_puertos[f'UDP:{puerto}'] += 1

    elif paquete.haslayer(TCP):
        conteo_protocolos['TCP'] += 1
        puerto = paquete[TCP].dport
        conteo_puertos[f'TCP:{puerto}'] += 1

    # Muestro cada paquete en tiempo real
    proto = 'UDP' if paquete.haslayer(UDP) else 'TCP' if paquete.haslayer(TCP) else 'OTRO'
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {proto} | {ip_origen} -> {ip_destino}")


def mostrar_estadisticas():
    # Cada 10 segundos muestro un resumen
    while True:
        time.sleep(10)
        duracion = (datetime.now() - inicio).seconds
        print("\n" + "="*50)
        print(f"  RESUMEN - {duracion}s de captura | {total_paquetes} paquetes totales")
        print("="*50)

        print("\n  Top IPs origen:")
        for ip, n in sorted(conteo_ips.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {ip}: {n} paquetes")

        print("\n  Protocolos:")
        for proto, n in conteo_protocolos.items():
            print(f"    {proto}: {n} paquetes")

        print("\n  Top puertos:")
        for puerto, n in sorted(conteo_puertos.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {puerto}: {n} paquetes")

        print("="*50 + "\n")


# Arranco el hilo de estadisticas en paralelo
threading.Thread(target=mostrar_estadisticas, daemon=True).start()

print("Analizador de trafico iniciado...")
print("Capturando paquetes UDP y TCP en la red...")
print("Resumen cada 10 segundos. Ctrl+C para parar.\n")

# Capturo todo el trafico de la red
# filter='udp or tcp' para solo capturar lo relevante
sniff(filter='udp or tcp', prn=procesar_paquete, store=False)