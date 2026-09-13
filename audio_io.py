import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None

class AudioIO:
    def __init__(self, channels: int = 1):
        self.channels = channels

    def record(self, duration: float, fs: int) -> np.ndarray:
        if not sd:
            raise RuntimeError("La librería sounddevice no está instalada.")
            
        n_muestras = int(duration * fs)
        
        grabacion = sd.rec(n_muestras, samplerate=fs, channels=self.channels, dtype="float64")
        sd.wait()
        
        return grabacion.flatten() if self.channels == 1 else grabacion

    def play(self, datos: np.ndarray, fs: int) -> None:
        if sd:
            sd.play(np.asarray(datos), samplerate=fs)
            sd.wait()