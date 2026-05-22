import socket
import requests
import json
import threading
import time
import sys

# Leo el archivo de configuracion que le paso por argumento
config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
with open(config_file) as f:
    cfg = json.load(f)

SERVER = f"http://{cfg['servidor_ip']}:{cfg['servidor_puerto']}"
reglas_locales = []


def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def registrarse():
    ip = get_ip_local()
    try:
        requests.post(f"{SERVER}/registrar", json={
            'id': cfg['nodo_id'],
            'ip': ip
        })
        print(f"[{cfg['nodo_id']}] Registrado. Mi IP es {ip}")
    except Exception as e:
        print(f"[{cfg['nodo_id']}] No pude registrarme: {e}")


def mandar_heartbeat():
    # Cada 5 segundos le aviso al servidor que sigo vivo
    while True:
        try:
            requests.post(f"{SERVER}/heartbeat/{cfg['nodo_id']}", timeout=3)
        except:
            pass
        time.sleep(5)


def actualizar_reglas():
    global reglas_locales
    while True:
        try:
            r = requests.get(f"{SERVER}/reglas")
            reglas_locales = r.json()
            print(f"[{cfg['nodo_id']}] Tengo {len(reglas_locales)} reglas activas")
        except Exception as e:
            print(f"[{cfg['nodo_id']}] Error al pedir reglas: {e}")
        time.sleep(cfg['intervalo_consulta'])


def evaluar_paquete(ip_origen, protocolo, puerto_destino):
    for regla in reglas_locales:
        coincide = True
        if regla.get('ip_origen') and regla['ip_origen'] != ip_origen:
            coincide = False
        if regla.get('protocolo') and regla['protocolo'].upper() != protocolo.upper():
            coincide = False
        if regla.get('puerto_destino') and str(regla['puerto_destino']) != str(puerto_destino):
            coincide = False
        if coincide:
            accion = regla['accion'].upper()
            print(f"[{cfg['nodo_id']}] Regla {regla['id']} aplicada -> {accion}")
            if accion == 'REPORTAR':
                try:
                    requests.post(f"{SERVER}/evento", json={
                        'nodo': cfg['nodo_id'],
                        'ip_origen': ip_origen,
                        'puerto': puerto_destino,
                        'regla_id': regla['id']
                    })
                except:
                    pass
            return accion
    return 'PERMITIR'


def escuchar_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', cfg['escuchar_puerto']))
    print(f"[{cfg['nodo_id']}] Escuchando UDP en puerto {cfg['escuchar_puerto']}...")
    while True:
        data, addr = sock.recvfrom(1024)
        ip_origen = addr[0]
        accion = evaluar_paquete(ip_origen, 'UDP', cfg['escuchar_puerto'])
        if accion == 'BLOQUEAR':
            print(f"[{cfg['nodo_id']}] BLOQUEADO paquete de {ip_origen}")
        elif accion == 'REPORTAR':
            print(f"[{cfg['nodo_id']}] REPORTADO paquete de {ip_origen} al servidor")
        else:
            print(f"[{cfg['nodo_id']}] PERMITIDO mensaje de {ip_origen}: {data.decode(errors='ignore')}")


# Arranco todo
registrarse()
threading.Thread(target=mandar_heartbeat, daemon=True).start()
threading.Thread(target=actualizar_reglas, daemon=True).start()
escuchar_udp()