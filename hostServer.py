import Server
import os
import socket
import threading
from tkinter import *
from tkinter import filedialog, messagebox

import customtkinter as ctk
from CTkListbox import *

import PIL.Image
import PIL.ImageTk
from Server import *

SIZE = 1024
FORMAT = "utf-8"
PORT = 4000

connFlag = [False, 0]


def serverLogWindow(frame, main_window, folderpath):
    # l=[f for f in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath, f))]
    l = []

    IP = socket.gethostbyname(socket.gethostname())
    ADDR = (IP, PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(ADDR)
    sock.listen()

    devicesConnectedVar = StringVar()
    devicesConnectedVar.set(f"Devices connected:{connFlag[1]}")

    serverLogs = []
    serverLogsVar = Variable(value=str(serverLogs))

    serverLogs.append("[STARTING] Server is starting...")
    serverLogsVar.set(str(serverLogs))

    print("Waiting for connection...")
    print(f"Share this code: {IP}")

    def checkChanges():
        l = []
        while True:
            new_l = [
                f
                for f in os.listdir(folderpath)
                if os.path.isfile(os.path.join(folderpath, f))
            ]

            if l != new_l:
                l = new_l
                msg = f"UPDATE%{str(new_l)}"
                # print(msg)
                server.send(convertToSIZE(msg))

    def serverHandler():
        while True:
            conn, addr = sock.accept()
            connFlag[0] = True

            if conn:
                serverConnected(conn, addr)

    def serverConnected(conn, addr):
        global server

        server = conn
        msg = "[NEW CLIENT] : HOST"
        # server.send(convertToSIZE(msg.encode(FORMAT)))
        server.send(msg.encode(FORMAT))

        serverLogs.append(f"[NEW CONNECTION]: {addr} Connected")
        serverLogsVar.set(str(serverLogs))

        clientThread = threading.Thread(target=clientHandlerHost, args=(server, addr))
        clientThread.start()

        connFlag[1] += 1
        devicesConnectedVar.set(f"Devices connected:{connFlag[1]}")

        if connFlag[1] == 1:
            checkChangeThread = threading.Thread(target=checkChanges)
            checkChangeThread.start()

    def clientHandlerHost(server, addr):
        new_l = [
            f
            for f in os.listdir(folderpath)
            if os.path.isfile(os.path.join(folderpath, f))
        ]

        msg = f"UPDATE%{str(new_l)}"
        # print(msg)
        server.send(convertToSIZE(msg))
        
        while True:
            msg = server.recv(SIZE)
            if not msg:
                continue
            else:
                msg = removeExtraBytes(msg).decode(FORMAT)

                cmd, msg = msg.split("%")

                if cmd == "DOWNLOAD":
                    filename = msg

                    filepath = os.path.join(folderpath, filename)
                    packetCount = getPacketCount(filepath)

                    fileData = f'["{filename}", "{packetCount}"]'

                    msgSend = f"TAKE_DATA%{fileData}"
                    server.send(convertToSIZE(msgSend))

                    with open(filepath, "rb") as f:
                        while packetCount > 0:
                            data = f.read(SIZE)
                            server.send(data)
                            packetCount -= 1

                elif cmd == "UPLOAD":
                    filename = msg
                    filepath = os.path.join(folderpath, filename).replace("\\", "/")

                    packetCountResponse = eval(
                        removeExtraBytes(server.recv(SIZE)).decode(FORMAT)
                    )

                    with open(filepath, "wb") as f:
                        while packetCountResponse > 0:
                            data = server.recv(SIZE)
                            f.write(data)
                            packetCountResponse -= 1

                elif cmd == "DELETE":
                    filename = msg
                    filepath = os.path.join(folderpath, filename).replace("\\", "/")

                    os.remove(filepath)
                    serverLogs.append(f"[DELETED]: {filename}")
                    serverLogsVar.set(str(serverLogs))
                                    
    def shutDownServerButton():
        frame.destroy()
        main_window()

    serverThread = threading.Thread(target=serverHandler)
    serverThread.start()

    lb1 = ctk.CTkLabel(
        frame,
        text="SERVER LOGS",
        font=("Comic Sans MS bold", 20),
        padx=5,
        pady=5,
    )
    lb1.pack()

    lb2 = ctk.CTkLabel(
        frame,
        text=f"Share this code to join: {IP}",
        font=("Comic Sans MS bold", 18),
        padx=5,
        pady=5,
    )
    lb2.place(x=10,y=50)

    lb3 = ctk.CTkLabel(
        frame,
        textvariable=devicesConnectedVar,
        font=("Comic Sans MS bold", 18),
        padx=5,
        pady=5,
    )
    lb3.place(x=790,y=50)

    listbox1 = CTkListbox(frame, listvariable=serverLogsVar, height=400,width=950)
    listbox1.place(x=10,y=100)

    btn1 = ctk.CTkButton(frame, text="Shut Down Server",command=shutDownServerButton)
    btn1.place(x=450,y=550)
