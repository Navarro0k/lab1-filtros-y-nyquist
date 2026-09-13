class NyquistAnalyzer:
    def check(self, fs: int, f_max: float) -> bool:
        nyquist_freq = fs / 2.0
        cumple_nyquist = nyquist_freq >= f_max
        return cumple_nyquist

    def resample(self, x, fs: int, new_fs: int):
        if len(x) == 0 or fs == new_fs:
            return x

        N = len(x)
        n_muestras_nuevas = int(round(N * new_fs / fs))
        
        y = []

        for i in range(n_muestras_nuevas):
            indice_original = int(i * N / n_muestras_nuevas)
            
            if indice_original >= N:
                indice_original = N - 1
                
            y.append(x[indice_original])

        return y