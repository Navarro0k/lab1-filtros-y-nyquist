import numpy as np
from matplotlib.figure import Figure


class SignalPlotter:
    def _aplicar_estilo(self, ax, titulo, xlabel, ylabel):
        ax.set_title(titulo, fontsize=9, fontweight='bold', pad=4)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)

        ax.grid(True, color='#E0E0E0', linestyle=':', linewidth=0.5)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['bottom'].set_linewidth(0.5)

        ax.tick_params(labelsize=7, width=0.4, length=2.5)

    def crear_figura_comparacion(self, orig: np.ndarray, filt: np.ndarray, fs: int = None) -> Figure:
        """Grafica la señal original (arriba) y la señal filtrada (abajo) en ejes separados."""
        orig = np.asarray(orig).flatten()
        filt = np.asarray(filt).flatten()

        if fs is not None:
            t_orig = np.arange(len(orig)) / fs
            t_filt = np.arange(len(filt)) / fs
            xlabel = "Tiempo [s]"
        else:
            t_orig = np.arange(len(orig))
            t_filt = np.arange(len(filt))
            xlabel = "Muestra [n]"

        # dpi más alto y líneas más finas para que se aprecie el detalle de
        # la forma de onda al hacer zoom con la barra de herramientas.
        fig = Figure(figsize=(9.5, 5.6), dpi=150)

        ax1 = fig.add_subplot(211)
        ax1.plot(t_orig, orig, color='#90A4AE', linewidth=0.35, antialiased=True)
        self._aplicar_estilo(ax1, "Señal Original (sin filtro)", "", "Amplitud")

        ax2 = fig.add_subplot(212, sharex=ax1)
        ax2.plot(t_filt, filt, color='#D84315', linewidth=0.35, antialiased=True)
        self._aplicar_estilo(ax2, "Señal Filtrada (Media Móvil)", xlabel, "Amplitud")

        fig.tight_layout(pad=2.5)

        return fig