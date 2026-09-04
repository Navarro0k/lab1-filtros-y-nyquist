## Informe del Laboratorio

Puedes consultar el informe detallado de este laboratorio en el siguiente enlace:

📄 [Ver el Informe en Google Docs](https://docs.google.com/document/d/1uvJHZgIx_z8_txHnFeki3ycri_8WqPCX21Uvqm2-6p0/edit?usp=sharing)
## Diagrama de Clases

```mermaid
classDiagram
    class AudioIO {
        +channels
        +record(duration, fs) datos
        +play(datos, fs)
    }
    class MovingAverageFilter {
        +M
        +apply(datos, fs) datos_filtrados
    }
    class NyquistAnalyzer {
        +check(datos, fs, f_max) bool
        +resample(datos, fs, new_fs) datos
    }
    class SignalPlotter {
        +plot_comparison(orig, filt)
        +plot_spectrum(datos, fs)
    }
    class LabController {
        -io
        -filtro
        -analyzer
        -plotter
        +run_parte1()
        +run_parte2()
    }
    LabController --> AudioIO
    LabController --> MovingAverageFilter
    LabController --> NyquistAnalyzer
    LabController --> SignalPlotter
```

## Diagrama de Secuencia Parte 1: Filtrado de Promedio Móvil
```mermaid
sequenceDiagram
    autonumber
    actor Main as main.py
    participant LC as LabController
    participant AIO as AudioIO
    participant MAF as MovingAverageFilter
    participant SP as SignalPlotter

    Main->>LC: run_parte1()
    activate LC

    LC->>AIO: record(duration, fs)
    activate AIO
    AIO-->>LC: datos
    deactivate AIO

    LC->>MAF: apply(datos, fs)
    activate MAF
    MAF-->>LC: datos_filtrados
    deactivate MAF

    LC->>SP: plot_comparison(datos, datos_filtrados)
    activate SP
    SP-->>LC: 
    deactivate SP

    LC->>AIO: play(datos_filtrados, fs)
    activate AIO
    AIO-->>LC: 
    deactivate AIO

    deactivate LC
```

##  Diagrama de secuencia Parte 2: Análisis de Nyquist y Submuestreo
```mermaid
sequenceDiagram
    autonumber
    actor Main as main.py
    participant LC as LabController
    participant AIO as AudioIO
    participant NA as NyquistAnalyzer
    participant SP as SignalPlotter

    Main->>LC: run_parte2()
    activate LC

    LC->>AIO: record(duration, fs)
    activate AIO
    AIO-->>LC: datos
    deactivate AIO

    LC->>NA: check(datos, fs, f_max)
    activate NA
    NA-->>LC: cumple_nyquist
    deactivate NA

    LC->>NA: resample(datos, fs, new_fs)
    activate NA
    NA-->>LC: datos_resampleados
    deactivate NA

    LC->>SP: plot_spectrum(datos_resampleados, new_fs)
    activate SP
    SP-->>LC: 
    deactivate SP

    LC->>AIO: play(datos_resampleados, new_fs)
    activate AIO
    AIO-->>LC: 
    deactivate AIO

    deactivate LC
```
