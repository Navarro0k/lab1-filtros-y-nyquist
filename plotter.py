"""
plotter.py

Encapsula las visualizaciones del laboratorio: comparacion de senales
en el tiempo (original vs. filtrada) y espectro de frecuencia.

Cada grafica se construye primero como un objeto matplotlib.figure.Figure
(metodos crear_*), lo que permite:
  - mostrarla en una ventana aparte (modo consola / script), o
  - incrustarla dentro de un widget de una interfaz grafica (Tkinter),
sin duplicar la logica de dibujo.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class SignalPlotter:
    """
    Genera las graficas requeridas por el laboratorio usando matplotlib.
    """

    # ------------------------------------------------------------------
    # Construccion de figuras (reutilizables por consola o por GUI)
    # ------------------------------------------------------------------
    def crear_figura_comparacion(self, orig: np.ndarray, filt: np.ndarray,
                                  fs: int = None) -> Figure:
        """
        Construye (sin mostrar) la figura de comparacion original vs.
        filtrada.

        Retorna
        -------
        fig : matplotlib.figure.Figure
        """
        orig = np.asarray(orig).flatten()
        filt = np.asarray(filt).flatten()

        if fs:
            t_orig = np.arange(len(orig)) / fs
            t_filt = np.arange(len(filt)) / fs
            xlabel = "Tiempo [s]"
        else:
            t_orig = np.arange(len(orig))
            t_filt = np.arange(len(filt))
            xlabel = "Muestra"

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(t_orig, orig, label="Original", alpha=0.7)
        ax.plot(t_filt, filt, label="Filtrada (promedio movil)", alpha=0.9)
        ax.set_title("Comparacion: senal original vs. filtrada")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Amplitud")
        ax.legend()
        fig.tight_layout()
        return fig

    def crear_figura_espectro(self, datos: np.ndarray, fs: int) -> Figure:
        """
        Construye (sin mostrar) la figura del espectro de magnitud (FFT).

        Retorna
        -------
        fig : matplotlib.figure.Figure
        """
        datos = np.asarray(datos).flatten()
        n = len(datos)

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        if n == 0:
            ax.set_title("Espectro de magnitud (senal vacia)")
            fig.tight_layout()
            return fig

        espectro = np.fft.rfft(datos)
        frecuencias = np.fft.rfftfreq(n, d=1.0 / fs)
        magnitud = np.abs(espectro) / n

        ax.plot(frecuencias, magnitud)
        ax.set_title(f"Espectro de magnitud (fs = {fs} Hz)")
        ax.set_xlabel("Frecuencia [Hz]")
        ax.set_ylabel("Magnitud")
        fig.tight_layout()
        return fig

    def crear_figura_espectro_comparacion(self, orig: np.ndarray, fs_orig: int,
                                           resampleada: np.ndarray, fs_new: int,
                                           cumple_nyquist: bool = None) -> Figure:
        """
        Construye una figura con dos subplots: el espectro de la senal
        original (a fs_orig) y el espectro de la senal remuestreada
        (a fs_new). Permite comparar visualmente el efecto de
        muestrear por encima o por debajo del criterio de Nyquist.

        Parametros
        ----------
        orig : np.ndarray
            Senal original.
        fs_orig : int
            Frecuencia de muestreo original en Hz.
        resampleada : np.ndarray
            Senal ya remuestreada.
        fs_new : int
            Nueva frecuencia de muestreo en Hz.
        cumple_nyquist : bool, opcional
            Resultado de NyquistAnalyzer.check(), usado solo para
            anotar el titulo de la figura.

        Retorna
        -------
        fig : matplotlib.figure.Figure
        """
        fig = Figure(figsize=(8, 6), dpi=100)

        ax1 = fig.add_subplot(211)
        self._dibujar_espectro(ax1, orig, fs_orig, f"Espectro original (fs = {fs_orig} Hz)")

        ax2 = fig.add_subplot(212)
        titulo_2 = f"Espectro remuestreado (fs = {fs_new} Hz)"
        if cumple_nyquist is not None:
            titulo_2 += "  -  Nyquist: " + ("CUMPLE" if cumple_nyquist else "NO CUMPLE (aliasing)")
        self._dibujar_espectro(ax2, resampleada, fs_new, titulo_2)

        fig.tight_layout()
        return fig

    @staticmethod
    def _dibujar_espectro(ax, datos: np.ndarray, fs: int, titulo: str) -> None:
        datos = np.asarray(datos).flatten()
        n = len(datos)
        if n == 0:
            ax.set_title(titulo + " (senal vacia)")
            return
        espectro = np.fft.rfft(datos)
        frecuencias = np.fft.rfftfreq(n, d=1.0 / fs)
        magnitud = np.abs(espectro) / n
        ax.plot(frecuencias, magnitud)
        ax.set_title(titulo)
        ax.set_xlabel("Frecuencia [Hz]")
        ax.set_ylabel("Magnitud")

    # ------------------------------------------------------------------
    # Interfaz "clasica" (modo consola / script): muestra o guarda
    # ------------------------------------------------------------------
    def plot_comparison(self, orig: np.ndarray, filt: np.ndarray, fs: int = None,
                         guardar_como: str = None) -> None:
        """
        Grafica la senal original y la filtrada, superpuestas, para
        comparar el efecto del filtro de promedio movil.

        Parametros
        ----------
        orig : np.ndarray
            Senal original.
        filt : np.ndarray
            Senal filtrada.
        fs : int, opcional
            Frecuencia de muestreo, usada para construir el eje de
            tiempo en segundos. Si no se entrega, el eje x se muestra
            en numero de muestra.
        guardar_como : str, opcional
            Si se entrega una ruta, la figura se guarda en disco en
            vez de mostrarse en pantalla.
        """
        if guardar_como:
            fig = self.crear_figura_comparacion(orig, filt, fs)
            fig.savefig(guardar_como, dpi=150)
            print(f"[SignalPlotter] Grafica guardada en: {guardar_como}")
        else:
            orig = np.asarray(orig).flatten()
            filt = np.asarray(filt).flatten()
            if fs:
                t_orig, t_filt, xlabel = np.arange(len(orig)) / fs, np.arange(len(filt)) / fs, "Tiempo [s]"
            else:
                t_orig, t_filt, xlabel = np.arange(len(orig)), np.arange(len(filt)), "Muestra"

            plt.figure(figsize=(10, 4))
            plt.plot(t_orig, orig, label="Original", alpha=0.7)
            plt.plot(t_filt, filt, label="Filtrada (promedio movil)", alpha=0.9)
            plt.title("Comparacion: senal original vs. filtrada")
            plt.xlabel(xlabel)
            plt.ylabel("Amplitud")
            plt.legend()
            plt.tight_layout()
            plt.show()

    def plot_spectrum(self, datos: np.ndarray, fs: int, guardar_como: str = None) -> None:
        """
        Grafica el espectro de magnitud (FFT) de la senal.

        Parametros
        ----------
        datos : np.ndarray
            Senal a analizar.
        fs : int
            Frecuencia de muestreo en Hz.
        guardar_como : str, opcional
            Si se entrega una ruta, la figura se guarda en disco en
            vez de mostrarse en pantalla.
        """
        if guardar_como:
            fig = self.crear_figura_espectro(datos, fs)
            fig.savefig(guardar_como, dpi=150)
            print(f"[SignalPlotter] Grafica guardada en: {guardar_como}")
            return

        datos = np.asarray(datos).flatten()
        n = len(datos)
        if n == 0:
            print("[SignalPlotter] Aviso: senal vacia, no se puede graficar espectro.")
            return

        espectro = np.fft.rfft(datos)
        frecuencias = np.fft.rfftfreq(n, d=1.0 / fs)
        magnitud = np.abs(espectro) / n

        plt.figure(figsize=(10, 4))
        plt.plot(frecuencias, magnitud)
        plt.title(f"Espectro de magnitud (fs = {fs} Hz)")
        plt.xlabel("Frecuencia [Hz]")
        plt.ylabel("Magnitud")
        plt.tight_layout()
        plt.show()
