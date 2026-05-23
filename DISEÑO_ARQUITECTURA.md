

## Separación de planos

| Plano | Componente | Rol |
|---|---|---|
| **Control** | `servidor.py` + `interfaz.html` | Almacena reglas, registra nodos, recibe eventos |
| **Datos** | `cliente.py` (×3) | Escucha tráfico, evalúa reglas, aplica acciones |
| **Pruebas** | `generador.py` | Produce tráfico UDP/TCP configurable |
| **Análisis** | `analizador.py` | Captura y estadística de tráfico con Scapy |


---

## Cómo se ven las reglas en nuestro proyecto

```mermaid
sequenceDiagram
    actor Op as Operador
    participant UI as interfaz.html
    participant SRV as servidor.py
    participant C1 as cliente-1
    participant GEN as generador.py

    Op->>UI: Llena formulario con la regla
    UI->>SRV: POST /reglas {ip, protocolo, puerto, acción, prioridad}
    SRV-->>UI: 200 OK — regla guardada y ordenada

    loop Cada 5 segundos
        C1->>SRV: GET /reglas
        SRV-->>C1: Lista ordenada por prioridad
        C1->>SRV: POST /heartbeat/cliente-1
        SRV-->>C1: 200 OK
    end

    GEN->>C1: Paquete UDP/TCP

    alt Coincide con regla BLOQUEAR
        C1->>C1: Descarta el paquete
        C1->>SRV: POST /evento {nodo, ip, puerto, regla_id}
    else Coincide con regla REPORTAR
        C1->>C1: Deja pasar el paquete
        C1->>SRV: POST /evento {nodo, ip, puerto, regla_id}
    else Coincide con regla PERMITIR
        C1->>C1: Deja pasar el paquete
    else Sin coincidencia
        C1->>C1: PERMITIR por defecto
    end

    UI->>SRV: GET /eventos
    SRV-->>UI: Lista de eventos con timestamps
```

---

## Pseudocódigo de lógica de prioridad

```mermaid
flowchart TD
    A["Llega un paquete"] --> B["Tomar lista de reglas\nordenada por prioridad"]
    B --> C{"¿Quedan\nreglas?"}
    C -->|No| D["PERMITIR\npor defecto"]
    C -->|Sí| E["Evaluar siguiente regla\nen la lista"]
    E --> F{"¿Todos los campos\ncoinciden?"}
    F -->|No| C
    F -->|Sí| G{"¿Cuál es\nla acción?"}
    G -->|PERMITIR| H["Dejar pasar\nel paquete"]
    G -->|BLOQUEAR| I["Descartar\nel paquete"]
    G -->|REPORTAR| J["Dejar pasar\n+ avisar al servidor"]
    G -->|MODIFICAR| K["Modificar\ny reenviar"]
```

---

## Gestión de nodos — heartbeat

```mermaid
stateDiagram-v2
    [*] --> Desconectado
    Desconectado --> Activo : POST /registrar
    Activo --> Activo : POST /heartbeat\n(cada 5s)
    Activo --> Inactivo : Sin heartbeat\npor más de 15s
    Inactivo --> Activo : POST /registrar\n(reconexión)
```

---

## Estructura de una regla

Cada regla tiene tres partes, igual que en OpenFlow real:

```mermaid
graph LR
    R["Regla"] --> M["Match\nCampos de coincidencia"]
    R --> A["Action\nQué hacer"]
    R --> P["Priority\nOrden de evaluación"]

    M --> M1["IP origen / destino"]
    M --> M2["Protocolo TCP / UDP"]
    M --> M3["Puerto origen / destino"]
    M --> M4["MAC origen / destino"]
    M --> M5["VLAN ID / prioridad"]
    M --> M6["EthType / ToS"]

    A --> A1["PERMITIR"]
    A --> A2["BLOQUEAR"]
    A --> A3["REPORTAR"]
    A --> A4["MODIFICAR"]
```

---

## Cumplimiento del enunciado

| Requisito | Implementación |
|---|---|
| Registrar clientes | `POST /registrar` → guarda en `data.json` |
| Lista de nodos con estado | `GET /nodos`.  id, IP, estado, última conexión |
| Detectar nodos caídos | automático PORQUE revisa heartbeat cada 5s |
| Almacenar y distribuir reglas | `POST /reglas` y `GET /reglas` ordenadas por prioridad |
| Recibir eventos de clientes | `POST /evento`, guarda con timestamp |
| Logs y evidencia | `logs.txt` con timestamp en cada operación |
| Persistencia | `data.json` |
| Cliente replicable | Mismo `cliente.py` en todos los PCs, solo cambia `config.json` |
| Evaluación de tráfico | `evaluar_paquete()`, primera coincidencia por prioridad gana |
| Acciones obligatorias | PERMITIR, BLOQUEAR y REPORTAR implementadas y probadas |
| Generador configurable | `--ip --puerto --cantidad --intervalo --mensaje --protocolo` |
| Interfaz de administración | Tabla de flujo, interpretación automática, pseudo-OpenFlow |
| Analizador de tráfico | Scapy — captura real, estadísticas cada 10 segundos |

---


**¿Por qué Flask y no FastAPI?**  
Flask es muuucho más fácil y directo. El código es más
legible y fácil de explicarle al profe. 

**¿Por qué HTTP/REST y no OpenFlow real?**  
OpenFlow requiere switches físicos compatibles. HTTP/REST permite demostrar
los mismos conceptos de separación de planos sobre cualquier red WiFi o
Ethernet sin hardware especializado.

**¿Por qué configuración separada del código?**  
Para cumplir el principio de replicabilidad SDN. El mismo `cliente.py` corre
en todos los PCs, solo cambia `config.json`. Esto demuestra que el sistema
escala a N clientes sin modificar código.
