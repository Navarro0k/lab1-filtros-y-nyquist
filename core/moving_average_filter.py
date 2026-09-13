"""
core/moving_average_filter.py

Implementa el filtro de promedio movil (media movil / "peine") descrito
en el enunciado del laboratorio, usado en la Parte 1 para minimizar el
ruido blanco de una senal de audio capturada.
"""

import numpy as np


class MovingAverageFilter:
    """
    Filtro FIR de promedio movil (media movil) de orden M.

    Dada una senal de entrada x(n) de N puntos, la ecuacion del filtro,
    tal como se define en el enunciado del laboratorio, es:

        y(n) = (1/M) * sum_{k=0}^{M-1} x(n - k),   con M < N

    Es decir, cada muestra de salida y(n) es el promedio de la muestra
    actual x(n) junto con las M-1 muestras anteriores. Las muestras
    x(n-k) con indice negativo (al inicio de la senal) se consideran 0.

    Atributos
    ---------
    M : int
        Numero de muestras que se promedian (tamano de la ventana).
        Debe ser un entero positivo y menor que el largo N de la senal
        de entrada. Valores mas grandes producen mayor suavizado
        (mayor eliminacion de ruido) pero tambien mayor atenuacion de
        frecuencias altas y mayor retardo.
    """

    def __init__(self, M: int = 5):
        if not isinstance(M, int) or M < 1:
            raise ValueError("M debe ser un entero positivo (M >= 1).")
        self.M = M

    def apply(self, datos: np.ndarray, fs: int) -> np.ndarray:
        """
        Aplica el filtro de promedio movil a la senal de entrada,
        implementando directamente y(n) = (1/M) * sum_{k=0}^{M-1} x(n-k).

        Parametros
        ----------
        datos : np.ndarray
            Senal de entrada x(n), de N puntos (1D, mono). Si llega en
            2D (n_muestras, 1) se aplana automaticamente.
        fs : int
            Frecuencia de muestreo en Hz (no se usa en el calculo del
            filtro en si, pero se recibe para mantener una interfaz
            consistente con el resto de las clases).

        Retorna
        -------
        datos_filtrados : np.ndarray
            Senal filtrada y(n), del mismo largo N que la entrada.
        """
        datos = np.asarray(datos).flatten().astype(float)
        n = datos.size

        if n == 0:
            return datos

        if self.M >= n:
            raise ValueError(
                f"M ({self.M}) debe ser menor que el numero de puntos "
                f"de la senal N ({n}), segun M < N."
            )

        # Se antepone x(-1), x(-2), ..., x(-(M-1)) = 0 para poder
        # calcular y(n) tambien en las primeras M-1 muestras.
        datos_padded = np.concatenate([np.zeros(self.M - 1), datos])

        # Suma de ventana deslizante de tamano M mediante sumas
        # acumuladas: suma(padded[n : n+M]) = sum_{k=0}^{M-1} x(n-k)
        cumsum = np.concatenate(([0.0], np.cumsum(datos_padded)))
        suma_ventana = cumsum[self.M:self.M + n] - cumsum[0:n]

        datos_filtrados = suma_ventana / self.M
        return datos_filtrados
