from core.moving_average_filter import MovingAverageFilter
from core.nyquist_analyzer import NyquistAnalyzer
from audio_io import AudioIO
from plotter import SignalPlotter

class LabController:
    # Constantes para la GUI
    M_POR_DEFECTO, FS_POR_DEFECTO, DURACION_POR_DEFECTO = 5, 44100, 5.0
    F_MAX_POR_DEFECTO, NEW_FS_POR_DEFECTO = 4000.0, 8000
    TIPO_MEDIA_MOVIL, TIPO_NYQUIST = "Media Movil", "Nyquist (remuestreo)"

    def __init__(self):
        self.io = AudioIO()
        self.filtro = MovingAverageFilter()
        self.analyzer = NyquistAnalyzer()
        self.plotter = SignalPlotter()

        self.fs = self.FS_POR_DEFECTO
        self.f_max = self.F_MAX_POR_DEFECTO
        self.new_fs = self.NEW_FS_POR_DEFECTO

        # Señales
        self.original = self.filtrada = self.resampleada = None

        self.hay_original = False
        self.hay_filtrada_media_movil = False
        self.hay_resampleada = False

    def grabar(self, duration: float) -> bool:
        self.original = self.io.record(duration, self.fs)
        self.filtrada = self.resampleada = None
        
        self.hay_original = True
        self.hay_filtrada_media_movil = self.hay_resampleada = False
        return False 

    def analizar(self, tipo: str, param: int):
        if not self.hay_original:
            raise RuntimeError("Primero graba una señal.")

        if tipo == self.TIPO_MEDIA_MOVIL:
            self.filtro.M = param
            self.filtrada = self.filtro.apply(self.original)
            self.hay_filtrada_media_movil = True
            return self.plotter.crear_figura_comparacion(self.original, self.filtrada, self.fs)
            
        elif tipo == self.TIPO_NYQUIST:
            self.new_fs = param
            cumple = self.analyzer.check(self.new_fs, self.f_max)
            self.resampleada = self.analyzer.resample(self.original, self.fs, self.new_fs)
            self.hay_resampleada = True
            
            fig = self.plotter.crear_figura_espectro_comparacion(
                self.original, self.fs, self.resampleada, self.new_fs, cumple_nyquist=cumple
            )
            return fig, cumple

    def reproducir_original(self):
        if self.hay_original:
            self.io.play(self.original, self.fs)

    def reproducir_filtrado(self, tipo: str):
        if tipo == self.TIPO_MEDIA_MOVIL and self.hay_filtrada_media_movil:
            self.io.play(self.filtrada, self.fs)
        elif tipo == self.TIPO_NYQUIST and self.hay_resampleada:
            self.io.play(self.resampleada, self.new_fs)