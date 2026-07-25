# Vending Verilog — simulador híbrido educativo

Dos ventanas: LA MÁQUINA (imagen de fondo, productos con imagen,
bandeja de retiro que cambia según la lógica) y el EDITOR (código
Verilog + consola + temas del mismo `temas.json` del JoJoP IDE).

Cada click re-simula toda la historia con Icarus Verilog (batch
replay): lo que se ve es el estado real del hardware del estudiante.

## Interfaz Verilog (simplificada)

La máquina le pasa al módulo el `precio` y `hay_stock` del producto
elegido; el estudiante solo diseña la lógica del dinero (~15 líneas):
saturación del crédito en 7, `listo`, comprar validando ANTES de
restar, `vuelto`, y conservar el crédito si no se puede comprar.
El stock y la grilla los maneja la GUI.

## Instalación (Windows)

1. Python 3.10+ (python.org, "Add to PATH").
2. Icarus Verilog: https://bleyer.org/icarus/ ("agregar al PATH").
3. Opcional: `pip install pillow` (jpg y mejor escalado).
4. `python app.py`

## Archivos

| Archivo | Qué es |
|---|---|
| `app.py` | Toda la aplicación (2 ventanas + motor de simulación) |
| `temas.json` | Temas (mismo formato que el IDE; editable) |
| `hdl/testbench.v` | Testbench fijo (el estudiante no lo ve) |
| `hdl/skeleton.v` | Esqueleto que completa el estudiante |
| `hdl/solucion.v` | **Solución — no distribuir** |
| `img/` | fondo.png, 0..8.png, bandeja_0/1.png (ver img/LEEME.txt) |

## Constantes (en app.py: PRICES / STOCK0 / NAMES)

```
slot   :  0  1  2  3  4  5  6  7  8
precio :  2  3  5  1  4  7  6  2  3
stock  :  3  2  2  3  1  2  0  3  2   (slot 6 agotado a propósito)
```

## Robustez

Timeouts de compilación (20 s) y simulación (10 s) + watchdog en el
testbench; errores de iverilog traducidos con línea y pista; aviso
claro si falta iverilog; autoguardado en `student_work.v`.

## Para el docente

- Ondas: `vvp sim.vvp +vcd` → `wave.vcd` (GTKWave).
- La clase `Sim` (eventos → run → dict) es el contrato a reutilizar
  como backend cuando se pase a Unity.
