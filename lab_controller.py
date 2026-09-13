from core.moving_average_filter import MovingAverageFilter
from core.nyquist_analyzer import NyquistAnalyzer
from audio_io import AudioIO
from plotter import SignalPlotter

class LabController:
    """Orquesta el flujo completo del laboratorio."""

    M_POR_DEFECTO = 5
    FS_POR_DEFECTO = 44100
    DURACION_POR_DEFECTO = 5.0
    F_MAX_POR_DEFECTO = 4000.0
    NEW_FS_POR_DEFECTO = 8000

    TIPO_MEDIA_MOVIL = "media_movil"
    TIPO_NYQUIST = "nyquist"

    def __init__(self, io: AudioIO = None, filtro: MovingAverageFilter = None,
                 analyzer: NyquistAnalyzer = None, plotter: SignalPlotter = None):
        self._io = io or AudioIO()
        self._filtro = filtro or MovingAverageFilter(M=self.M_POR_DEFECTO)
        self._analyzer = analyzer or NyquistAnalyzer()
        self._plotter = plotter or SignalPlotter()

        self._fs = self.FS_POR_DEFECTO
        self._duration = self.DURACION_POR_DEFECTO

        self._ultima_original = None
        self._ultima_filtrada_mm = None
        self._ultima_resampleada = None
        self._ultima_fs_resampleada = None
        self._ultimo_cumple_nyquist = None

    def configurar(self, M: int = None, fs: int = None, duration: float = None) -> None:
        if M is not None:
            self._filtro.M = M
        if fs is not None:
            self._fs = fs
        if duration is not None:
            self._duration = duration

    def grabar(self) -> bool:
        """
        Graba la señal original. 
        Retorna False siempre, ya que se eliminó el modo simulado.
        """
        self._ultima_original = self._io.record(self._duration, self._fs)

        # Se invalidan los análisis previos porque hay una nueva grabación
        self._ultima_filtrada_mm = None
        self._ultima_resampleada = None
        self._ultima_fs_resampleada = None
        self._ultimo_cumple_nyquist = None

        return False  # Ya no existe self._io.ultimo_modo_simulado

    def analizar_media_movil(self):
        if self._ultima_original is None:
            raise RuntimeError("Primero hay que grabar una señal (botón 'Grabar').")

        self._ultima_filtrada_mm = self._filtro.apply(self._ultima_original, self._fs)
        return self._plotter.crear_figura_comparacion(self._ultima_original, self._ultima_filtrada_mm, self._fs)

    def analizar_nyquist(self, f_max: float, new_fs: int):
        if self._ultima_original is None:
            raise RuntimeError("Primero hay que grabar una señal (botón 'Grabar').")

        cumple_nyquist = self._analyzer.check(new_fs, f_max) 
        self._ultima_resampleada = self._analyzer.resample(self._ultima_original, self._fs, new_fs)
        
        self._ultima_fs_resampleada = new_fs
        self._ultimo_cumple_nyquist = cumple_nyquist

        fig = self._plotter.crear_figura_espectro_comparacion(
            self._ultima_original, self._fs,
            self._ultima_resampleada, new_fs,
            cumple_nyquist=cumple_nyquist,
        )
        return fig, cumple_nyquist

    def reproducir_original(self) -> None:
        if self._ultima_original is None:
            raise RuntimeError("Primero hay que grabar una señal.")
        self._io.play(self._ultima_original, self._fs)

    def reproducir_filtrado(self, tipo: str) -> None:
        if tipo == self.TIPO_MEDIA_MOVIL:
            if self._ultima_filtrada_mm is None:
                raise RuntimeError("No hay señal filtrada con media móvil todavía.")
            self._io.play(self._ultima_filtrada_mm, self._fs)

        elif tipo == self.TIPO_NYQUIST:
            if self._ultima_resampleada is None:
                raise RuntimeError("No hay señal remuestreada todavía.")
            self._io.play(self._ultima_resampleada, self._ultima_fs_resampleada)

        else:
            raise ValueError(f"Tipo de filtro desconocido: {tipo!r}")

    @property
    def M(self) -> int: return self._filtro.M
    @property
    def fs(self) -> int: return self._fs
    @property
    def duration(self) -> float: return self._duration
    @property
    def hay_original(self) -> bool: return self._ultima_original is not None
    @property
    def hay_filtrada_media_movil(self) -> bool: return self._ultima_filtrada_mm is not None
    @property
    def hay_resampleada(self) -> bool: return self._ultima_resampleada is not None