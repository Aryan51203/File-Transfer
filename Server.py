import os
import socket
import threading
from tkinter import *
from tkinter import filedialog

SIZE = 1024
FORMAT = "utf-8"
PORT = 4000
DISCONNECT_MESSAGE = "!Disconnect!"


def convertToSIZE(sen):
    sen = sen.encode(FORMAT)
    sen += b"\x00" * (SIZE - len(sen))
    return sen


def removeExtraBytes(sen):
    index = len(sen) - 1

    while sen[index] == 0:
        index -= 1

    sen = sen[: index + 1]
    return sen


def getPacketCount(fpath):
    byte_size = os.stat(fpath).st_size
    packet_count = byte_size // SIZE

    if byte_size % SIZE:
        packet_count += 1

    return packet_count


def selectFile():
    root = Tk()
    root.attributes("-topmost", True)  # Display the dialog in the foreground.
    root.iconify()  # Hide the little window.
    fp = filedialog.askopenfilename()
    root.destroy()  # Destroy the root window when folder selected.
    return fp


def selectFolder():
    root = Tk()
    root.attributes("-topmost", True)  # Display the dialog in the foreground.
    root.iconify()  # Hide the little window.
    fp = filedialog.askdirectory()
    root.destroy()  # Destroy the root window when folder selected.
    return fp


def startServer(handle_Client_Function):
    IP = socket.gethostbyname(socket.gethostname())
    ADDR = (IP, PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(ADDR)
    sock.listen()
    print("Waiting for connection...")
    print(f"Share this code: {IP}")

    while True:
        conn, addr = sock.accept()

        thread = threading.Thread(target=handle_Client_Function, args=(conn, addr))
        thread.start()

        print(f"[ACTIVE CONNECTIONS] : {threading.active_count()-1}")
