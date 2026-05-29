import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 12345

def recibir_mensajes(sock):
    """Hilo dedicado exclusivamente a escuchar lo que llega del servidor."""
    while True:
        try:
            data = sock.recv(1024).decode("utf-8")
            if not data:
                print("\n[SISTEMA] Conexión cerrada por el servidor.")
                break
            
            # --- CORRECCIÓN AQUÍ ---
            # Imprimimos el mensaje que llega limpiando la línea actual (\r) 
            # pero SIN agregar la etiqueta "Cliente: " manualmente.
            sys.stdout.write("\r" + data + "\n")
            sys.stdout.flush()
        except:
            break
    print("\nHilo de recepción finalizado.")


try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        
        # 1. Primer mensaje del servidor (Pide autenticación)
        print(s.recv(1024).decode("utf-8"), end="")
        
        # 2. Enviar el nombre de usuario para autenticarse
        username = input()
        s.sendall(username.encode("utf-8"))
        
        # 3. Recibir confirmación de bienvenida
        print(s.recv(1024).decode("utf-8"))

        # 4. Encender el hilo de recepción de mensajes grupales
        hilo_recibir = threading.Thread(target=recibir_mensajes, args=(s,), daemon=True)
        hilo_recibir.start()

        # 5. Bucle principal del teclado (Envío)
        try:
            while True:
                mensaje = input("Cliente: ")
                if mensaje == "/":
                    break
                if not mensaje.strip():
                    continue
                s.sendall(mensaje.encode("utf-8"))
                
        except KeyboardInterrupt:
            # Captura el Ctrl + C de forma limpia y evita el mensaje rojo
            print("\n\n[SISTEMA] Saliendo del chat de forma segura...")

except ConnectionRefusedError:
    print("Error: No se pudo conectar al servidor.")

print("Has salido del chat.")
