import tkinter as tk
from tkinter import Label, Entry, Button
import qrcode
from PIL import Image, ImageTk
import sqlite3
import os
import datetime

class GeneradorQRApp:
    def __init__(self, master):
        self.master = master
        master.title("Generador de Códigos QR")

        self.labels = [
            "Especie", "Cap Code", "Rim Profile", "Emboss",
            "Cover", "Continuous", "Couch", "Mem safe"
        ]

        self.entries = {}
        for label_text in self.labels:
            label = Label(master, text=f"{label_text}:")
            label.pack()
            entry = Entry(master)
            entry.pack()
            self.entries[label_text] = entry

        self.generate_button = Button(master, text="Generar y Guardar QR", command=self.generar_y_guardar)
        self.generate_button.pack()

        self.qr_label = Label(master)
        self.qr_label.pack()

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
