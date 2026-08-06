import os
import tkinter as tk
from tkinter import messagebox

from config import NAMES, SKELETON
from editor import Editor
from estilos import CH, CW, load_themes
from logica import NO_IV, Sim, toolchain
from maquina import Maquina
from ondas import open_gtkwave

#prueba de cambio desde pc linux jsjs
class App:
    def __init__(self, root):
        self.root = root
        self.themes = load_themes()
        self.tname = next((k for k in self.themes if "In the Pool" in k),
                          list(self.themes)[0])
        self.sim = self.state = None
        self.on = self.anim = False
        self.sel = self.tray = self.motor_activo = None
        self.ultimo_exito = False

        root.title("Chiclera Verilog")
        root.geometry(f"{CW + 780}x{CH + 16}")
        izq = tk.Frame(root, width=CW + 10)
        izq.pack(side="left", fill="y")
        izq.pack_propagate(False)
        self.izq = izq
        self.maq = Maquina(izq, self)
        self.editor = Editor(root, self)
        if os.path.isfile(SKELETON):
            self.editor.poner(open(SKELETON, encoding="utf-8").read())
        self.cambiar_tema(self.tname)
        if not toolchain()[0]:
            root.after(300, lambda: messagebox.showwarning("Falta Icarus", NO_IV))

    @property
    def T(self):
        return self.themes[self.tname]

    def hl(self, k):
        return self.T["hl"].get(k, "#888888")

    def cambiar_tema(self, nombre):
        self.tname = nombre
        self.root.configure(bg=self.T["fondo_app"])
        self.izq.configure(bg=self.T["fondo_app"])
        self.editor.aplicar_tema(self.T, self.hl)
        self.editor.set_fondo_tema(self.T)
        self.maq.draw()

    def _correr(self):
        self.root.configure(cursor="watch")
        self.root.update_idletasks()
        try:
            res = self.sim.run()
        finally:
            self.root.configure(cursor="")
        if res["status"] != "ok":
            self.editor.msg(res["msg"], "err")
            return None
        self.state = res
        return res

    def compilar(self):
        self.sim = Sim(self.editor.codigo())
        self.sel = self.tray = self.motor_activo = None
        self.ultimo_exito = False
        self.editor.msg("Compilando...", "info")
        if self._correr():
            self.on = True
            self.editor.msg("Listo. Elegi un color y mete una moneda.", "ok")
        else:
            self.on = False
        self.maq.draw()

    def elegir(self, i):
        self.sel = i
        self.sim.events.append({"b": 0x30 | i})
        if self._correr():
            self.editor.msg(f"Color elegido: {NAMES[i]} ({i})", "info")
        else:
            self.sim.events.pop()
        self.maq.draw()

    def moneda(self):
        if self.sel is None:
            self.editor.msg("Elegi un color primero", "err")
            return
        self.sim.events.append({"b": 0x30 | self.sel})
        self.sim.events.append({"b": 0x10})
        if not self._correr():
            self.sim.events = self.sim.events[:-2]
            return
        motor = self.state["motor"][-1]
        exito = self.state["exito"][-1]
        self.ultimo_exito = exito
        if motor is not None and exito:
            self.tray = motor
            self.editor.msg(f"Salio un chicle {NAMES[motor]} "
                            f"(motor {motor + 1})", "ok")
            self.maq.draw()
            self.maq.caer(motor)
            return
        if motor is not None:
            self.editor.msg(f"El motor {motor + 1} giro pero el led de "
                            "exito nunca prendio. Revisa el estado EXITO.",
                            "err")
        else:
            self.editor.msg("Ningun motor arranco. Revisa tu FSM "
                            "(estado INICIO y el case de color).", "err")
        self.maq.draw()

    def retirar(self):
        if self.tray is not None:
            self.editor.msg(f"Retiraste el chicle {NAMES[self.tray]}", "ok")
            self.tray = None
            self.maq.draw()

    def reiniciar(self):
        self.sim.events = []
        self.sel = self.tray = self.motor_activo = None
        self.ultimo_exito = False
        self._correr()
        self.editor.msg("Sesion reiniciada", "info")
        self.maq.draw()

    def esqueleto(self):
        self.editor.poner(open(SKELETON, encoding="utf-8").read())
        self.editor.msg("Esqueleto cargado: completa los TODO", "info")

    def ondas(self):
        err = open_gtkwave(self.sim)
        if err:
            self.editor.msg(err, "err")
            return
        self.editor.msg("GTKWave abierto. Volve a apretar Senales "
                        "para ver los cambios mas recientes.", "info")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
