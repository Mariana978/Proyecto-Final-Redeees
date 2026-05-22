from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
import time
import threading

app = Flask(__name__)
CORS(app)

# Archivo donde vamos a guardar todo para que no se pierda al reiniciar
DATA_FILE = 'data.json'

def cargar_datos():
    # Si el archivo existe lo cargo, si no empiezo con todo vacio
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('nodos', {}), data.get('reglas', []), data.get('eventos', [])
    return {}, [], []

def guardar_datos():
    # Guardo todo en el archivo cada vez que hay un cambio
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'nodos': nodos, 'reglas': reglas, 'eventos': eventos}, f, indent=2, ensure_ascii=False)

def log(mensaje):
    # Guardo los logs en un archivo de texto con timestamp
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    linea = f"[{ts}] {mensaje}"
    print(linea)
    with open('logs.txt', 'a', encoding='utf-8') as f:
        f.write(linea + '\n')

# Cargo los datos al arrancar
nodos, reglas, eventos = cargar_datos()
log("Servidor iniciado")

def verificar_nodos_automatico():
    while True:
        time.sleep(5)
        ahora = datetime.now()
        cambios = False
        for nodo_id, info in nodos.items():
            ultima = datetime.fromisoformat(info['ultima_vez'])
            segundos = (ahora - ultima).total_seconds()
            estado_nuevo = 'activo' if segundos < 15 else 'inactivo'
            if info['estado'] != estado_nuevo:
                info['estado'] = estado_nuevo
                cambios = True
                log(f"Nodo {nodo_id} cambiado a {estado_nuevo}")
        if cambios:
            guardar_datos()

threading.Thread(target=verificar_nodos_automatico, daemon=True).start()

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.json
    nodo_id = data['id']
    nodos[nodo_id] = {
        'ip': data['ip'],
        'estado': 'activo',
        'ultima_vez': datetime.now().isoformat()
    }
    guardar_datos()
    log(f"Nodo conectado: {nodo_id} desde {data['ip']}")
    return jsonify({'ok': True})


@app.route('/nodos', methods=['GET'])
def ver_nodos():
    return jsonify(nodos)


@app.route('/heartbeat/<nodo_id>', methods=['POST'])
def heartbeat(nodo_id):
    # El cliente manda un heartbeat cada cierto tiempo para avisar que sigue vivo
    if nodo_id in nodos:
        nodos[nodo_id]['ultima_vez'] = datetime.now().isoformat()
        nodos[nodo_id]['estado'] = 'activo'
        guardar_datos()
    return jsonify({'ok': True})


@app.route('/verificar_nodos', methods=['GET'])
def verificar_nodos():
    # Reviso cuales nodos no han mandado heartbeat en los ultimos 15 segundos
    ahora = datetime.now()
    cambios = False
    for nodo_id, info in nodos.items():
        ultima = datetime.fromisoformat(info['ultima_vez'])
        segundos = (ahora - ultima).total_seconds()
        estado_nuevo = 'activo' if segundos < 15 else 'inactivo'
        if info['estado'] != estado_nuevo:
            info['estado'] = estado_nuevo
            cambios = True
            log(f"Nodo {nodo_id} marcado como {estado_nuevo}")
    if cambios:
        guardar_datos()
    return jsonify(nodos)


@app.route('/reglas', methods=['GET'])
def ver_reglas():
    return jsonify(reglas)


@app.route('/reglas', methods=['POST'])
def agregar_regla():
    regla = request.json
    regla['id'] = len(reglas) + 1
    regla['paquetes'] = 0
    campos = [
        'nombre', 'ingress_port', 'mac_src', 'mac_dst', 'eth_type',
        'vlan_id', 'vlan_prio', 'ip_origen', 'ip_destino', 'protocolo',
        'puerto_origen', 'puerto_destino', 'tos', 'accion', 'prioridad'
    ]
    for campo in campos:
        if campo not in regla:
            regla[campo] = None
    reglas.append(regla)
    reglas.sort(key=lambda r: r.get('prioridad', 0) or 0, reverse=True)
    guardar_datos()
    log(f"Regla agregada: {regla.get('nombre') or 'sin nombre'} | accion: {regla['accion']} | prioridad: {regla['prioridad']}")
    return jsonify({'ok': True, 'regla': regla})


@app.route('/reglas/vaciar', methods=['POST'])
def vaciar_reglas():
    reglas.clear()
    guardar_datos()
    log("Tabla de reglas vaciada")
    return jsonify({'ok': True})


@app.route('/evento', methods=['POST'])
def recibir_evento():
    evento = request.json
    evento['timestamp'] = datetime.now().isoformat()
    eventos.append(evento)
    regla_id = evento.get('regla_id')
    if regla_id:
        for r in reglas:
            if r.get('id') == regla_id:
                r['paquetes'] = r.get('paquetes', 0) + 1
                break
    guardar_datos()
    log(f"Evento de {evento.get('nodo')}: IP {evento.get('ip_origen')} puerto {evento.get('puerto')}")
    return jsonify({'ok': True})


@app.route('/eventos', methods=['GET'])
def ver_eventos():
    return jsonify(eventos)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)