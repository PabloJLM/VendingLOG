import os
import shutil
import subprocess

from config import GTKWAVE_DIRS
from logica import FLAGS

NO_GTKWAVE = ("No esta gtkwwave hay que descargarlo")
#leo senales 
SENALES = """[dumpfile] "{vcd}" 
[size] 1100 650
@28
testbench.clk
testbench.rst
testbench.ficha_1
testbench.ficha_5
testbench.btn_comprar
testbench.hay_stock
@22
testbench.producto[3:0]
testbench.credito[2:0]
testbench.vuelto[2:0]
@28
testbench.listo
testbench.motor_on
testbench.error
"""


def find_gtkwave():
    if (g := shutil.which("gtkwave")):
        return g
    for d in GTKWAVE_DIRS:
        for exe in ("gtkwave.exe", "gtkwave"):
            p = os.path.join(d, exe)
            if os.path.isfile(p):
                return p
    return None


def open_gtkwave(sim):
    exe = find_gtkwave()
    if not exe:
        return NO_GTKWAVE
    if not (sim and os.path.isfile(sim.vcd)):
        return "Todavia no hay ondas: compila y usa la maquina primero."
    gtkw = os.path.join(sim.wd, "wave.gtkw")
    with open(gtkw, "w") as f:
        f.write(SENALES.format(vcd=sim.vcd.replace("\\", "\\\\")))
    subprocess.Popen([exe, sim.vcd, gtkw], cwd=sim.wd, creationflags=FLAGS)
    return None
