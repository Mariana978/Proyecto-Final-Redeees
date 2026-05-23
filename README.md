# Proyecto final de Redes de Computadores — Universidad del Rosario

Matemáticas Aplicadas y Ciencias de la Computación

**Mariana Álvarez y Sofía Aponte**

---

## ¿Qué es esto?

Implementamos una red basada en SDN,

donde un servidor controla las reglas de tráfico y las distribuye a varios clientes

en la red. Los clientes miran el tráfico que reciben y deciden si permitirlo, bloquearlo

o reportarlo al servidor, todo según las reglas que el servidor les manda.

Pues según lo que vimos en clase, básicamente es un firewall donde las reglas se crean desde una interfaz

web y se aplican automáticamente en todos los computadores de la red.

---

## Componentes

| Archivo | Para qué sirve |
|---|---|
| `servidor.py` | Guarda reglas, registra clientes y recibe eventos |
| `cliente.py` | Se instala en cada PC. Escucha tráfico y aplica las reglas |
| `generador.py` | Manda paquetes UDP o TCP para probar que las reglas funcionan |
| `interfaz.html` | Panel web para crear y visualizar reglas en tiempo real |
| `analizador.py` | Captura y analiza el tráfico de la red con Scapy |
| `config_clienteX.json` | Configuración de cada cliente — solo esto cambia entre PCs |

---

## Cómo correrlo en un solo PC (para pruebas)

### 1. Instalar dependencias

pip install flask flask-cors requests scapy

### 2. Abrir 5 terminales y en cada una entrar a la carpeta

cd Desktop/proyecto_sdn/prueba_un_pc

### 3. Terminal 1 — Servidor

python servidor.py

### 4. Terminal 2, 3 y 4 — Clientes

python cliente.py config_cliente1.json

python cliente.py config_cliente2.json

python cliente.py config_cliente3.json

### 5. Abrir la interfaz

Hacer doble clic en interfaz.html

### 6. Terminal 5 — Generador (para probar reglas)

python generador.py --ip 127.0.0.1 --puerto 9001 --cantidad 5

### 7. Analizador (requiere abrir terminal como administrador)

python analizador.py

---

## Cómo correrlo en varios PCs (para nuestra presentación)

Usar la carpeta prueba\_varios\_pcs/. Ver el archivo INSTRUCCIONES.txt dentro de esa carpeta.

En resumen:

1. Todos los PCs conectados a la misma red WiFi

2. Correr ipconfig en el PC servidor y anotar la IP

3. En cada PC cliente crear config.json con esa IP y un nodo\_id distinto

4. Actualizar la línea const SERVIDOR en interfaz.html con esa IP

5. Correr el servidor, luego los clientes

---

## Pruebas implementadas

| Prueba | Regla |
|---|---|
| Permitir UDP | protocolo=UDP, puerto=9001, acción=PERMITIR, prioridad=5 |
| Bloquear UDP | protocolo=UDP, puerto=9001, acción=BLOQUEAR, prioridad=10 |
| Bloquear por IP | ip_origen=127.0.0.1, acción=BLOQUEAR, prioridad=5 |
| Reportar al controlador | acción=REPORTAR, prioridad=20 |
| Conflicto de prioridad | Dos reglas mismo flujo — gana la de mayor prioridad |


---

## Arquitectura

[Interfaz Web] ←→ [Servidor controlador]

↓ ↓ ↓

[Cliente 1] [Cliente 2] [Cliente 3]

↑

[Generador de tráfico]

---

## Tecnologías usadas

- Python 3.11

- Flask + Flask-CORS (servidor)

- Sockets UDP/TCP (cliente y generador)

- Scapy (analizador)

- HTML + CSS + JavaScript (interfaz)
