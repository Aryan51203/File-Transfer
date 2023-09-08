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

def getPacketCount(fpath):
    byte_size = os.stat(fpath).st_size
    packet_count = byte_size // SIZE

    if byte_size % SIZE:
        packet_count += 1

    return packet_count


def convertToSIZE(sen):
    sen = sen.encode(FORMAT)
    sen += b"\x00" * (SIZE - len(sen))
    return sen


def removeExtraBytes(sen):
    index = len(sen) - 1
    # print(index)
    # print(sen)
    while sen[index] == 0:
        # print(index)
        index -= 1

    sen = sen[: index + 1]
    return sen


def selectFile():
    root = Tk()
    root.attributes("-topmost", True)  # Display the dialog in the foreground.
    root.iconify()  # Hide the little window.
    fp = filedialog.askopenfilename()
    root.destroy()  # Destroy the root window when folder selected.
    return fp


def joinServer(frame, main_window, IP, sock):
    uploadedFiles = []

    def incomingMessageHandler():
        while True:
            msg = sock.recv(SIZE)
            if not msg:
                continue
            else:
                msg = removeExtraBytes(msg)
                msg = msg.decode(FORMAT)

                if msg == "UPLOAD/REMOVE":
                    global availableFiles
                    availableFiles = sock.recv(SIZE).decode(FORMAT)
                    serverFilesVar.set(availableFiles)
                    # print(availableFiles,'available files')

                elif msg == "DOWNLOAD":
                    filepath = sock.recv(SIZE).decode(FORMAT)

                    print(filepath)

                    s = "TAKE DATA"
                    s = convertToSIZE(s)
                    sock.send(s)

                    packetCount = getPacketCount(filepath)

                    filename = filepath.split("/")[-1]

                    fileData = f'["{filename}", "{packetCount}"]'

                    sock.send(convertToSIZE(fileData))

                    with open(filepath, "rb") as f:
                        while packetCount > 0:
                            data = f.read(SIZE)
                            if len(data) < SIZE:
                                data += b"\x00" * (SIZE - len(data))

                            sock.send(data)
                            packetCount -= 1

                        sock.send(b"\x00" * SIZE)

                elif msg == "TAKE DATA":
                    fileName, packetCountResponse = eval(
                        removeExtraBytes(sock.recv(SIZE)).decode(FORMAT)
                    )
                    packetCountResponse = int(packetCountResponse)
                    folderpath = selectFolder()
                    filepath = os.path.join(folderpath, f"Received_{fileName}").replace(
                        "\\", "/"
                    )

                    with open(filepath, "wb") as f:
                        data = b""
                        while True:
                            currData = sock.recv(SIZE)
                            if currData == b"\x00" * SIZE:
                                break
                            data += currData
                        data = removeExtraBytes(data)

                        f.write(data)

    def appendFilepath(fp):
        if len(uploadedFiles) > 0:
            if uploadedFiles[0] == "No File Uploaded":
                uploadedFiles[0] = fp
            else:
                uploadedFiles.append(fp)

        else:
            uploadedFiles.append(fp)

    def uploadFile(client):  # ORIGINAL
        filepath = selectFile()

        if not filepath:
            messagebox.showerror("ERROR", "No file selected")
        else:
            appendFilepath(filepath)

            clientFilesVar.set(str(uploadedFiles))

            # listbox1.insert('END',filepath)

            s = convertToSIZE("UPLOAD/REMOVE")
            client.send(s)
            client.send(str(uploadedFiles).encode(FORMAT))

    def downloadFile(client):
        filename = listbox2.get()
        # print(filename)

        s = convertToSIZE("DOWNLOAD")
        client.send(s)

        client.send(str(filename).encode(FORMAT))

    clientListener = threading.Thread(target=incomingMessageHandler)
    clientListener.start()

    def removeFile(client):
        filepath = listbox1.get()

        if not filepath:
            messagebox.showerror("ERROR", "No file selected")
        else:
            uploadedFiles.remove(filepath)
            clientFilesVar.set(str(uploadedFiles))

            s = convertToSIZE("UPLOAD/REMOVE")
            client.send(s)
            client.send(str(uploadedFiles).encode(FORMAT))

    def backButton():
        # sock.close()
        frame.destroy()
        main_window()

    availableFiles = '["No File to Download",]'
    uploadedFiles = ["No File Uploaded"]

    serverFilesVar = Variable(value=availableFiles)
    clientFilesVar = Variable(value=str(uploadedFiles))

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

    listbox1 = CTkListbox(frame, listvariable=clientFilesVar, width=300, height=400)
    listbox1.place(x=30, y=90)

    x_coll = 800

    listbox2 = CTkListbox(frame, listvariable=serverFilesVar, width=300, height=400)
    listbox2.place(x=425, y=90)

    btn1 = ctk.CTkButton(
        master=frame,
        text="UPLOAD",
        font=("Comic Sans MS", 22),
        width=160,
        command=lambda: uploadFile(sock),
        image=upload_image,
        compound=LEFT,
    )
    btn1.place(x=x_coll, y=190)

    btn2 = ctk.CTkButton(
        master=frame,
        text="DOWNLOAD",
        font=("Comic Sans MS", 22),
        width=160,
        command=lambda: downloadFile(sock),
        image=download_image,
        compound=LEFT,
    )
    btn2.place(x=x_coll, y=260)

    btn3 = ctk.CTkButton(
        master=frame,
        text="REMOVE",
        font=("Comic Sans MS", 22),
        width=160,
        command=lambda: removeFile(sock),
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
