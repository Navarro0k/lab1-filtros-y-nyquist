import threading
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from lab_controller import LabController

class LabGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Laboratorio DSP")
        self.root.geometry("800x600")
        self.controller = LabController()
        self.canvas = None

        # --- Interfaz ---
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Duración (s):").grid(row=0, column=0)
        self.ent_dur = tk.Entry(frame, width=8)
        self.ent_dur.insert(0, "5")
        self.ent_dur.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="M (Filtro):").grid(row=0, column=2)
        self.ent_m = tk.Entry(frame, width=8)
        self.ent_m.insert(0, "5")
        self.ent_m.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Nueva fs:").grid(row=0, column=4)
        self.ent_fs = tk.Entry(frame, width=8)
        self.ent_fs.insert(0, "8000")
        self.ent_fs.grid(row=0, column=5, padx=5)

        self.btn_grabar = tk.Button(frame, text="Grabar", command=self.hilo_grabar)
        self.btn_grabar.grid(row=1, column=0, pady=10)

        self.combo = ttk.Combobox(frame, values=["Media Movil", "Nyquist (remuestreo)"], state="readonly")
        self.combo.current(0)
        self.combo.grid(row=1, column=1, columnspan=2)

        self.btn_analizar = tk.Button(frame, text="Analizar", command=self.hilo_analizar)
        self.btn_analizar.grid(row=1, column=3)

        self.btn_rep_orig = tk.Button(frame, text="Rep. Original", command=self.hilo_reproducir_orig)
        self.btn_rep_orig.grid(row=1, column=4, padx=5)

        self.btn_rep_filt = tk.Button(frame, text="Rep. Analizado", command=self.hilo_reproducir_filt)
        self.btn_rep_filt.grid(row=1, column=5)

        self.frame_grafica = tk.Frame(root)
        self.frame_grafica.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Lanzadores (Crean un hilo para no congelar la ventana)
    # ------------------------------------------------------------------
    def hilo_grabar(self):
        threading.Thread(target=self.tarea_grabar, daemon=True).start()

    def hilo_analizar(self):
        threading.Thread(target=self.tarea_analizar, daemon=True).start()

    def hilo_reproducir_orig(self):
        threading.Thread(target=self.tarea_reproducir_orig, daemon=True).start()

    def hilo_reproducir_filt(self):
        threading.Thread(target=self.tarea_reproducir_filt, daemon=True).start()

    # ------------------------------------------------------------------
    # Tareas (Ejecutan el controlador y muestran resultados o errores)
    # ------------------------------------------------------------------
    def tarea_grabar(self):
        try:
            duracion = float(self.ent_dur.get())
            self.controller.grabar(duracion)
            self.root.after(0, messagebox.showinfo, "Éxito", "Grabación completa.")
        except Exception as error:
            self.root.after(0, messagebox.showerror, "Error", str(error))

    def tarea_analizar(self):
        try:
            tipo = self.combo.get()
            parametro = int(self.ent_m.get()) if tipo == "Media Movil" else int(self.ent_fs.get())
            
            resultado = self.controller.analizar(tipo, parametro)
            figura = resultado if tipo == "Media Movil" else resultado[0]
            
            self.root.after(0, self.dibujar_grafica, figura)
        except Exception as error:
            self.root.after(0, messagebox.showerror, "Error", str(error))

    def tarea_reproducir_orig(self):
        try:
            self.controller.reproducir_original()
        except Exception as error:
            self.root.after(0, messagebox.showerror, "Error", str(error))

    def tarea_reproducir_filt(self):
        try:
            self.controller.reproducir_filtrado(self.combo.get())
        except Exception as error:
            self.root.after(0, messagebox.showerror, "Error", str(error))


    def dibujar_grafica(self, fig):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = LabGUI(root)
    root.mainloop()