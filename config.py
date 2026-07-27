import os

BASE = os.path.dirname(os.path.abspath(__file__))

# Rutasn---------------------------------------------------------------------------------------
HDL      = os.path.join(BASE, "hdl")
IMG      = os.path.join(BASE, "img")
BG       = os.path.join(BASE, "bg")
TEMAS    = os.path.join(BASE, "temas.json")
SKELETON = os.path.join(HDL, "base.v")

# ruta de Icarus Verilog 
IVERILOG_DIRS = [r"C:\iverilog\bin", r"C:\Program Files\iverilog\bin"]

# GTKWave 
GTKWAVE_DIRS = [
    os.path.join(BASE, "gtkwave64", "bin"),
    os.path.join(BASE, "gtkwave-3.3.100-bin-win64", "gtkwave64", "bin"),
    r"C:\gtkwave64\bin",
    r"C:\Program Files\GTKWave\bin",
]

# Productos por slot (0..8). Los precios deben coincidir con el case del .v
NAMES  = ["Chips", "Galletas", "Soda", "Chicle", "Agua",
          "Chocolate", "Café", "Caramelo", "Jugo"]
PRICES = [2, 3, 5, 1, 4, 7, 6, 2, 3]
STOCK0 = [3, 2, 2, 3, 1, 2, 0, 3, 2]
