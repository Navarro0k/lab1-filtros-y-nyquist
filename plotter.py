import numpy as np
from matplotlib.figure import Figure

class SignalPlotter:
    def _aplicar_estilo(self, ax, titulo, xlabel, ylabel):
        ax.set_title(titulo, fontsize=8, fontweight='bold', pad=4)
        ax.set_xlabel(xlabel, fontsize=7)
        ax.set_ylabel(ylabel, fontsize=7)

        ax.grid(True, color='#E0E0E0', linestyle=':', linewidth=0.25)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)

        ax.tick_params(labelsize=6, width=0.4, length=2.5)

    def crear_figura_comparacion(self, orig: np.ndarray, filt: np.ndarray, fs: int = None) -> Figure:
        orig = np.asarray(orig).flatten()
        filt = np.asarray(filt).flatten()

        if fs is not None:
            t = np.arange(len(orig)) / fs
            xlabel = "Tiempo [s]"
        else:
            t = np.arange(len(orig))
            xlabel = "Muestra [n]"

        fig = Figure(figsize=(9, 4), dpi=300)
        ax = fig.add_subplot(111)

        # Líneas ultra finas para máximo detalle visual
        ax.plot(t, orig, color='#90A4AE', linewidth=0.12, label="Original", zorder=1)
        ax.plot(t, filt, color='#D84315', linewidth=0.12, alpha=0.7, label="Filtrada", zorder=2)

        self._aplicar_estilo(ax, "Temporal: Original vs Filtrada", xlabel, "Amplitud")
        ax.legend(fontsize=6, loc='upper right', framealpha=0.8, handlelength=1.2)

        fig.tight_layout(pad=3)

        return fig

    def crear_figura_espectro_comparacion(self, orig: np.ndarray, fs_orig: int, res: np.ndarray, fs_new: int, cumple_nyquist: bool = None) -> Figure:
        # Altura reducida de 4.5 a 3.5 para que no sature la ventana de Tkinter
        fig = Figure(figsize=(8, 3.5), dpi=300)
        
        estado = ""
        if cumple_nyquist is not None:
            if cumple_nyquist is True:
                estado = " | Nyquist: CUMPLE"
            else:
                estado = " | Nyquist: NO CUMPLE"
                
        ax1 = fig.add_subplot(211)
        titulo_orig = f"Original (fs = {fs_orig} Hz)"
        self._dibujar_espectro(ax1, orig, fs_orig, titulo_orig)

        ax2 = fig.add_subplot(212)
        titulo_res = f"Remuestreado (fs = {fs_new} Hz){estado}"
        self._dibujar_espectro(ax2, res, fs_new, titulo_res)

        # Se aumenta el pad para dar más espacio entre subplots y evitar solapamientos
        fig.tight_layout(pad=2.2)
        
        return fig

    def _dibujar_espectro(self, ax, datos: np.ndarray, fs: int, titulo: str):
        datos = np.asarray(datos).flatten()

        if len(datos) == 0:
            ax.set_title(titulo + " (Vacía)", fontsize=8)
            return

        n = len(datos)
        espectro = np.abs(np.fft.rfft(datos)) / n
        frecs = np.fft.rfftfreq(n, d=1.0 / fs)

        ax.fill_between(frecs, espectro, color='#BBDEFB', alpha=0.25)
        ax.plot(frecs, espectro, color='#1565C0', linewidth=0.2)

        self._aplicar_estilo(ax, titulo, "Frecuencia [Hz]", "Magnitud")

        ax.set_xlim(left=0, right=fs / 2)
        ax.set_ylim(bottom=0)