import threading
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from audio_io import AudioIO
from core.moving_average_filter import MovingAverageFilter
from core.nyquist_analyzer import NyquistAnalyzer
from plotter import SignalPlotter
from lab_controller import LabController


class LabGUI:
    """Ventana principal del laboratorio simplificada y desacoplada."""

    OPCIONES_FILTRO = {
        "Media Movil": LabController.TIPO_MEDIA_MOVIL,
        "Nyquist (remuestreo)": LabController.TIPO_NYQUIST,
    }

    def __init__(self, root: tk.Tk, controller: LabController = None):
        self.root = root
        self.root.title("Lab 1 - DSP: Media Movil y Nyquist")
        self.root.geometry("880x750")
        self.controller = controller or LabController()
        self._canvas_widget = None

        self._construir_interfaz()

    def _construir_interfaz(self):
        # --- Panel Superior (Controles consolidados) ---
        panel = ttk.Frame(self.root, padding=10)
        panel.pack(fill="x")

        # Fila 0: Parámetros de entrada (Solo los solicitados)
        ttk.Label(panel, text="Duración (s):").grid(row=0, column=0, sticky="e", padx=5)
        self.ent_dur = ttk.Entry(panel, width=8)
        self.ent_dur.insert(0, str(LabController.DURACION_POR_DEFECTO))
        self.ent_dur.grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(panel, text="M (Filtro):").grid(row=0, column=2, sticky="e", padx=5)
        self.ent_m = ttk.Entry(panel, width=8)
        self.ent_m.insert(0, str(LabController.M_POR_DEFECTO))
        self.ent_m.grid(row=0, column=3, sticky="w", pady=2)

        ttk.Label(panel, text="Nueva fs (Nyquist):").grid(row=0, column=4, sticky="e", padx=5)
        self.ent_newfs = ttk.Entry(panel, width=8)
        self.ent_newfs.insert(0, str(LabController.NEW_FS_POR_DEFECTO))
        self.ent_newfs.grid(row=0, column=5, sticky="w", pady=2)

        # Fila 1: Botones de Acción y Select
        acciones = ttk.Frame(panel)
        acciones.grid(row=1, column=0, columnspan=6, pady=15)

        self.btn_grabar = ttk.Button(acciones, text="Grabar", command=self._cmd_grabar)
        self.btn_grabar.pack(side="left", padx=5)

        ttk.Separator(acciones, orient="vertical").pack(side="left", fill="y", padx=10)

        # Select para elegir qué analizar / reproducir
        self.combo_analisis = ttk.Combobox(acciones, values=list(self.OPCIONES_FILTRO.keys()), state="readonly", width=18)
        self.combo_analisis.current(0)
        self.combo_analisis.pack(side="left", padx=5)

        self.btn_analizar = ttk.Button(acciones, text="Analizar", command=self._cmd_analizar, state="disabled")
        self.btn_analizar.pack(side="left", padx=5)

        ttk.Separator(acciones, orient="vertical").pack(side="left", fill="y", padx=10)

        self.btn_rep_orig = ttk.Button(acciones, text="Reproducir Original", command=self._cmd_rep_orig, state="disabled")
        self.btn_rep_orig.pack(side="left", padx=5)

        self.btn_rep_analizado = ttk.Button(acciones, text="Reproducir Analizado", command=self._cmd_rep_analizado, state="disabled")
        self.btn_rep_analizado.pack(side="left", padx=5)

        # --- Estado y Gráfica ---
        self.lbl_estado = ttk.Label(self.root, text="Listo.", foreground="gray")
        self.lbl_estado.pack(fill="x", padx=10)

        self.frame_grafica = ttk.Frame(self.root)
        self.frame_grafica.pack(fill="both", expand=True, padx=10, pady=10)

    # ------------------------------------------------------------------
    # Lógica de tareas asíncronas
    # ------------------------------------------------------------------
    def _ejecutar_tarea(self, mensaje: str, tarea_func, callback_func):
        self._set_estado(mensaje)
        
        for btn in (self.btn_grabar, self.btn_analizar, self.btn_rep_orig, self.btn_rep_analizado):
            btn.config(state="disabled")

        def worker():
            try:
                resultado = tarea_func()
                error = None
            except Exception as e:
                resultado, error = None, e
            self.root.after(0, lambda: callback_func(resultado, error))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------
    def _cmd_grabar(self):
        try:
            dur = float(self.ent_dur.get())
            self.controller.configurar(duration=dur)
        except ValueError:
            return messagebox.showerror("Error", "Duración inválida.")

        self._ejecutar_tarea(
            f"Grabando {dur}s...",
            tarea_func=self.controller.grabar,
            callback_func=self._cb_grabar
        )

    def _cb_grabar(self, simulado, error):
        if error:
            messagebox.showerror("Error", str(error))
            self._set_estado("Error al grabar.")
        else:
            self._set_estado("Grabación completa.", color="green")
        self._actualizar_botones()

    def _cmd_analizar(self):
        opcion = self.combo_analisis.get()
        
        if opcion == "Media Movil":
            try:
                self.controller.configurar(M=int(self.ent_m.get()))
            except ValueError:
                return messagebox.showerror("Error", "El valor M debe ser entero.")
            
            self._ejecutar_tarea("Aplicando Media Móvil...", self.controller.analizar_media_movil, self._cb_analisis_mm)
            
        elif opcion == "Nyquist (remuestreo)":
            try:
                nfs = int(self.ent_newfs.get())
            except ValueError:
                return messagebox.showerror("Error", "Nueva fs inválida.")
            
            # Se usa el default del controlador para f_max
            fmax = LabController.F_MAX_POR_DEFECTO
            self._ejecutar_tarea(
                "Analizando Nyquist...", 
                tarea_func=lambda: self.controller.analizar_nyquist(fmax, nfs), 
                callback_func=self._cb_nyquist
            )

    def _cb_analisis_mm(self, fig, error):
        if error:
            messagebox.showerror("Error", str(error))
        else:
            self._mostrar_figura(fig)
            self._set_estado("Análisis Media Móvil completado.", "green")
        self._actualizar_botones()

    def _cb_nyquist(self, resultado, error):
        if error:
            messagebox.showerror("Error", str(error))
        else:
            fig, cumple = resultado
            self._mostrar_figura(fig)
            msg = "Cumple Nyquist" if cumple else "NO cumple Nyquist (Aliasing)"
            self._set_estado(msg, "green" if cumple else "red")
        self._actualizar_botones()

    def _cmd_rep_orig(self):
        self._ejecutar_tarea("Reproduciendo...", self.controller.reproducir_original, self._cb_reproducir)

    def _cmd_rep_analizado(self):
        tipo = self.OPCIONES_FILTRO.get(self.combo_analisis.get())
        self._ejecutar_tarea("Reproduciendo...", lambda: self.controller.reproducir_filtrado(tipo), self._cb_reproducir)

    def _cb_reproducir(self, _, error):
        if error:
            messagebox.showerror("Error", str(error))
        self._set_estado("Reproducción finalizada.", "black")
        self._actualizar_botones()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _actualizar_botones(self):
        hay_orig = self.controller.hay_original
        hay_filt = self.controller.hay_filtrada_media_movil or self.controller.hay_resampleada
        
        self.btn_grabar.config(state="normal")
        self.btn_analizar.config(state="normal" if hay_orig else "disabled")
        self.btn_rep_orig.config(state="normal" if hay_orig else "disabled")
        self.btn_rep_analizado.config(state="normal" if hay_filt else "disabled")

    def _set_estado(self, texto: str, color: str = "gray"):
        self.lbl_estado.config(text=texto, foreground=color)

    def _mostrar_figura(self, fig):
        if self._canvas_widget:
            self._canvas_widget.get_tk_widget().destroy()
        self._canvas_widget = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        self._canvas_widget.draw()
        self._canvas_widget.get_tk_widget().pack(fill="both", expand=True)

def main():
    root = tk.Tk()
    app = LabGUI(root, controller=LabController(
        io=AudioIO(), 
        filtro=MovingAverageFilter(M=LabController.M_POR_DEFECTO), 
        analyzer=NyquistAnalyzer(), 
        plotter=SignalPlotter()
    ))
    root.mainloop()

if __name__ == "__main__":
    main()