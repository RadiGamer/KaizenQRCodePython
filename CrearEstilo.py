import tkinter as tk
from tkinter import ttk, Label, Entry, Button
import qrcode
from PIL import Image, ImageTk
import sqlite3
import os
import datetime

class GeneradorQRApp:
    def __init__(self, master):
        self.master = master
        master.title("Generador de Códigos QR")
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12))

        self.container_frame = ttk.Frame(master)
        self.container_frame.pack(expand=True, fill=tk.BOTH)

        self.logo_path = "logo.png"  
        self.logo_img = Image.open(self.logo_path)
        self.logo_img.thumbnail((200, 200))
        self.logo_img_tk = ImageTk.PhotoImage(self.logo_img)

        self.logo_label = ttk.Label(self.container_frame, image=self.logo_img_tk)
        self.logo_label.image = self.logo_img_tk
        self.logo_label.grid(row=0, column=1, padx=10, pady=10, sticky='ne')

        self.labels = [
            "Especie", "Cap Code", "Rim Profile", "Emboss",
            "Cover", "Continuous", "Couch", "Mem safe"
        ]

        self.entries = {}
        for row, label_text in enumerate(self.labels, start=1):
            label = ttk.Label(self.container_frame, text=f"{label_text}:")
            label.grid(row=row, column=0, padx=(0, 10), pady=5, sticky='e')
            entry = ttk.Entry(self.container_frame)
            entry.grid(row=row, column=1, pady=5, sticky='w')
            self.entries[label_text] = entry

        generate_button = ttk.Button(self.container_frame, text="Generar y Guardar QR", command=self.generar_y_guardar)
        generate_button.grid(row=len(self.labels) + 1, column=0, columnspan=2, pady=10)

        self.qr_label = ttk.Label(self.container_frame)
        self.qr_label.grid(row=len(self.labels) + 2, column=0, columnspan=2, pady=10)

    def generar_y_guardar_qr(self, datos):
        ahora = datetime.datetime.now()
        identificador = ahora.strftime('%Y%m%d%H%M%S')
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(identificador))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        carpeta_actual = ahora.strftime('%Y%m%d')
        if not os.path.exists(carpeta_actual):
            os.makedirs(carpeta_actual)

        nombre_archivo = f"{carpeta_actual}/codigo_qr_{identificador}.png"
        img.save(nombre_archivo)

        conn = sqlite3.connect("base_de_datos.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS codigos_qr (identificador TEXT PRIMARY KEY, datos TEXT, nombre_archivo TEXT)")
        cursor.execute("INSERT INTO codigos_qr (identificador, datos, nombre_archivo) VALUES (?, ?, ?)", (identificador, str(datos), nombre_archivo))
        conn.commit()
        conn.close()

        img_pil = Image.open(nombre_archivo)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.qr_label.config(image=img_tk)
        self.qr_label.image = img_tk

    def generar_y_guardar(self):
        datos = {label: entry.get() for label, entry in self.entries.items()}
        self.generar_y_guardar_qr(datos)
        print("Código QR generado y datos almacenados en la base de datos.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneradorQRApp(root)
    root.mainloop()
