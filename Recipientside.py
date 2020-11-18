import math
import os
import socket
import time
import tkinter as tk
from tkinter import messagebox, filedialog

import numpy as np

LARGE_FONT= ("Verdana", 12)

GAP = "<line_break>"
MB = int(math.pow(2, 20))
chunk = int(math.pow(2, 30))
GB = int(math.pow(2, 30))

class Page(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


def wchunk(client, cno, csize, savename):
    pkt = bytearray()
    while len(pkt) < csize:
        recvfile = client.recv(csize - len(pkt))
        if not recvfile:
            raise Exception(f"chunk {cno} not fully received.")
        pkt += recvfile
    np.array(bytes(pkt)).tofile(open(savename, 'ab+'))
    return


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        l_title=tk.Label(self, text="TCP File Recipient Daemon",
                         font="Arial,12")
        l_title.grid(row=0,column=0,columnspan=3, sticky="NSEW",padx=30,pady=30)

        label_username = tk.Label(self, text="Username")
        label_password = tk.Label(self, text="Password")

        entry_username = tk.Entry(self,show="*")

        entry_password = tk.Entry(self, show="*")

        label_username.grid(row=2, column=0, sticky='NSEW',padx=10,pady=10)
        label_password.grid(row=3, column=0, sticky='NSEW',padx=10,pady=10)
        entry_username.grid(row=2, column=1,sticky='NSEW',padx=10,pady=10)
        entry_password.grid(row=3, column=1,sticky='NSEW',padx=10,pady=10)

        checkbox = tk.Checkbutton(self, text="Keep me logged in")
        checkbox.grid(row=4, column=1,sticky='NSEW',padx=10,pady=10)

        logbtn = tk.Button(self, text="Login", bg="GREEN", fg="White",command=lambda: login_btn_clicked())
        logbtn.grid(row=5, column=1,sticky='NSEW', padx=10, pady=10)

        def login_btn_clicked():
            # print("Clicked")
            username = entry_username.get()
            password = entry_password.get()

            if len(username) and len(password) > 2:

                if username == "admin" and password == "admin":
                    controller.show_frame(PageOne)
                # display a message if username and password is incorrect!
                else:
                    messagebox.showinfo(self,"Invalid username or password ! ")

            else:
                messagebox.showinfo(self,"Enter Username and Password")


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        clock = tk.Label(self, font=('times', 18, 'bold'), bg='green',fg="white")
        clock.grid(row=0,column=2, sticky="NSNESWSE",padx=8,pady=8)



        def tick():
            time2=time.strftime('%H:%M:%S')
            clock.config(text=time2)
            clock.after(200,tick)
        tick()

        label = tk.Label(self, text="TCP RECIPIENT DAEMON", font="Arial,16",bg="black",fg="White")
        label.grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="NSNESWSE")

        l_host=tk.Label(self,text="Enter Host NAME")
        l_host.grid(row=1, column=0, padx=8, pady=8, sticky="NSNESWSE")


        e_host=tk.Entry(self)
        e_host.grid(row=1, column=1, columnspan=2, padx=8, pady=8, sticky="NSNESWSE")
        e_host.insert(tk.END,'127.0.0.1')


        l_port=tk.Label(self,text="Enter Port")
        l_port.grid(row=2, column=0, padx=8, pady=8, sticky="NSNESWSE")

        e_port=tk.Entry(self)
        e_port.grid(row=2, column=1, columnspan=2, padx=8, pady=8, sticky="NSNESWSE")
        e_port.insert(tk.END,12121)

        message_label =tk.Label(self,text="Log:",font=("Arial,12"))
        message_label.grid(row=3,column=0,columnspan=3,padx=10,pady=10,sticky="NSEW")


        scrollbar_y = tk.Scrollbar(self)
        scrollbar_y.grid(row=4, column=3,rowspan=6)

        show_1=tk.Text(self,height=8, width=35, yscrollcommand=scrollbar_y.set,
                       bg="BLACK",fg="GREEN")
        show_1.grid(row=4, column=0,rowspan=3,columnspan=3,sticky="NSEW")

        b_connect=tk.Button(self,text=" Receive",command=lambda: my_server())
        b_connect.grid(row=14,column=0,padx=10,pady=10,sticky="nsew")
        #
        # e_data=tk.Entry(self)
        # e_data.grid(row=14,column=1,padx=10,pady=10,sticky="nsew")

        def my_server():
            # e_data_v = e_data.get()
            host = e_host.get()
            port = int(e_port.get())

            HOST, PORT = host, port
            # data  = e_data_v

                # Create a socket (SOCK_STREAM means a TCP socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Connect to server and send data
                s.connect((HOST, PORT))
                # s.sendall(bytes(data + "\n", "utf-8"))
                GAP = "<line_break>"

                data = s.recv(4096).decode()
                filename, file_size, ftype = data.split(GAP)
                filename = os.path.basename(filename)
                file_size = int(file_size)
                num = (file_size//chunk)+1
                savename = filedialog.asksaveasfilename(initialdir='/', title=f"Save {filename} as",
                                                        filetypes=(('all files', '*.*'), ('jpeg files','*.jpg'), ('mp4 files','*.mp4'),
                                                                   ))
                curr = 0
                show_1.insert(tk.END, f'Downloading...........\n')
                if file_size > GB:

                    while curr < num:
                        s.send('READY'.encode())
                        cid, chunk_size = s.recv(1024).decode().split(GAP)
                        chunk_size = int(chunk_size)
                        n = int(cid)
                        wchunk(s, n, chunk_size, savename)
                        curr += 1

                else:
                    # show_1.insert(tk.END, f'Downloading...........\n')
                    with open(savename, 'a+b') as f:
                        tot = 0
                        while tot < file_size:
                            recvfile = s.recv(MB)
                            if not recvfile:
                                break
                            f.write(recvfile)
                            tot += len(recvfile)
            show_1.insert(tk.END,f'{filename} received and saved as {os.path.basename(savename)}.')
            s.close()










app = Page()
app.mainloop()
