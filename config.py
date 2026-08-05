import os

BASE = os.path.dirname(os.path.abspath(__file__))

# Rutas ---------------------------------------------------------------
HDL      = os.path.join(BASE, "hdl")
IMG      = os.path.join(BASE, "img")
BG       = os.path.join(BASE, "bg")
TEMAS    = os.path.join(BASE, "temas.json")

# El estudiante completa esqueleto.v; control.v es la solucion (docente)
SKELETON = os.path.join(HDL, "esqueleto.v")
SOLUCION = os.path.join(HDL, "control.v")
RTL_FIJO = [os.path.join(HDL, "stepper.v"), os.path.join(HDL, "top.v")]

# ruta de Icarus Verilog
IVERILOG_DIRS = [r"C:\iverilog\bin", r"C:\Program Files\iverilog\bin"]

# GTKWave
GTKWAVE_DIRS = [
    os.path.join(BASE, "gtkwave64", "bin"),
    os.path.join(BASE, "gtkwave-3.3.100-bin-win64", "gtkwave64", "bin"),
    r"C:\gtkwave64\bin",
    r"C:\Program Files\GTKWave\bin",
]

# Los 3 colores de chicle (color 0, 1, 2 -> imagenes img/0.png, 1.png, 2.png)
NAMES = ["Rojo", "Verde", "Azul"]
