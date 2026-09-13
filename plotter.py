import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class SignalPlotter:
    COLOR_ORIG = '#90A4AE'
    COLOR_FILT = '#D84315'
    COLOR_ESPEC = '#1565C0'
    COLOR_FILL = '#BBDEFB'

    def _aplicar_estilo(self, ax, titulo, xlabel, ylabel):
        ax.set_title(titulo, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.grid(True, color='#E0E0E0', linestyle='--', linewidth=0.7, alpha=0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#78909C')
        ax.spines['bottom'].set_color('#78909C')
        ax.tick_params(colors='#455A64', labelsize=9)

    def crear_figura_comparacion(self, orig: np.ndarray, filt: np.ndarray, fs: int = None) -> Figure:
        orig = np.asarray(orig).flatten()
        filt = np.asarray(filt).flatten()

        if fs:
            t_orig = np.arange(len(orig)) / fs
            t_filt = np.arange(len(filt)) / fs
            xlabel = "Tiempo [s]"
        else:
            t_orig = np.arange(len(orig))
            t_filt = np.arange(len(filt))
            xlabel = "Muestra [n]"

        fig = Figure(figsize=(10, 5), dpi=120)
        ax = fig.add_subplot(111)
        
        ax.plot(t_orig, orig, color=self.COLOR_ORIG, linewidth=1.2, label="Señal Original", zorder=1)
        ax.plot(t_filt, filt, color=self.COLOR_FILT, linewidth=2.0, label="Filtrada (Promedio Móvil)", zorder=2)
        
        self._aplicar_estilo(ax, "Comparación Temporal: Original vs. Filtrada", xlabel, "Amplitud")
        ax.legend(frameon=True, shadow=True, fancybox=True, fontsize=10, loc='upper right')
        fig.tight_layout()
        return fig

    def crear_figura_espectro_comparacion(self, orig: np.ndarray, fs_orig: int,
                                          resampleada: np.ndarray, fs_new: int,
                                          cumple_nyquist: bool = None) -> Figure:
        fig = Figure(figsize=(10, 7), dpi=120)

        ax1 = fig.add_subplot(211)
        self._dibujar_espectro(ax1, orig, fs_orig, f"Espectro Original (fs = {fs_orig} Hz)")

        ax2 = fig.add_subplot(212)
        titulo_2 = f"Espectro Remuestreado (fs = {fs_new} Hz)"
        if cumple_nyquist is not None:
            estado = "CUMPLE" if cumple_nyquist else "NO CUMPLE (Aliasing)"
            titulo_2 += f"  |  Nyquist: {estado}"
            
        self._dibujar_espectro(ax2, resampleada, fs_new, titulo_2)

        fig.tight_layout(pad=2.0)
        return fig

    def _dibujar_espectro(self, ax, datos: np.ndarray, fs: int, titulo: str) -> None:
        datos = np.asarray(datos).flatten()
        n = len(datos)
        if n == 0:
            ax.set_title(titulo + " (señal vacía)")
            return
            
        espectro = np.fft.rfft(datos)
        frecuencias = np.fft.rfftfreq(n, d=1.0 / fs)
        magnitud = np.abs(espectro) / n

        ax.fill_between(frecuencias, magnitud, color=self.COLOR_FILL, alpha=0.5)
        ax.plot(frecuencias, magnitud, color=self.COLOR_ESPEC, linewidth=1.5)
        
        self._aplicar_estilo(ax, titulo, "Frecuencia [Hz]", "Magnitud")
        ax.set_xlim(left=0) 
        ax.set_ylim(bottom=0)

    def plot_comparison(self, orig: np.ndarray, filt: np.ndarray, fs: int = None, guardar_como: str = None) -> None:
        fig = self.crear_figura_comparacion(orig, filt, fs)
        if guardar_como:
            fig.savefig(guardar_como, dpi=300, bbox_inches='tight')
            print(f"Gráfica guardada exitosamente en: {guardar_como}")
        else:
            dummy_fig = plt.figure(figsize=(10, 5), dpi=120)
            dummy_fig.canvas.manager.canvas.figure = fig
            fig.canvas.manager = dummy_fig.canvas.manager
            plt.show()

    def plot_spectrum(self, datos: np.ndarray, fs: int, guardar_como: str = None) -> None:
        fig = Figure(figsize=(10, 4), dpi=120)
        ax = fig.add_subplot(111)
        self._dibujar_espectro(ax, datos, fs, f"Espectro de Magnitud (fs = {fs} Hz)")
        fig.tight_layout()
        
        if guardar_como:
            fig.savefig(guardar_como, dpi=300, bbox_inches='tight')
            print(f"Espectro guardado exitosamente en: {guardar_como}")
        else:
            dummy_fig = plt.figure(figsize=(10, 4), dpi=120)
            dummy_fig.canvas.manager.canvas.figure = fig
            fig.canvas.manager = dummy_fig.canvas.manager
            plt.show()