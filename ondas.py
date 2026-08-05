import os
import shutil
import subprocess

from config import GTKWAVE_DIRS
from logica import FLAGS

NO_GTKWAVE = ("No esta GTKWave: copialo dentro del proyecto o "
              "descargalo (ver GTKWAVE_DIRS en config.py)")

SENALES = """[dumpfile] "{vcd}"
[size] 1100 650
@28
testbench.clk
testbench.rst
testbench.sensor_entrada
testbench.sensor_salida
@22
testbench.color[1:0]
testbench.dut.u_control.estado_actual[1:0]
@28
testbench.dut.inicio1
testbench.dut.inicio2
testbench.dut.inicio3
testbench.ocupado1
testbench.ocupado2
testbench.ocupado3
testbench.paso_pin1
testbench.paso_pin2
testbench.paso_pin3
testbench.led
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
