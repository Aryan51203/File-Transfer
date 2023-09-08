import os
import socket
import threading
from tkinter import *
from tkinter import filedialog, messagebox

import customtkinter as ctk
from CTkListbox import *

import PIL.Image
import PIL.ImageTk

from Client import *
from Server import *

SIZE = 1024
FORMAT = "utf-8"
PORT = 4000

connFlag = [
    False,
]


def convertToSIZE(sen):
    sen = sen.encode(FORMAT)
    sen += b"\x00" * (SIZE - len(sen))
    return sen


def removeExtraBytes(sen):
    flag=False
  
    # print(sen)
    index = len(sen) - 1
    while sen[index] == 0:
        # print(sen[index])
        index -= 1
        
    sen = sen[: index + 1]
    return sen


def createServer(frame, main_window):
    uploadedFiles = []

    IP = socket.gethostbyname(socket.gethostname())
    ADDR = (IP, PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(ADDR)
    sock.listen()
    print("Waiting for connection...")
    print(f"Share this code: {IP}")

    def serverHandler():
        while True:
            conn, addr = sock.accept()
            connFlag[0] = True

            if conn:
                serverConnected(conn)
                break

    serverThread = threading.Thread(target=serverHandler)
    serverThread.start()

    def incomingMessageHandler():
        while True:
            msg = server.recv(SIZE)

            if not msg:
                continue
            else:
                msg = removeExtraBytes(msg)
                msg = msg.decode(FORMAT)

                if msg == "UPLOAD/REMOVE":
                    global availableFiles
                    availableFiles = server.recv(SIZE).decode(FORMAT)
                    clientFilesVar.set(availableFiles)
                    print(availableFiles, "available files")

                elif msg == "DOWNLOAD":
                    filepath = server.recv(SIZE).decode(FORMAT)

                    print(filepath)

                    s = "TAKE DATA"
                    s = convertToSIZE(s)
                    server.send(s)

                    packetCount = getPacketCount(filepath)

                    filename = filepath.split("/")[-1]

                    fileData = f'["{filename}", "{packetCount}"]'

                    server.send(convertToSIZE(fileData))

                    with open(filepath, "rb") as f:
                        while packetCount > 0:
                            data = f.read(SIZE)
                            if len(data) < SIZE:
                                data += b"\x00" * (SIZE - len(data))

                            server.send(data)
                            packetCount -= 1

                        server.send(b"\x00" * SIZE)

                elif msg == "TAKE DATA":
                    fileName, packetCountResponse = eval(
                        removeExtraBytes(server.recv(SIZE)).decode(FORMAT)
                    )
                    packetCountResponse = int(packetCountResponse)
                    folderpath = selectFolder()
                    filepath = os.path.join(folderpath, f"Received_{fileName}").replace(
                        "\\", "/"
                    )

                    with open(filepath, "wb") as f:
                        data = b""
                        while True:
                            currData = server.recv(SIZE)
                            if currData == b"\x00" * SIZE:
                                break
                            data += currData
                        # print(data)
                        data= data[:-1024] + removeExtraBytes(data[-1024:])

                        f.write(data)

    def serverConnected(conn):
        global server
        server = conn
        connectedFlag.set("Connected")
        lb1.configure(bg_color="green")

        serverListener = threading.Thread(target=incomingMessageHandler)
        serverListener.start()

    def appendFilepath(fp):
        if len(uploadedFiles) > 0:
            if uploadedFiles[0] == "No File Uploaded":
                uploadedFiles[0] = fp
            else:
                uploadedFiles.append(fp)

        else:
            uploadedFiles.append(fp)

    def uploadFile():  # ORIGINAL
        if not connFlag[0]:
            messagebox.showerror("ERROR", "No file selected")
        else:
            filepath = selectFile()

            if not filepath:
                messagebox.showerror("ERROR", "No file selected")
            else:
                appendFilepath(filepath)

                serverFilesVar.set(str(uploadedFiles))

                s = convertToSIZE("UPLOAD/REMOVE")
                server.send(s)
                server.send(str(uploadedFiles).encode(FORMAT))

    def downloadFile():  # ORIGINAL
        if not connFlag[0]:
            messagebox.showerror("ERROR", "No file selected")
        else:
            filename = listbox2.get()
            if not filename:
                messagebox.showerror("ERROR", "No file selected")
            else:
                s = convertToSIZE("DOWNLOAD")
                server.send(s)
                server.send(str(filename).encode(FORMAT))

    def removeFile():
        filepath = listbox1.get()

        if not filepath:
            messagebox.showerror("ERROR", "No file selected")
        else:
            uploadedFiles.remove(filepath)
            serverFilesVar.set(str(uploadedFiles))

            s = convertToSIZE("UPLOAD/REMOVE")

            server.send(s)
            server.send(str(uploadedFiles).encode(FORMAT))

    def backButton():
        # if connFlag[0]==False:
        #     sock.close()
        # else:
        #     server.close()
        frame.destroy()
        main_window()

    availableFiles = '["No File to Download",]'
    clientFilesVar = Variable(value=availableFiles)

    uploadedFiles = ["No File Uploaded"]
    serverFilesVar = Variable(value=str(uploadedFiles))

    upload_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(r"Assets\upload.png").resize((20, 20))
    )
    download_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(r"Assets\download2.png").resize(
            (20, 20)
        )
    )
    remove_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(r"Assets\remove.png").resize((20, 20))
    )
    back_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(r"Assets\back.png").resize((20, 20))
    )

    connectedFlag = StringVar()
    connectedFlag.set("Not Connected")

    lb3Str = f"Share this code with anyone you want to connect to: {IP}"

    lb1 = ctk.CTkLabel(
        frame, text="UPLOADED FILES", font=("Comic Sans MS bold", 20), padx=5, pady=5
    )
    lb1.place(x=40, y=20)
    lb2 = ctk.CTkLabel(
        frame,
        text="FILES AVAILABLE FOR DOWNLOAD",
        font=("Comic Sans MS bold", 20),
        padx=5,
        pady=5,
    )
    lb2.place(x=400, y=20)

    lb3 = ctk.CTkLabel(
        frame, text=lb3Str, font=("Comic Sans MS bold", 14), padx=5, pady=5
    )
    lb3.place(x=400, y=550)

    listbox1 = CTkListbox(frame, listvariable=serverFilesVar, width=300, height=400)
    listbox1.place(x=30, y=90)

    x_coll = 800

    listbox2 = CTkListbox(frame, listvariable=clientFilesVar, width=300, height=400)
    listbox2.place(x=425, y=90)

    lb1 = ctk.CTkLabel(
        frame,
        textvariable=connectedFlag,
        font=("Comic Sans MS bold", 22),
        padx=5,
        pady=5,
        width=160,
        bg_color="Red",
    )
    lb1.place(x=x_coll, y=100)

    btn1 = ctk.CTkButton(
        master=frame,
        text="UPLOAD",
        font=("Comic Sans MS", 22),
        width=160,
        command=uploadFile,
        image=upload_image,
        compound=LEFT,
    )
    btn1.place(x=x_coll, y=190)

    btn2 = ctk.CTkButton(
        master=frame,
        text="DOWNLOAD",
        font=("Comic Sans MS", 22),
        width=160,
        command=downloadFile,
        image=download_image,
        compound=LEFT,
    )
    btn2.place(x=x_coll, y=260)

    btn3 = ctk.CTkButton(
        master=frame,
        text="REMOVE",
        font=("Comic Sans MS", 22),
        width=160,
        command=removeFile,
        image=remove_image,
        compound=LEFT,
    )
    btn3.place(x=x_coll, y=330)

    btn3 = ctk.CTkButton(
        master=frame,
        text="BACK",
        font=("Comic Sans MS", 22),
        width=160,
        command=backButton,
        image=back_image,
        compound=LEFT,
    )
    btn3.place(x=x_coll, y=400)
