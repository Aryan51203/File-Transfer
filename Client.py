import os
import socket
import threading
from tkinter import *
from tkinter import filedialog

SIZE = 1024
FORMAT = "utf-8"
PORT = 4000
DISCONNECT_MESSAGE = "!Disconnect!"

def connectToServer(IP):

    ADDR = (IP, PORT)
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:

        sock.connect(ADDR)
        print("Connect")
        
        return sock

    except Exception as e:
        print(e)
        print("Failed to connect to server")
