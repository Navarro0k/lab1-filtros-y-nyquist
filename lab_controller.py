"""
lab_controller.py

Orquestador del laboratorio. Coordina AudioIO, MovingAverageFilter,
NyquistAnalyzer y SignalPlotter.

Expone un flujo interactivo pensado para una interfaz con botones
independientes:

    Grabar  ->  graba unicamente la senal original (no filtra).
    Analisis Media Movil  ->  filtra la ultima senal grabada con el M
        actual y grafica original vs. filtrada.
    Analisis Nyquist  ->  verifica el criterio de Nyquist para f_max,
        remuestrea la senal grabada a new_fs y grafica los espectros
        comparados.
    Reproducir Original  ->  reproduce la senal tal como se grabo.
    Reproducir Filtrado  ->  reproduce el resultado del analisis
        elegido (media movil o nyquist/remuestreo).
"""

from core.moving_average_filter import MovingAverageFilter
from core.nyquist_analyzer import NyquistAnalyzer
from audio_io import AudioIO
from plotter import SignalPlotter


class LabController:
    """
    Orquesta el flujo completo del laboratorio.

    Atributos (privados)
    ---------------------
    io : AudioIO
    filtro : MovingAverageFilter
    analyzer : NyquistAnalyzer
    plotter : SignalPlotter
    """

    # Valores por defecto del laboratorio.
    M_POR_DEFECTO = 5
    FS_POR_DEFECTO = 44100
    DURACION_POR_DEFECTO = 5.0
    F_MAX_POR_DEFECTO = 4000.0
    NEW_FS_POR_DEFECTO = 8000

    TIPO_MEDIA_MOVIL = "media_movil"
    TIPO_NYQUIST = "nyquist"

    def __init__(self, io: AudioIO = None, filtro: MovingAverageFilter = None,
                 analyzer: NyquistAnalyzer = None, plotter: SignalPlotter = None):
        self._io = io if io is not None else AudioIO()
        self._filtro = filtro if filtro is not None else MovingAverageFilter(
            M=self.M_POR_DEFECTO)
        self._analyzer = analyzer if analyzer is not None else NyquistAnalyzer()
        self._plotter = plotter if plotter is not None else SignalPlotter()

        # Parametros configurables desde la GUI.
        self._fs = self.FS_POR_DEFECTO
        self._duration = self.DURACION_POR_DEFECTO

        # Estado de la ultima grabacion / analisis.
        self._ultima_original = None
        self._ultima_filtrada_mm = None      # resultado del analisis de media movil
        self._ultima_resampleada = None      # resultado del analisis de Nyquist
        self._ultima_fs_resampleada = None
        self._ultimo_cumple_nyquist = None

    # ------------------------------------------------------------------
    # Configuracion de parametros
    # ------------------------------------------------------------------
    def configurar(self, M: int = None, fs: int = None, duration: float = None) -> None:
        """
        Actualiza los parametros del laboratorio (M, fs de grabacion,
        duracion). Cualquier parametro no entregado conserva su valor
        actual.
        """
        if M is not None:
            self._filtro.M = M
        if fs is not None:
            self._fs = fs
        if duration is not None:
            self._duration = duration

    # ------------------------------------------------------------------
    # Boton "Grabar": solo graba la senal original
    # ------------------------------------------------------------------
    def grabar(self):
        """
        Graba la senal original con los parametros actuales (fs,
        duration). No aplica ningun filtro ni analisis todavia.

        Retorna
        -------
        modo_simulado : bool
            True si no se detecto microfono real y se uso una senal
            simulada (para que la GUI pueda avisarle al usuario).
        """
        datos = self._io.record(self._duration, self._fs)
        self._ultima_original = datos

        # Cualquier analisis previo queda invalido: corresponde a otra grabacion.
        self._ultima_filtrada_mm = None
        self._ultima_resampleada = None
        self._ultima_fs_resampleada = None
        self._ultimo_cumple_nyquist = None

        return self._io.ultimo_modo_simulado

    # ------------------------------------------------------------------
    # Boton "Analisis Media Movil"
    # ------------------------------------------------------------------
    def analizar_media_movil(self):
        """
        Aplica el filtro de promedio movil (con el M actual) sobre la
        ultima senal grabada, y construye la grafica de comparacion.

        Retorna
        -------
        fig : matplotlib.figure.Figure
        """
        if self._ultima_original is None:
            raise RuntimeError("Primero hay que grabar una senal (boton 'Grabar').")

        datos_filtrados = self._filtro.apply(self._ultima_original, self._fs)
        self._ultima_filtrada_mm = datos_filtrados

        fig = self._plotter.crear_figura_comparacion(
            self._ultima_original, datos_filtrados, self._fs)
        return fig

    # ------------------------------------------------------------------
    # Boton "Analisis Nyquist"
    # ------------------------------------------------------------------
    def analizar_nyquist(self, f_max: float, new_fs: int):
        """
        Verifica el criterio de Nyquist para f_max sobre la senal
        grabada (a self._fs), remuestrea la senal a new_fs y construye
        la grafica comparativa de espectros.

        Parametros
        ----------
        f_max : float
            Frecuencia maxima de interes (ancho de banda) en Hz.
        new_fs : int
            Nueva frecuencia de muestreo a evaluar (por encima o por
            debajo del limite de Nyquist).

        Retorna
        -------
        fig : matplotlib.figure.Figure
        cumple_nyquist : bool
        """
        if self._ultima_original is None:
            raise RuntimeError("Primero hay que grabar una senal (boton 'Grabar').")

        # Se evalua si la NUEVA frecuencia de muestreo (la que se quiere
        # probar, por encima o por debajo del limite) cumple el criterio
        # de Nyquist para f_max. Esto es lo que permite "variar la
        # frecuencia de muestreo por encima y por debajo del criterio".
        cumple_nyquist = self._analyzer.check(self._ultima_original, new_fs, f_max)
        datos_resampleados = self._analyzer.resample(self._ultima_original, self._fs, new_fs)

        self._ultima_resampleada = datos_resampleados
        self._ultima_fs_resampleada = new_fs
        self._ultimo_cumple_nyquist = cumple_nyquist

        fig = self._plotter.crear_figura_espectro_comparacion(
            self._ultima_original, self._fs,
            datos_resampleados, new_fs,
            cumple_nyquist=cumple_nyquist,
        )
        return fig, cumple_nyquist

    # ------------------------------------------------------------------
    # Botones de reproduccion
    # ------------------------------------------------------------------
    def reproducir_original(self) -> None:
        """Reproduce la senal tal como fue grabada (sin filtrar)."""
        if self._ultima_original is None:
            raise RuntimeError("Primero hay que grabar una senal (boton 'Grabar').")
        self._io.play(self._ultima_original, self._fs)

    def reproducir_filtrado(self, tipo: str) -> None:
        """
        Reproduce el resultado de un analisis previo.

        Parametros
        ----------
        tipo : str
            LabController.TIPO_MEDIA_MOVIL o LabController.TIPO_NYQUIST.
        """
        if tipo == self.TIPO_MEDIA_MOVIL:
            if self._ultima_filtrada_mm is None:
                raise RuntimeError(
                    "No hay una senal filtrada con media movil todavia. "
                    "Primero hay que correr 'Analisis Media Movil'."
                )
            self._io.play(self._ultima_filtrada_mm, self._fs)

        elif tipo == self.TIPO_NYQUIST:
            if self._ultima_resampleada is None:
                raise RuntimeError(
                    "No hay una senal remuestreada todavia. "
                    "Primero hay que correr 'Analisis Nyquist'."
                )
            self._io.play(self._ultima_resampleada, self._ultima_fs_resampleada)

        else:
            raise ValueError(f"Tipo de filtro desconocido: {tipo!r}")

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------
    @property
    def M(self) -> int:
        return self._filtro.M

    @property
    def fs(self) -> int:
        return self._fs

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def hay_original(self) -> bool:
        return self._ultima_original is not None

    @property
    def hay_filtrada_media_movil(self) -> bool:
        return self._ultima_filtrada_mm is not None

    @property
    def hay_resampleada(self) -> bool:
        return self._ultima_resampleada is not None
