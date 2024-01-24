import tkinter as tk
from tkinter import Label
import cv2
import sqlite3
from threading import Thread
from datetime import datetime
from PIL import Image, ImageTk

class LectorQRApp:
    def __init__(self, master):
        self.master = master
        master.title("Lector de Códigos QR")

        # Widgets para mostrar información del QR
        self.labels = ["Specie", "CapCode", "Rim Profile", "Emboss", "Cover", "Continuous", "Couch", "Mem Safe"]
        self.label_widgets = {}
        for label_text in self.labels:
            label_widget = Label(master, text=f"{label_text}:")
            label_widget.pack()
            self.label_widgets[label_text] = label_widget

        # Widget para mostrar la vista previa de la cámara
        self.camera_label = Label(master)
        self.camera_label.pack()

        self.last_qr_code = None
        self.timer_label = Label(master, text="Timer: 0 seconds")
        self.timer_label.pack()

        self.capture_thread_stop = False  # Flag to signal the thread to stop
        self.capture_thread = Thread(target=self.leer_y_buscar_qr_thread, daemon=True)
        self.capture_thread.start()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def leer_y_buscar_qr_thread(self):
        cap = cv2.VideoCapture(0)
        while not self.capture_thread_stop:
            ret, frame = cap.read()
            if ret:
                self.show_frame(frame)
                decoded_object = self.detect_qr_code(frame)
                if decoded_object and decoded_object != self.last_qr_code:
                    self.process_qr_code(decoded_object)
            else:
                print("Error al capturar el marco de la cámara.")

        cap.release()

    def show_frame(self, frame):
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)
        self.camera_label.after(10, self.show_frame, frame)

    def detect_qr_code(self, frame):
        detector = cv2.QRCodeDetector()
        decoded_object, _, _ = detector.detectAndDecode(frame)
        if decoded_object:
            print("Identificador del código QR detectado:", decoded_object)
            return decoded_object
        return None

    def process_qr_code(self, decoded_object):
        self.last_qr_code = decoded_object
        self.start_timer()
        # Aquí puedes agregar el código para procesar el código QR detectado

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
        cv2.destroyAllWindows()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LectorQRApp(root)
    root.mainloop()