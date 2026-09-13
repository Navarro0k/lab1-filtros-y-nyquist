"""
core/nyquist_analyzer.py

Implementa el analisis del criterio de Nyquist y el remuestreo
(resampling) de una senal, usado en la Parte 2 del laboratorio.
"""

import numpy as np
from scipy.signal import resample as scipy_resample


class NyquistAnalyzer:
    """
    Analiza si una senal cumple el criterio de Nyquist para una
    frecuencia maxima de interes dada, y permite remuestrearla.
    """

    def check(self, datos: np.ndarray, fs: int, f_max: float) -> bool:
        """
        Verifica si fs cumple el criterio de Nyquist para f_max:

            fs >= 2 * f_max

        Parametros
        ----------
        datos : np.ndarray
            Senal de entrada (no se usa directamente en el chequeo,
            se recibe para mantener una interfaz uniforme y para
            permitir extender el analisis, p. ej. estimando f_max
            desde el espectro si no se entrega explicitamente).
        fs : int
            Frecuencia de muestreo actual en Hz.
        f_max : float
            Frecuencia maxima de interes / ancho de banda de la senal
            en Hz.

        Retorna
        -------
        cumple_nyquist : bool
            True si fs >= 2 * f_max, False en caso contrario.
        """
        nyquist_freq = fs / 2.0
        cumple_nyquist = nyquist_freq >= f_max
        return cumple_nyquist

    def resample(self, datos: np.ndarray, fs: int, new_fs: int) -> np.ndarray:
        """
        Remuestrea la senal desde fs a new_fs.

        Parametros
        ----------
        datos : np.ndarray
            Senal de entrada (1D).
        fs : int
            Frecuencia de muestreo original en Hz.
        new_fs : int
            Nueva frecuencia de muestreo deseada en Hz.

        Retorna
        -------
        datos_resampleados : np.ndarray
            Senal remuestreada a new_fs.
        """
        datos = np.asarray(datos).flatten().astype(float)

        if datos.size == 0 or fs == new_fs:
            return datos

        n_muestras_nuevas = int(round(len(datos) * new_fs / fs))
        datos_resampleados = scipy_resample(datos, n_muestras_nuevas)

        return datos_resampleados
