from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import os

import customtkinter as ctk
from PIL import Image
import views.create_screen as CreateServer


def create_main_screen(frame):
    server_image = ctk.CTkImage(
        light_image=Image.open(os.path.join("Assets", "server_image.png")),
        size=(200, 200),
    )

    join_image = ctk.CTkImage(
        light_image=Image.open(os.path.join("Assets", "join.png")), size=(200, 200)
    )

    host_image = ctk.CTkImage(
        light_image=Image.open(os.path.join("Assets", "host.jpg")), size=(200, 200)
    )

    lb1 = ctk.CTkLabel(
        frame,
        text="FILE TRANSFER SYSTEM",
        font=("Comic Sans MS bold", 34),
        padx=5,
        pady=5,
    )
    lb1.place(x=275, y=75)

    btn1 = ctk.CTkButton(
        master=frame,
        text="CREATE A SERVER",
        image=server_image,
        font=("Comic Sans MS", 22),
        command=lambda: CreateServer.create_createServer_screen(frame),
        compound=BOTTOM,
    )
    btn1.place(x=150, y=200)

    btn2 = ctk.CTkButton(
        master=frame,
        text="JOIN A SERVER",
        image=join_image,
        font=("Comic Sans MS", 22),
        command=lambda: Join_Frame(frame),
        compound=BOTTOM,
    )
    btn2.place(x=400, y=200)

    btn3 = ctk.CTkButton(
        master=frame,
        text="H0ST A FOLDER",
        image=host_image,
        font=("Comic Sans MS", 22),
        command=lambda: Host_Frame(frame),
        compound=BOTTOM,
    )
    btn3.place(x=650, y=200)

    btn4 = ctk.CTkButton(
        master=frame, text="EXIT", font=("Comic Sans MS", 22), command=window.destroy
    )
    btn4.place(x=425, y=500)


window = ctk.CTk()
window.title("File Transfer")
# window.resizable(0, 0)
window.geometry("1000x600+700+200")

frame1 = ctk.CTkFrame(master=window)
frame1.pack(fill="both", expand=1)

create_main_screen(frame1)

window.mainloop()
