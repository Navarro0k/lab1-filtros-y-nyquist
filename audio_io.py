"""
audio_io.py

Encapsula la grabacion y reproduccion de audio usando la libreria
'sounddevice'. Si no hay un microfono/dispositivo de entrada real
disponible (por ejemplo al correr en un servidor o contenedor sin
audio), cae en un modo "simulado" que genera una senal de prueba,
para que el resto del pipeline (filtrado, analisis, graficas) se
pueda seguir probando igual. El modo simulado queda claramente
marcado (self.ultimo_modo_simulado) para que la interfaz pueda
avisarle al usuario.
"""

import time
import numpy as np

try:
    import sounddevice as sd
    _SOUNDDEVICE_IMPORTABLE = True
except Exception:
    _SOUNDDEVICE_IMPORTABLE = False


class AudioIO:
    """
    Interfaz de entrada/salida de audio.

    Atributos
    ---------
    channels : int
        Numero de canales de audio (1 = mono, 2 = estereo).
    ultimo_modo_simulado : bool
        True si la ultima llamada a record() tuvo que usar la senal
        simulada (no se detecto/uso un microfono real).
    """

    def __init__(self, channels: int = 1):
        self.channels = channels
        self.ultimo_modo_simulado = False

    # ------------------------------------------------------------------
    def _hay_dispositivo_de_entrada(self) -> bool:
        """
        Verifica, de forma defensiva, si hay un dispositivo de entrada
        de audio disponible antes de intentar grabar.
        """
        if not _SOUNDDEVICE_IMPORTABLE:
            return False
        try:
            dispositivos = sd.query_devices()
            return any(d.get("max_input_channels", 0) > 0 for d in dispositivos)
        except Exception:
            return False

    # ------------------------------------------------------------------
    def record(self, duration: float, fs: int) -> np.ndarray:
        """
        Graba audio desde el microfono por 'duration' segundos a 'fs' Hz.

        Parametros
        ----------
        duration : float
            Duracion de la grabacion en segundos.
        fs : int
            Frecuencia de muestreo en Hz.

        Retorna
        -------
        datos : np.ndarray
            Arreglo 1D (si channels == 1) con las muestras grabadas.
            Si no hay hardware de audio disponible o la grabacion real
            falla, retorna una senal sintetica (tono + ruido) de la
            MISMA duracion solicitada (respetando el tiempo pedido), y
            deja marcado self.ultimo_modo_simulado = True.
        """
        n_muestras = int(round(duration * fs))
        self.ultimo_modo_simulado = False

        if self._hay_dispositivo_de_entrada():
            try:
                print(f"[AudioIO] Grabando {duration} s a {fs} Hz...")
                grabacion = sd.rec(
                    n_muestras, samplerate=fs, channels=self.channels, dtype="float64"
                )
                sd.wait()
                datos = grabacion.flatten() if self.channels == 1 else grabacion
                print("[AudioIO] Grabacion finalizada.")
                return datos
            except Exception as e:
                print(f"[AudioIO] Error al grabar con el dispositivo real: {e}. "
                      f"Se usara una senal simulada.")

        # Modo simulado: no hay microfono disponible o fallo la grabacion real.
        # Se respeta la duracion solicitada (no debe terminar antes de tiempo).
        print(
            "[AudioIO] Aviso: no se detecto un microfono/dispositivo de entrada "
            "utilizable. Generando senal simulada."
        )
        self.ultimo_modo_simulado = True
        time.sleep(max(duration, 0.0))

        t = np.linspace(0, duration, n_muestras, endpoint=False)
        tono = 0.6 * np.sin(2 * np.pi * 440 * t)  # tono de prueba, La4 (440 Hz)
        ruido = 0.05 * np.random.randn(n_muestras)
        datos = tono + ruido
        return datos

    # ------------------------------------------------------------------
    def play(self, datos: np.ndarray, fs: int) -> None:
        """
        Reproduce una senal de audio.

        Parametros
        ----------
        datos : np.ndarray
            Senal a reproducir.
        fs : int
            Frecuencia de muestreo en Hz.
        """
        datos = np.asarray(datos)

        if _SOUNDDEVICE_IMPORTABLE:
            try:
                print(f"[AudioIO] Reproduciendo senal a {fs} Hz...")
                sd.play(datos, samplerate=fs)
                sd.wait()
                print("[AudioIO] Reproduccion finalizada.")
                return
            except Exception as e:
                print(f"[AudioIO] Error al reproducir con el dispositivo real: {e}.")

        print(
            "[AudioIO] Aviso: no se pudo reproducir con un dispositivo real. "
            f"Se omite reproduccion de {len(datos)} muestras a {fs} Hz."
        )
