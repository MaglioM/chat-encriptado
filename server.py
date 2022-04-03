import socket
import threading

HOST = '127.0.0.1'
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))

server.listen()

clients = []
keys = []

def handle(client):
    while True:
        message = client.recv(1024).decode('utf-8')
        if message == 'PUBLIC':#el emisor me está pidiendo la pública del receptor
            if clients.index(client) == 0:
                #envio al emisor la publica del receptor
                client.send(keys[1])
                #recibo del emisor, el mensaje encriptado con la publica del receptor
                encMessage = client.recv(1024)
                #le mando el mensaje encriptado al receptor
                clients[1].send(encMessage)
            else:#lo mismo para el otro cliente
                client.send(keys[0])
                encMessage = client.recv(1024)
                clients[0].send(encMessage)
            


def receive():
    while True:
        client, address = server.accept()
        print("Conectado a" + str(address))

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024)

        client.send("CLAVE".encode('utf-8'))
        key = client.recv(1024)

        clients.append(client)
        keys.append(key)
        
        print(f"\nEl nick del usuario es: {nickname.decode('utf-8')}")
        print(f"\nSu clave pública es:\n{key.decode()}")

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Servidor iniciado...")
receive()
