import os

BASE = os.path.dirname(os.path.abspath(__file__))

# Rutas (cambiá acá si movés carpetas)
HDL      = os.path.join(BASE, "hdl")
IMG      = os.path.join(BASE, "img")
TEMAS    = os.path.join(BASE, "temas.json")
SKELETON = os.path.join(HDL, "skeleton.v")

# Icarus Verilog en Windows (si no está en el PATH)
IVERILOG_DIRS = [r"C:\iverilog\bin", r"C:\Program Files\iverilog\bin"]

# GTKWave (opcional). Si lo copiás dentro del proyecto, su carpeta bin:
GTKWAVE_DIRS = [
    os.path.join(BASE, "gtkwave64", "bin"),
    os.path.join(BASE, "gtkwave-3.3.100-bin-win64", "gtkwave64", "bin"),
    r"C:\gtkwave64\bin",
    r"C:\Program Files\GTKWave\bin",
]

# Productos por slot (0..8). Los precios deben coincidir con el case
# del Verilog del estudiante.
NAMES  = ["Chips", "Galletas", "Soda", "Chicle", "Agua",
          "Chocolate", "Café", "Caramelo", "Jugo"]
PRICES = [2, 3, 5, 1, 4, 7, 6, 2, 3]
STOCK0 = [3, 2, 2, 3, 1, 2, 0, 3, 2]

# Imágenes en img/ (opcionales): fondo.png (~460x680), 0.png..8.png,
# bandeja_0.png y bandeja_1.png (~250x120)
