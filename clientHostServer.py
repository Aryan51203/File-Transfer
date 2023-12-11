import os
import socket
import threading
from tkinter import *
from tkinter import filedialog, messagebox

import customtkinter as ctk
import PIL.Image
import PIL.ImageTk
from CTkListbox import *

from Client import *
from Server import *

SIZE = 1024
FORMAT = "utf-8"
PORT = 4000


def hostHandler(frame, main_window, IP, client):
    def clientMessageHandler():
        while True:
            msg = client.recv(SIZE)
            if not msg:
                continue
            else:
                msg = removeExtraBytes(msg)
                cmd, msg = msg.decode(FORMAT).split("%")
                # print(cmd, msg)

                if cmd == "UPDATE":
                    availableFiles = eval(msg)
                    serverFilesVar.set(str(availableFiles))
                elif cmd == "TAKE_DATA":
                    fileName, packetCountResponse = eval(msg)

                    packetCountResponse = int(packetCountResponse)
                    folderpath = selectFolder()
                    filepath = os.path.join(folderpath, f"Received_{fileName}").replace(
                        "\\", "/"
                    )

                    with open(filepath, "wb") as f:
                        while packetCountResponse > 0:
                            data = client.recv(SIZE)
                            f.write(data)
                            packetCountResponse -= 1

    def downloadFile():
        filename = listbox2.get()
        s = convertToSIZE(f"DOWNLOAD%{filename}")
        client.send(s)

    def uploadFile():
        filepath = selectFile()

        filename = filepath.split("/")[-1]

        s = convertToSIZE(f"UPLOAD%{filename}")
        client.send(s)

        packetCount = getPacketCount(filepath)
        client.send(convertToSIZE(str(packetCount)))

        with open(filepath, "rb") as f:
            while packetCount > 0:
                data = f.read(SIZE)
                client.send(data)
                packetCount -= 1

    def deleteFile():
        filename = listbox2.get()

        if not filename:
            messagebox.showerror("ERROR", "No file selected")
        else:
            msg = f"DELETE%{filename}"
            client.send(convertToSIZE(msg))

        print("Deleting")

    def backButton():
        frame.destroy()
        main_window()

    clientListener = threading.Thread(target=clientMessageHandler)
    clientListener.start()

    availableFiles = [
        "EMPTY FOLDER",
    ]

    serverFilesVar = Variable(value=str(availableFiles))

    upload_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(os.path.join("Assets", "upload.png")).resize((20, 20))
    )
    download_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(os.path.join("Assets", "download.png")).resize((20, 20))
    )
    remove_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(os.path.join("Assets", "remove.png")).resize((20, 20))
    )
    back_image = PIL.ImageTk.PhotoImage(
        PIL.Image.open(os.path.join("Assets", "back.png")).resize((20, 20))
    )

    lb2 = ctk.CTkLabel(
        frame,
        text="FILES ON SERVER",
        font=("Comic Sans MS bold", 20),
        padx=5,
        pady=5,
    )
    lb2.place(x=400, y=20)

    x_coll = 800

    listbox2 = CTkListbox(frame, listvariable=serverFilesVar, width=600, height=400)
    listbox2.place(x=50, y=90)

    btn1 = ctk.CTkButton(
        master=frame,
        text="UPLOAD",
        font=("Comic Sans MS", 22),
        width=160,
        image=upload_image,
        command=uploadFile,
        compound=LEFT,
    )
    btn1.place(x=x_coll, y=190)

    btn2 = ctk.CTkButton(
        master=frame,
        text="DOWNLOAD",
        font=("Comic Sans MS", 22),
        width=160,
        image=download_image,
        command=downloadFile,
        compound=LEFT,
    )
    btn2.place(x=x_coll, y=260)

    btn3 = ctk.CTkButton(
        master=frame,
        text="DELETE",
        font=("Comic Sans MS", 22),
        width=160,
        image=remove_image,
        command=deleteFile,
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
