# Vending Verilog — simulador híbrido educativo

Una sola ventana (maximizable): a la izquierda LA MÁQUINA (imagen de
fondo, productos con imagen, halo amarillo en el slot elegido, bandeja
de retiro que cambia según la lógica) y a la derecha el EDITOR (código
Verilog + consola + temas de `temas.json`).

Cada click re-simula toda la historia con Icarus Verilog (batch
replay): lo que se ve es el estado real del hardware del estudiante.

## Interfaz Verilog (simplificada)

La máquina le pasa al módulo el número de `producto` (0-8) y
`hay_stock`; el estudiante escribe: el **case de precios** (producto 2
= Soda vale 5 → resta 5, y así con cada uno), las fichas con
saturación en 7, la compra validando ANTES de restar, y el **flag
`error`**: se enciende si una suma haría overflow (se satura en 7) o
si una compra intentaría una resta negativa / no hay stock. El crédito
siempre se conserva ante un error. El stock lo maneja la GUI.

## Instalación (Windows)

1. Python 3.10+ (python.org, "Add to PATH").
2. Icarus Verilog: https://bleyer.org/icarus/ ("agregar al PATH").
3. Opcional: `pip install pillow` (jpg y mejor escalado).
4. `python app.py`

## Archivos

| Archivo | Qué es |
|---|---|
| `app.py` | Sesión y acciones — **se ejecuta este** |
| `maquina.py` | Canvas de la vending (grilla, halo, bandeja, animación) |
| `editor.py` | Editor de código + consola + selector de tema |
| `logica.py` | Motor de simulación (iverilog/vvp, errores, timeouts) |
| `ondas.py` | Visor de señales (GTKWave) |
| `imagenes.py` | Carga de imágenes con aspect ratio |
| `estilos.py` | Temas, fuentes, layout, formas |
| `config.py` | Rutas, precios, nombres, stock — **lo que se cambia está acá** |
| `temas.json` | Temas: Básicos + In the Pool (editable) |
| `hdl/testbench.v` | Testbench fijo (el estudiante no lo ve) |
| `hdl/skeleton.v` | Esqueleto que completa el estudiante |
| `hdl/solucion.v` | **Solución — no distribuir** |
| `img/` | fondo.png, 0..8.png, bandeja_0/1.png (ver img/LEEME.txt) |

El código del estudiante se compila desde el editor a una carpeta
temporal: no queda ningún archivo de trabajo en el proyecto.

## Constantes (config.py: PRICES / STOCK0 / NAMES)

```
slot   :  0  1  2  3  4  5  6  7  8
precio :  2  3  5  1  4  7  6  2  3
stock  :  3  2  2  3  1  2  0  3  2   (slot 6 agotado a propósito)
```

## Robustez

Timeouts de compilación (20 s) y simulación (10 s) + watchdog en el
testbench; errores de iverilog traducidos con línea y pista; aviso
claro si falta iverilog o GTKWave, sin romperse.

## Visor de señales (GTKWave, opcional)

Botón **Señales**: abre GTKWave con la historia completa de la sesión
y las señales precargadas en orden didáctico (clk, fichas, producto,
credito, listo, motor_on, vuelto, error). GTKWave puede ir embebido en
el proyecto (ver `GTKWAVE_DIRS` en config.py).

## Para el docente

La clase `Sim` de logica.py (eventos → run → dict) es el contrato a
reutilizar como backend cuando se pase a Unity.
