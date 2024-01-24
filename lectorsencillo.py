import tkinter as tk
from tkinter import Label
import cv2
import sqlite3
from PIL import Image, ImageTk

class LectorQRApp:
    def __init__(self, master):
        self.master = master
        master.title("Lector de Códigos QR")

        self.labels = ["Specie", "CapCode", "Rim Profile", "Emboss", "Cover", "Continuous", "Couch", "Mem Safe"]

        self.label_widgets = {}
        for label_text in self.labels:
            label_widget = Label(master, text=f"{label_text}:")
            label_widget.pack()
            self.label_widgets[label_text] = label_widget

        self.leer_y_buscar_qr()

    def leer_y_buscar_qr(self):
        ret, frame = cv2.VideoCapture(0).read()

        if not ret:
            print("Error al capturar el marco de la cámara.")
            self.master.after(10, self.leer_y_buscar_qr)
            return

        detector = cv2.QRCodeDetector()
        decoded_object, _, _ = detector.detectAndDecode(frame)

        if decoded_object:
            print("Identificador del código QR:")
            print(decoded_object)

            # Buscar datos en la base de datos
            conn = sqlite3.connect("base_de_datos.db")
            cursor = conn.cursor()
            cursor.execute("SELECT datos FROM codigos_qr WHERE identificador=?", (decoded_object,))
            resultado = cursor.fetchone()

            if resultado:
                print("¡Código QR encontrado en la base de datos!")
                datos = resultado[0].split(",")  # Suponiendo que los datos están separados por comas

                # Actualizar etiquetas con datos encontrados
                for label, dato in zip(self.labels, datos):
                    campo, valor = dato.strip().split(":")
                    self.label_widgets[label].config(text=f"{label}: {dato.strip()}")

            else:
                print("Código QR no encontrado en la base de datos.")

            conn.close()

        self.master.after(10, self.leer_y_buscar_qr)

if __name__ == "__main__":
    root = tk.Tk()
    app = LectorQRApp(root)
    root.mainloop()
