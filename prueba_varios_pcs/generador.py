import socket
import time
import argparse

# Recibo los parametros por consola para no tener que editar el codigo cada vez
parser = argparse.ArgumentParser()
parser.add_argument('--ip',        default='127.0.0.1',  help='IP destino')
parser.add_argument('--puerto',    type=int, default=9001, help='Puerto destino')
parser.add_argument('--cantidad',  type=int, default=5,   help='Cuantos paquetes enviar')
parser.add_argument('--intervalo', type=float, default=1.0, help='Segundos entre cada envio')
parser.add_argument('--mensaje',   default='hola',        help='Mensaje a enviar')
parser.add_argument('--protocolo', default='UDP',         help='UDP o TCP')
args = parser.parse_args()

print(f"Enviando {args.cantidad} paquetes {args.protocolo} a {args.ip}:{args.puerto}")
print("-" * 40)

if args.protocolo.upper() == 'UDP':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in range(args.cantidad):
        sock.sendto(args.mensaje.encode(), (args.ip, args.puerto))
        print(f"  [{i+1}/{args.cantidad}] Paquete UDP enviado")
        time.sleep(args.intervalo)

elif args.protocolo.upper() == 'TCP':
    for i in range(args.cantidad):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((args.ip, args.puerto))
            sock.send(args.mensaje.encode())
            sock.close()
            print(f"  [{i+1}/{args.cantidad}] Paquete TCP enviado")
        except Exception as e:
            print(f"  [{i+1}/{args.cantidad}] Error: {e}")
        time.sleep(args.intervalo)

print("-" * 40)
print("Listo.")