from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from CTkListbox import *

import customtkinter as ctk
from PIL import Image, ImageTk


def serverLogWindow(frame, main_window, folderpath):
    dirPathHosted = StringVar()
    devicesConnected = StringVar()
    dirPathHosted.set("Folder hosted: "+folderpath)
    devicesConnected.set("Devices connected: 0")

    lb1 = ctk.CTkLabel(
        frame,
        text="SERVER LOGS",
        font=("Comic Sans MS bold", 34),
        padx=5,
        pady=5,
    )
    lb1.pack()

    lb2 = ctk.CTkLabel(
        frame,
        textvariable=dirPathHosted,
        font=("Comic Sans MS bold", 34),
        padx=5,
        pady=5,
    )
    lb2.pack()

    lb3 = ctk.CTkLabel(
        frame,
        textvariable=devicesConnected,
        font=("Comic Sans MS bold", 34),
        padx=5,
        pady=5,
    )
    lb3.pack()

    serverLogs = []
    serverLogsVar = Variable(value=str(serverLogs))

    listbox1 = CTkListbox(frame, listvariable=serverLogsVar, width=300, height=400)
    listbox1.pack()