"""
gui.py

Interfaz grafica (Tkinter) del laboratorio. Es el UNICO punto de
entrada de la aplicacion (no existe main.py aparte).

Permite:
  - Ingresar M (orden del filtro de promedio movil), fs (frecuencia de
    muestreo de grabacion) y la duracion de grabacion, todos con
    valores predeterminados.
  - Ingresar f_max y la nueva frecuencia de muestreo (new_fs) para el
    analisis de Nyquist, tambien con valores predeterminados.
  - Boton "Grabar": graba UNICAMENTE la senal original (sin filtrar).
  - Boton "Analisis Media Movil": filtra la ultima senal grabada con
    el M actual y muestra la grafica original vs. filtrada, usando la
    ecuacion y(n) = (1/M) * sum_{k=0}^{M-1} x(n-k).
  - Boton "Analisis Nyquist": verifica el criterio de Nyquist para
    f_max, remuestrea la senal grabada a new_fs y muestra los
    espectros comparados.
  - Boton "Reproducir Original": reproduce la senal tal como se grabo.
  - Selector "Filtro a reproducir" + boton "Reproducir Filtrado":
    reproduce el resultado del analisis elegido (media movil o
    Nyquist/remuestreo).

Mantiene la arquitectura de clases (AudioIO, MovingAverageFilter,
NyquistAnalyzer, SignalPlotter, LabController); esta GUI solo actua
como la "vista" que dispara los metodos de LabController.
"""

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
    """Ventana principal del laboratorio."""

    OPCIONES_FILTRO = {
        "Media Movil": LabController.TIPO_MEDIA_MOVIL,
        "Nyquist (remuestreo)": LabController.TIPO_NYQUIST,
    }

    def __init__(self, root: tk.Tk, controller: LabController = None):
        self.root = root
        self.root.title("Lab 1 - DSP: Media Movil y Criterio de Nyquist")
        self.root.geometry("880x750")

        self.controller = controller if controller is not None else LabController()

        self._canvas_widget = None  # canvas de matplotlib actualmente mostrado
        self._construir_widgets()

    # ------------------------------------------------------------------
    # Construccion de la interfaz
    # ------------------------------------------------------------------
    def _construir_widgets(self):
        # --- Parametros de grabacion / filtro de media movil ---
        frame_params = ttk.LabelFrame(self.root, text="Parametros de grabacion y filtro")
        frame_params.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(frame_params, text="M (orden del filtro):").grid(
            row=0, column=0, padx=5, pady=6, sticky="w")
        self.entry_M = ttk.Entry(frame_params, width=10)
        self.entry_M.insert(0, str(LabController.M_POR_DEFECTO))
        self.entry_M.grid(row=0, column=1, padx=5, pady=6, sticky="w")

        ttk.Label(frame_params, text="Frecuencia de muestreo fs (Hz):").grid(
            row=0, column=2, padx=5, pady=6, sticky="w")
        self.entry_fs = ttk.Entry(frame_params, width=10)
        self.entry_fs.insert(0, str(LabController.FS_POR_DEFECTO))
        self.entry_fs.grid(row=0, column=3, padx=5, pady=6, sticky="w")

        ttk.Label(frame_params, text="Duracion de grabacion (s):").grid(
            row=1, column=0, padx=5, pady=6, sticky="w")
        self.entry_duration = ttk.Entry(frame_params, width=10)
        self.entry_duration.insert(0, str(LabController.DURACION_POR_DEFECTO))
        self.entry_duration.grid(row=1, column=1, padx=5, pady=6, sticky="w")

        # --- Parametros del analisis de Nyquist ---
        frame_nyq = ttk.LabelFrame(self.root, text="Parametros del analisis de Nyquist")
        frame_nyq.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_nyq, text="f_max (Hz, ancho de banda de interes):").grid(
            row=0, column=0, padx=5, pady=6, sticky="w")
        self.entry_fmax = ttk.Entry(frame_nyq, width=10)
        self.entry_fmax.insert(0, str(LabController.F_MAX_POR_DEFECTO))
        self.entry_fmax.grid(row=0, column=1, padx=5, pady=6, sticky="w")

        ttk.Label(frame_nyq, text="Nueva fs a evaluar (Hz):").grid(
            row=0, column=2, padx=5, pady=6, sticky="w")
        self.entry_new_fs = ttk.Entry(frame_nyq, width=10)
        self.entry_new_fs.insert(0, str(LabController.NEW_FS_POR_DEFECTO))
        self.entry_new_fs.grid(row=0, column=3, padx=5, pady=6, sticky="w")

        ttk.Label(
            frame_nyq,
            text="(Prueba valores por encima y por debajo de 2*f_max para ver el efecto)",
            foreground="gray",
        ).grid(row=1, column=0, columnspan=4, padx=5, pady=(0, 4), sticky="w")

        # --- Botones: grabar y analisis ---
        frame_acciones = ttk.Frame(self.root)
        frame_acciones.pack(fill="x", padx=10, pady=5)

        self.btn_grabar = ttk.Button(
            frame_acciones, text="Grabar", command=self._on_grabar)
        self.btn_grabar.pack(side="left", padx=5)

        self.btn_analisis_mm = ttk.Button(
            frame_acciones, text="Analisis Media Movil",
            command=self._on_analisis_media_movil, state="disabled")
        self.btn_analisis_mm.pack(side="left", padx=5)

        self.btn_analisis_nyq = ttk.Button(
            frame_acciones, text="Analisis Nyquist",
            command=self._on_analisis_nyquist, state="disabled")
        self.btn_analisis_nyq.pack(side="left", padx=5)

        # --- Botones: reproduccion ---
        frame_reproduccion = ttk.LabelFrame(self.root, text="Reproduccion")
        frame_reproduccion.pack(fill="x", padx=10, pady=5)

        self.btn_reproducir_original = ttk.Button(
            frame_reproduccion, text="Reproducir Original",
            command=self._on_reproducir_original, state="disabled")
        self.btn_reproducir_original.pack(side="left", padx=5, pady=6)

        ttk.Label(frame_reproduccion, text="Filtro a reproducir:").pack(
            side="left", padx=(20, 5))
        self.combo_filtro = ttk.Combobox(
            frame_reproduccion, values=list(self.OPCIONES_FILTRO.keys()),
            state="readonly", width=20)
        self.combo_filtro.current(0)
        self.combo_filtro.pack(side="left", padx=5)

        self.btn_reproducir_filtrado = ttk.Button(
            frame_reproduccion, text="Reproducir Filtrado",
            command=self._on_reproducir_filtrado, state="disabled")
        self.btn_reproducir_filtrado.pack(side="left", padx=5)

        # --- Estado ---
        self.label_estado = ttk.Label(self.root, text="Listo.", foreground="gray")
        self.label_estado.pack(fill="x", padx=10, pady=(5, 0))

        # --- Zona de la grafica ---
        self.frame_grafica = ttk.LabelFrame(self.root, text="Resultado")
        self.frame_grafica.pack(fill="both", expand=True, padx=10, pady=10)

        self._todos_los_botones = [
            self.btn_grabar, self.btn_analisis_mm, self.btn_analisis_nyq,
            self.btn_reproducir_original, self.btn_reproducir_filtrado,
        ]

    # ------------------------------------------------------------------
    # Lectura y validacion de parametros
    # ------------------------------------------------------------------
    def _leer_entero(self, entry: ttk.Entry, nombre: str, minimo: int = 1) -> int:
        try:
            valor = int(entry.get())
        except ValueError:
            raise ValueError(f"{nombre} debe ser un numero entero.")
        if valor < minimo:
            raise ValueError(f"{nombre} debe ser mayor o igual a {minimo}.")
        return valor

    def _leer_flotante(self, entry: ttk.Entry, nombre: str, minimo: float = 0.0,
                        inclusive: bool = False) -> float:
        try:
            valor = float(entry.get())
        except ValueError:
            raise ValueError(f"{nombre} debe ser un numero.")
        if inclusive and valor < minimo:
            raise ValueError(f"{nombre} debe ser mayor o igual a {minimo}.")
        if not inclusive and valor <= minimo:
            raise ValueError(f"{nombre} debe ser mayor que {minimo}.")
        return valor

    def _leer_parametros_grabacion(self):
        M = self._leer_entero(self.entry_M, "M", minimo=1)
        fs = self._leer_entero(self.entry_fs, "La frecuencia de muestreo", minimo=1)
        duration = self._leer_flotante(self.entry_duration, "La duracion", minimo=0.0)
        return M, fs, duration

    def _leer_parametros_nyquist(self):
        f_max = self._leer_flotante(self.entry_fmax, "f_max", minimo=0.0)
        new_fs = self._leer_entero(self.entry_new_fs, "La nueva frecuencia de muestreo", minimo=1)
        return f_max, new_fs

    # ------------------------------------------------------------------
    # Boton "Grabar"
    # ------------------------------------------------------------------
    def _on_grabar(self):
        try:
            M, fs, duration = self._leer_parametros_grabacion()
        except ValueError as e:
            messagebox.showerror("Parametros invalidos", str(e))
            return

        self.controller.configurar(M=M, fs=fs, duration=duration)

        self._set_botones_habilitados(False)
        self._set_estado(f"Grabando {duration} s a {fs} Hz...")

        threading.Thread(target=self._grabar_en_hilo, daemon=True).start()

    def _grabar_en_hilo(self):
        try:
            modo_simulado = self.controller.grabar()
            error = None
        except Exception as e:
            modo_simulado = False
            error = e
        self.root.after(0, self._al_terminar_grabar, modo_simulado, error)

    def _al_terminar_grabar(self, modo_simulado, error):
        if error is not None:
            self._set_estado("Error al grabar.")
            messagebox.showerror("Error al grabar", str(error))
            self._actualizar_estado_botones()
            return

        if modo_simulado:
            self._set_estado(
                "\u26a0 No se detecto microfono: se genero una senal simulada "
                "(la duracion solicitada SI se respeto).",
                color="#b8860b",
            )
        else:
            self._set_estado("Grabacion completa. Ya se puede analizar o reproducir.")

        self._actualizar_estado_botones()

    # ------------------------------------------------------------------
    # Boton "Analisis Media Movil"
    # ------------------------------------------------------------------
    def _on_analisis_media_movil(self):
        try:
            M = self._leer_entero(self.entry_M, "M", minimo=1)
        except ValueError as e:
            messagebox.showerror("Parametros invalidos", str(e))
            return

        self.controller.configurar(M=M)
        self._set_botones_habilitados(False)
        self._set_estado(f"Aplicando filtro de media movil (M={M})...")

        threading.Thread(target=self._analisis_mm_en_hilo, daemon=True).start()

    def _analisis_mm_en_hilo(self):
        try:
            fig = self.controller.analizar_media_movil()
            error = None
        except Exception as e:
            fig, error = None, e
        self.root.after(0, self._al_terminar_analisis_mm, fig, error)

    def _al_terminar_analisis_mm(self, fig, error):
        if error is not None:
            self._set_estado("Error en el analisis de media movil.")
            messagebox.showerror("Error", str(error))
            self._actualizar_estado_botones()
            return

        self._mostrar_figura(fig)
        self._set_estado("Analisis de media movil completo.")
        self._actualizar_estado_botones()

    # ------------------------------------------------------------------
    # Boton "Analisis Nyquist"
    # ------------------------------------------------------------------
    def _on_analisis_nyquist(self):
        try:
            f_max, new_fs = self._leer_parametros_nyquist()
        except ValueError as e:
            messagebox.showerror("Parametros invalidos", str(e))
            return

        self._set_botones_habilitados(False)
        self._set_estado(f"Analizando Nyquist (f_max={f_max} Hz, nueva fs={new_fs} Hz)...")

        threading.Thread(
            target=self._analisis_nyquist_en_hilo, args=(f_max, new_fs), daemon=True
        ).start()

    def _analisis_nyquist_en_hilo(self, f_max, new_fs):
        try:
            fig, cumple = self.controller.analizar_nyquist(f_max, new_fs)
            error = None
        except Exception as e:
            fig, cumple, error = None, None, e
        self.root.after(0, self._al_terminar_analisis_nyquist, fig, cumple, error)

    def _al_terminar_analisis_nyquist(self, fig, cumple, error):
        if error is not None:
            self._set_estado("Error en el analisis de Nyquist.")
            messagebox.showerror("Error", str(error))
            self._actualizar_estado_botones()
            return

        self._mostrar_figura(fig)
        veredicto = "SI cumple" if cumple else "NO cumple (hay riesgo de aliasing)"
        self._set_estado(f"Analisis de Nyquist completo: {veredicto} el criterio de Nyquist.")
        self._actualizar_estado_botones()

    # ------------------------------------------------------------------
    # Botones de reproduccion
    # ------------------------------------------------------------------
    def _on_reproducir_original(self):
        self._set_botones_habilitados(False)
        self._set_estado("Reproduciendo senal original...")
        threading.Thread(target=self._reproducir_original_en_hilo, daemon=True).start()

    def _reproducir_original_en_hilo(self):
        try:
            self.controller.reproducir_original()
            error = None
        except Exception as e:
            error = e
        self.root.after(0, self._al_terminar_reproducir, error, "original")

    def _on_reproducir_filtrado(self):
        etiqueta = self.combo_filtro.get()
        tipo = self.OPCIONES_FILTRO.get(etiqueta)
        if tipo is None:
            messagebox.showerror("Error", "Selecciona un tipo de filtro valido.")
            return

        self._set_botones_habilitados(False)
        self._set_estado(f"Reproduciendo senal filtrada ({etiqueta})...")
        threading.Thread(
            target=self._reproducir_filtrado_en_hilo, args=(tipo,), daemon=True
        ).start()

    def _reproducir_filtrado_en_hilo(self, tipo):
        try:
            self.controller.reproducir_filtrado(tipo)
            error = None
        except Exception as e:
            error = e
        self.root.after(0, self._al_terminar_reproducir, error, "filtrado")

    def _al_terminar_reproducir(self, error, cual):
        if error is not None:
            self._set_estado(f"Error al reproducir ({cual}).")
            messagebox.showerror("Error al reproducir", str(error))
        else:
            self._set_estado(f"Reproduccion ({cual}) finalizada.")
        self._actualizar_estado_botones()

    # ------------------------------------------------------------------
    # Utilidades de UI
    # ------------------------------------------------------------------
    def _set_botones_habilitados(self, habilitados: bool):
        estado = "normal" if habilitados else "disabled"
        for boton in self._todos_los_botones:
            boton.config(state=estado)
        if not habilitados:
            return
        # Si se reactivan, se ajusta cada boton segun el estado real del controller.
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self):
        hay_original = self.controller.hay_original
        self.btn_analisis_mm.config(state="normal" if hay_original else "disabled")
        self.btn_analisis_nyq.config(state="normal" if hay_original else "disabled")
        self.btn_reproducir_original.config(state="normal" if hay_original else "disabled")

        hay_filtrada = (
            self.controller.hay_filtrada_media_movil or self.controller.hay_resampleada
        )
        self.btn_reproducir_filtrado.config(state="normal" if hay_filtrada else "disabled")
        self.btn_grabar.config(state="normal")

    def _set_estado(self, texto: str, color: str = "gray"):
        self.label_estado.config(text=texto, foreground=color)

    def _mostrar_figura(self, fig):
        if self._canvas_widget is not None:
            self._canvas_widget.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas_widget = canvas


def main():
    root = tk.Tk()
    io = AudioIO(channels=1)
    filtro = MovingAverageFilter(M=LabController.M_POR_DEFECTO)
    analyzer = NyquistAnalyzer()
    plotter = SignalPlotter()
    controller = LabController(io=io, filtro=filtro, analyzer=analyzer, plotter=plotter)

    app = LabGUI(root, controller=controller)
    root.mainloop()


if __name__ == "__main__":
    main()
