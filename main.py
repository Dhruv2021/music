import socket
import threading
import tkinter as tk
from tkinter import filedialog
from plyer import notification  # Install the plyer library using: pip install plyer

HOST = '127.0.0.1'
PORT = 6000

class MusicSharingClient:
    def __init__(self):
        self.username = ""
        self.client_socket = None
        self.connected = False

        self.name_window = tk.Tk()
        self.name_window.title("Enter Your Username")

        self.username_entry = tk.Entry(self.name_window, width=30)
        self.username_entry.pack(pady=10)

        self.connect_button = tk.Button(self.name_window, text="Connect", command=self.connect_and_start)
        self.connect_button.pack(pady=10)

        self.chat_window = None  # Reference to the chat window
        self.file_name_label = None
        self.send_button = None

        self.name_window.mainloop()

    def connect_and_start(self):
        self.username = self.username_entry.get().strip()
        if self.username:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.username.encode('utf-8'))

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            self.connected = True
            self.name_window.destroy()  # Close the name window
            self.setup_gui()

            notification.notify(
                title='Music Sharing App',
                message=f"{self.username} joined the chat!",
                app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
                timeout=10,
            )

    def setup_gui(self):
        if not self.connected:
            return

        self.chat_window = tk.Tk()
        self.chat_window.title(f"Music Sharing Chat - {self.username}")

        self.message_frame = tk.Frame(self.chat_window)
        self.message_frame.pack(pady=10)

        self.message_entry = tk.Entry(self.message_frame, width=50)
        self.message_entry.grid(row=0, column=0, padx=10)
        self.message_entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.message_frame, text="Send", command=self.send_message, state=tk.NORMAL)
        self.send_button.grid(row=0, column=1)

        self.file_frame = tk.Frame(self.chat_window)
        self.file_frame.pack(pady=10)

        self.attach_button = tk.Button(self.file_frame, text="Attach File", command=self.attach_file)
        self.attach_button.grid(row=0, column=0)

        self.file_name_label = tk.Label(self.file_frame, text="")
        self.file_name_label.grid(row=0, column=1)

        self.send_file_button = tk.Button(self.file_frame, text="Send File", command=self.send_file, state=tk.DISABLED)
        self.send_file_button.grid(row=0, column=2)

    def send_message(self, event=None):
        if not self.connected:
            return
        message = self.message_entry.get()
        self.client_socket.send(message.encode('utf-8'))
        self.message_entry.delete(0, tk.END)

    def attach_file(self):
        if not self.connected:
            return
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_data = open(file_path, 'rb').read()
            self.file_name = file_path.split("/")[-1]
            self.file_name_label.config(text=f"Attached: {self.file_name}")
            self.send_button.config(state=tk.DISABLED)
            self.send_file_button.config(state=tk.NORMAL)

    def send_file(self):
        if not self.connected:
            return
        try:
            self.client_socket.send(self.file_name.encode('utf-8'))
            self.client_socket.send(self.file_data)
            print(f"File '{self.file_name}' sent successfully.")
            self.file_name_label.config(text=f"Download File: {self.file_name}")
            self.send_button.config(state=tk.NORMAL)
            self.send_file_button.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error sending file: {e}")

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                if "sent a file:" in data:
                    file_name = data.split(':')[1].strip()
                    self.file_name_label.config(text=f"Download File: {file_name}")
                else:
                    print(data)
            except ConnectionResetError:
                print("Connection reset by the server.")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break


if __name__ == "__main__":
    client = MusicSharingClient()
