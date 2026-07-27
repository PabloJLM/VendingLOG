import os
import tkinter as tk
from tkinter import messagebox

from config import NAMES, PRICES, SKELETON, STOCK0
from editor import Editor
from estilos import CH, CW, load_themes
from logica import NO_IV, Sim, toolchain
from maquina import Maquina
from ondas import open_gtkwave


class App:
    def __init__(self, root):
        self.root = root
        self.themes = load_themes()
        self.tname = next((k for k in self.themes if "In the Pool" in k),
                          list(self.themes)[0])
        self.sim = self.state = None
        self.on = self.anim = False
        self.sel = self.tray = None
        self.stock = STOCK0[:]

        root.title("Expendedora Verilog")
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

    def _sel_bytes(self, i):
        return [{"b": 0x30 | i}, {"b": 0x50 | (1 if self.stock[i] > 0 else 0)}]

    def compilar(self):
        self.sim = Sim(self.editor.codigo())
        self.sel, self.tray, self.stock = None, None, STOCK0[:]
        self.editor.msg("Compilando y simulando...", "info")
        if self._correr():
            self.on = True
            self.editor.msg("Listooooo"
                            "Meter dinero y elegir", "ok")
        else:
            self.on = False
        self.maq.draw()

    def ficha(self, byte):
        self.sim.events.append({"b": byte})
        if not self._correr():
            self.sim.events.pop()
            return
        if self.state["error"]:
            self.editor.msg(f"Crédito: {self.state['credito']} — flag "
                            "ERROR: la suma se pasó de 7 (overflow evitado).",
                            "err")
        else:
            self.editor.msg(f"Crédito: {self.state['credito']}", "info")
        self.maq.draw()

    def elegir(self, i):
        self.sel = i
        self.sim.events.extend(self._sel_bytes(i))
        if self._correr():
            listo = "sí" if self.state["listo"] else "todavía no"
            self.editor.msg(f"Elegiste {NAMES[i]} ($ {PRICES[i]}). "
                            f"¿Alcanza el crédito?: {listo}.", "info")
        else:
            self.sim.events = self.sim.events[:-2]
        self.maq.draw()

    def comprar(self):
        if self.sel is None:
            self.editor.msg("selecciona un producto", "err")
            return
        i = self.sel
        self.sim.events.extend(self._sel_bytes(i))
        self.sim.events.append({"b": 0x40, "slot": i})
        if not self._correr():
            self.sim.events = self.sim.events[:-3]
            return
        if self.state["dispensed"][-1]:
            self._recontar()
            self.tray = i
            self.editor.msg(f"Entregado: {NAMES[i]}. "
                            f"Vuelto: {self.state['vuelto']}.", "ok")
            self.maq.draw()
            self.maq.caer(i)
            return
        motivo = "slot AGOTADO" if self.stock[i] == 0 else \
            f"crédito insuficiente ({self.state['credito']} < {PRICES[i]})"
        self.editor.msg(f"ERROR {motivo}. flag ERROR encendido "
                        "(resta negativa evitada). Tu dinero se conserva.",
                        "err")
        self.maq.draw()

    def retirar(self):
        if self.tray is not None:
            self.editor.msg(f"Retiraste {NAMES[self.tray]}. ¡Provecho!", "ok")
            self.tray = None
            self.maq.draw()

    def reiniciar(self):
        self.sim.events, self.sel, self.tray = [], None, None
        self.stock = STOCK0[:]
        self._correr()
        self.editor.msg("Reinicio hecho ", "info")
        self.maq.draw()

    def _recontar(self):
        self.stock = STOCK0[:]
        for e, d in zip(self.sim.events, self.state["dispensed"]):
            if d and "slot" in e:
                self.stock[e["slot"]] -= 1

    def esqueleto(self):
        self.editor.poner(open(SKELETON, encoding="utf-8").read())
        self.editor.msg("Codigo base cargado, termina tu .v jsj",
                        "info")

    def ondas(self):
        err = open_gtkwave(self.sim)
        if err:
            self.editor.msg(err, "err")
            return
        self.editor.msg("GTKWave abierto con la historia de tu sesión. "
                        "Mira el: 'dinero' sube con cada ficha (y se satura "
                        "en 7), 'motor_on' pulsa UN ciclo al comprar, y "
                        "'error' se enciende en overflow o resta negativa. "
                        "Cada click nuevo re-simula: reabre las Señales para "
                        "actualizar.", "info")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
