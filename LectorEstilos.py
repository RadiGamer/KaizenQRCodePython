import tkinter as tk
from tkinter import Label
import cv2
import sqlite3
from PIL import Image, ImageTk
from threading import Thread
from datetime import datetime

class LectorQRApp:
    def __init__(self, master):
        self.master = master
        master.title("Lector de Códigos QR")

        self.labels = ["Specie", "CapCode", "Rim Profile", "Emboss", "Cover", "Continuous", "Couch", "Mem Safe"]

        # Set row and column weights to make labels take up more space
        for i in range(len(self.labels) * 2 + 1):  # *2 for data, +1 for the timer label
            master.grid_rowconfigure(i, weight=1)

        # Calculate the number of columns needed to divide the screen
        num_columns = (len(self.labels) + 2) // 3  # Add 2 to ensure it's rounded up

        # Set column weights for dividing the screen
        for i in range(num_columns * 2):  # *2 for label and data
            master.grid_columnconfigure(i, weight=1)

        self.label_widgets = {}
        for row, label_text in enumerate(self.labels):
            col = (row % 3) * 2  # Adjusted to ensure correct alignment
            label_widget = Label(master, text=f"{label_text}:", font=("Arial", 16, "bold"))
            label_widget.grid(row=row * 2, column=col, sticky='w', padx=10, pady=10)
            self.label_widgets[label_text] = label_widget

            data_widget = Label(master, text="", font=("Arial", 12))
            data_widget.grid(row=row * 2 + 1, column=col, sticky='w', padx=10, pady=10)
            self.label_widgets[f"{label_text}_data"] = data_widget

        self.last_qr_code = None
        self.timer_label = Label(master, text="Timer: 0 seconds", font=("Arial", 16, "bold"))
        self.timer_label.grid(row=len(self.labels) * 2, column=0, columnspan=num_columns * 2, sticky='w', padx=10, pady=10)

        self.capture_thread_stop = False  # Flag to signal the thread to stop
        self.capture_thread = Thread(target=self.leer_y_buscar_qr_thread, daemon=True)
        self.capture_thread.start()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def leer_y_buscar_qr_thread(self):
        cap = cv2.VideoCapture(0)

        while not self.capture_thread_stop:
            ret, frame = cap.read()

            if not ret:
                print("Error al capturar el marco de la cámara.")
                continue

            detector = cv2.QRCodeDetector()
            decoded_object, _, _ = detector.detectAndDecode(frame)

            if decoded_object:
                print("Identificador del código QR:")
                print(decoded_object)

                if decoded_object != self.last_qr_code:
                    self.last_qr_code = decoded_object
                    self.start_timer()

                    conn = sqlite3.connect("base_de_datos.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT datos FROM codigos_qr WHERE identificador=?", (decoded_object,))
                    resultado = cursor.fetchone()

                    if resultado:
                        print("¡Código QR encontrado en la base de datos!")
                        datos = resultado[0].split(",")  # Suponiendo que los datos están separados por comas

                        for label, dato in zip(self.labels, datos):
                            campo, valor = dato.strip().split(":")
                            self.label_widgets[label].config(text=f"{label}:")
                            self.label_widgets[f"{label}_data"].config(text=valor.strip())  # Fix here

                    else:
                        print("Código QR no encontrado en la base de datos.")

                    conn.close()

        cap.release()

    def start_timer(self):
        self.start_time = datetime.now()
        self.update_timer()

    def update_timer(self):
        elapsed_time = datetime.now() - self.start_time
        self.timer_label.config(text=f"Timer: {elapsed_time.seconds} seconds")
        self.master.after(1000, self.update_timer)

    def on_closing(self):
        self.capture_thread_stop = True
        self.capture_thread.join()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LectorQRApp(root)
    root.mainloop()
