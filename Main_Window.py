from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageTk
from Client import connectToServer

import createServer
import joinServer
import hostServer
import clientHostServer

SIZE = 1024
FORMAT = "utf-8"


def selectFolder(inp):
    root = Tk()
    root.attributes("-topmost", True)  # Display the dialog in the foreground.
    root.iconify()  # Hide the little window.
    fp = filedialog.askdirectory()
    root.destroy()  # Destroy the root window when folder selected.

    inp.set(fp)


def main_frame():
    frame = ctk.CTkFrame(master=window)
    frame.pack(fill="both", expand=1)

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
        command=lambda: Send_Frame(frame),
        compound=BOTTOM,
    )
    btn1.place(x=250, y=200)

    btn2 = ctk.CTkButton(
        master=frame,
        text="JOIN A SERVER",
        image=join_image,
        font=("Comic Sans MS", 22),
        command=lambda: Join_Frame(frame),
        compound=BOTTOM,
    )
    btn2.place(x=550, y=200)

    btn3 = ctk.CTkButton(
        master=frame,
        text="H0ST A FILE OR FOLDER",
        font=("Comic Sans MS", 22),
        command=lambda: Host_Frame(frame),
    )
    btn3.place(x=650, y=250)

    btn4 = ctk.CTkButton(
        master=frame, text="EXIT", font=("Comic Sans MS", 22), command=window.destroy
    )
    btn4.place(x=425, y=500)


def Send_Frame(main_frame_delete):
    main_frame_delete.destroy()
    frame1 = ctk.CTkFrame(master=window)
    frame1.pack(fill="both", expand=1)
    createServer.createServer(frame1, main_frame)


def Join_Frame(main_frame_delete):
    dialog = ctk.CTkInputDialog(
        text="Enter code to connect to server:", title="Connect to server"
    )
    inpIP = dialog.get_input()

    if inpIP:
        sock = connectToServer(inpIP)

        if not sock:
            messagebox.showerror("Error", "Server not found")
        else:
            msg = sock.recv(SIZE).decode(FORMAT)

            if msg == "[NEW CLIENT] : HOST":
                main_frame_delete.destroy()
                frame1 = ctk.CTkFrame(master=window)
                frame1.pack(fill="both", expand=1)
                clientHostServer.hostHandler(frame1, main_frame, inpIP, sock)

            elif msg == "ONE_ONE_SERVER":
                main_frame_delete.destroy()
                frame1 = ctk.CTkFrame(master=window)
                frame1.pack(fill="both", expand=1)
                joinServer.joinServer(frame1, main_frame, inpIP, sock)
            else:
                print("Error, Something went wrong")


def Host_Frame(main_frame_delete):
    def createHost():
        root.destroy()
        main_frame_delete.destroy()
        frame1 = ctk.CTkFrame(master=window)
        frame1.pack(fill="both", expand=1)
        fp = inputGot.get()
        hostServer.serverLogWindow(frame1, main_frame, fp)

    root = ctk.CTkToplevel(window)
    root.geometry("400x400")
    root.title("Host Server")

    lb1 = ctk.CTkLabel(
        root,
        text="Create Server",
        font=("Comic Sans MS bold", 34),
        padx=5,
        pady=5,
    )
    lb1.pack()

    inputGot = StringVar()
    inp1 = ctk.CTkEntry(master=root, textvariable=inputGot)
    inp1.pack()

    btn1 = ctk.CTkButton(
        master=root,
        text="BROWSE",
        font=("Comic Sans MS", 22),
        command=lambda: selectFolder(inputGot),
        # compound=BOTTOM,
    )
    btn1.pack()

    btn2 = ctk.CTkButton(
        master=root,
        text="CREATE",
        font=("Comic Sans MS", 22),
        command=createHost,
        # compound=BOTTOM,
    )
    btn2.pack()

    btn3 = ctk.CTkButton(
        master=root,
        text="CANCEL",
        font=("Comic Sans MS", 22),
        command=root.destroy,
        # compound=BOTTOM,
    )
    btn3.pack()

    root.mainloop()


window = ctk.CTk()
server_image = ImageTk.PhotoImage(
    Image.open(r"Assets\server_image.png").resize((200, 200))
)
join_image = ImageTk.PhotoImage(Image.open(r"Assets\join.png").resize((200, 200)))

window.title("File Transfer")
window.resizable(0, 0)
# window.state('zoomed')
window.geometry("1000x600+700+200")

main_frame()
window.mainloop()
