import socket
import rsa
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT = 9090

class Client:
    def __init__(self,host,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))

        msg = tkinter.Tk()
        msg.withdraw()

        #genero el juego de llaves para el cliente
        self.publicKey, self.privateKey = rsa.newkeys(1024)

        self.nickname = simpledialog.askstring("Nickname", "Elija su nombre", parent=msg)
        
        self.guiDone = False

        self.running = True
        
        guiThread = threading.Thread(target=self.guiLoop)
        receiveThread = threading.Thread(target=self.receive)

        guiThread.start()
        receiveThread.start()

    def guiLoop(self):
        self.win = tkinter.Tk()
        self.win.title(f'Chat cifrado - {self.nickname}')
        self.win.configure(bg='lightgrey')

        self.chatLabel = tkinter.Label(self.win, text='Chat:', bg = 'lightgrey')
        self.chatLabel.config(font=("Roboto",12))
        self.chatLabel.pack(padx=20,pady=5)

        self.textArea = tkinter.scrolledtext.ScrolledText(self.win)
        self.textArea.pack(padx=20,pady=5)
        self.textArea.config(state='disabled')

        self.msgLabel = tkinter.Label(self.win, text='Escribí tu mensaje:', bg = 'lightgrey')
        self.msgLabel.config(font=("Roboto",12))
        self.msgLabel.pack(padx=20,pady=5)
        
        self.inputArea = tkinter.Text(self.win, height=3)
        self.inputArea.pack(padx=20,pady=5)

        self.sendButton = tkinter.Button(self.win, text="Enviar", command=self.writeThread)
        self.sendButton.config(font=('Roboto', 12))
        self.sendButton.pack(padx=20,pady=5)

        self.guiDone= True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def writeThread(self):
        writeThread = threading.Thread(target=self.write)
        writeThread.start()

    def write(self):
        message = f"{self.nickname} dice: {self.inputArea.get('1.0','end')}"
        #pedir la publica del receptor
        self.sock.send("PUBLIC".encode('utf-8'))
        receiverPublicKey = rsa.PublicKey.load_pkcs1(self.sock.recv(1024))
        #encriptar mensaje con la publica del receptor antes de mandarlo
        encryptedMessage = rsa.encrypt(message.encode('utf-8'),receiverPublicKey)
        print(f"\nEste es el mensaje encriptado:\n{encryptedMessage}")
        self.sock.send(encryptedMessage)
        self.inputArea.delete('1.0','end')
        #imprimo mi mensaje en mi pantalla
        self.textArea.config(state='normal')
        self.textArea.insert('end',message)
        self.textArea.yview('end')
        self.textArea.config(state='disabled')
        
    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)


    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024)
                try:
                    if message.decode() == "NICK":#el servidor me pide mi nick
                       self.sock.send(self.nickname.encode('utf-8'))
                    elif message.decode() == "CLAVE":#el servidor me pide mi pública
                       self.sock.send(self.publicKey.save_pkcs1())
                except:#si no lo puede decodear, es un mensaje encriptado del otro cliente, por eso el except
                    #lo desencripto con mi privada
                    decMessage = rsa.decrypt(message, self.privateKey).decode()
                    #imprimo en pantalla el mensaje recibido
                    self.textArea.config(state='normal')
                    self.textArea.insert('end',decMessage)
                    self.textArea.yview('end')
                    self.textArea.config(state='disabled')
            except ConnectionAbortedError:
                break


client = Client(HOST,PORT)

