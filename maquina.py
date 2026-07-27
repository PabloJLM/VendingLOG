import tkinter as tk

from config import NAMES, PRICES
from estilos import (CELL_H, CELL_W, CH, CW, FUENTE_CHICA, FUENTE_LCD,
                     FUENTE_TITULO, FUENTE_UI, GAP, GX, GY, SELECCION, TRAY,
                     rrect)
import imagenes


class Maquina(tk.Canvas):
    def __init__(self, parent, app):
        super().__init__(parent, width=CW, height=CH, highlightthickness=0)
        self.app = app
        self.pack(expand=True)
        self.bind("<Button-1>", self._click)
        self.img, self.big = imagenes.cargar()
        self.hot = []

    def _celda(self, i):
        r, c = divmod(i, 3)
        return GX + c * (CELL_W + GAP), GY + r * (CELL_H + GAP)

    def _zona(self, x1, y1, x2, y2, cmd):
        self.hot.append((x1, y1, x2, y2, cmd))

    def _click(self, e):
        if not self.app.on or self.app.anim:
            return
        for x1, y1, x2, y2, cmd in self.hot:
            if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                cmd()
                return

    def _pill(self, x1, y1, x2, y2, txt, color, cmd, fg="#ffffff"):
        rrect(self, x1, y1, x2, y2, r=(y2 - y1) // 2, fill=color)
        self.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=txt, fill=fg,
                         font=FUENTE_UI)
        self._zona(x1, y1, x2, y2, cmd)

    def draw(self):
        a, t, st = self.app, self.app.T, self.app.state
        panel, edge = t["fondo_consola"], t["tab_sel"]
        acc, muted = a.hl("instrucciones"), a.hl("comentarios")
        self.configure(bg=t["fondo_app"])
        self.delete("all")
        self.hot = []

        if "fondo" in self.big:
            self.create_image(CW / 2, CH / 2, image=self.big["fondo"])
        else:
            rrect(self, 10, 10, CW - 10, CH - 10, r=26,
                  fill=t["fondo_editor"], outline=edge, width=2)
        self.create_text(CW / 2, 30, text="FIT XVII", fill=acc,
                         font=FUENTE_TITULO)

        rrect(self, GX, 48, GX + 250, 88, r=14, fill=panel, outline=edge)
        self.create_text(GX + 14, 68, anchor="w",
                         text=f"CREDITO {st['credito'] if st else 0}",
                         fill=a.hl("inmediatos"), font=FUENTE_LCD)
        self.create_text(GX + 140, 68, anchor="w",
                         text=f"VUELTO {st['vuelto'] if st else 0}",
                         fill=a.hl("registros"), font=FUENTE_LCD)
        self._led(GX + 276, "LISTO", a.hl("inmediatos"),
                  bool(st and st["listo"] and a.sel is not None), panel, edge, muted)
        self._led(GX + 320, "ERROR", a.hl("registros"),
                  bool(st and st["error"]), panel, edge, muted)

        for i in range(9):
            self._slot(i, panel, edge, acc, muted, t)

        self._pill(GX, 428, GX + 92, 462, "FICHA 1", a.hl("etiquetas"),
                   lambda: a.ficha(0x10))
        self._pill(GX + 100, 428, GX + 192, 462, "FICHA 5",
                   a.hl("registros"), lambda: a.ficha(0x20))
        self._pill(GX + 202, 428, CW - GX, 462, "COMPRAR",
                   a.hl("inmediatos"), a.comprar, fg=t["fondo_app"])

        self._bandeja(panel, edge, muted)

        self.create_text(CW - GX, CH - 22, anchor="e", text="reiniciar sesion",
                         fill=muted, font=("Segoe UI", 9, "underline"))
        self._zona(CW - GX - 110, CH - 34, CW - GX, CH - 10, a.reiniciar)

        if not a.on:
            rrect(self, 10, 10, CW - 10, CH - 10, r=26, fill=t["fondo_app"],
                  stipple="gray50", outline="")
            self.create_text(CW / 2, CH / 2 - 10, text="MAQUINA APAGADA",
                             fill=t["texto_editor"],
                             font=("Courier New", 14, "bold"))
            self.create_text(CW / 2, CH / 2 + 16, fill=muted,
                             font=("Segoe UI", 10),
                             text="Compila tu modulo y se encendera")

    def _led(self, x, texto, color, encendido, panel, edge, muted):
        self.create_oval(x, 52, x + 32, 84, fill=color if encendido else panel,
                         outline=edge, width=2)
        self.create_text(x + 16, 94, text=texto, fill=muted,
                         font=("Segoe UI", 7))

    def _slot(self, i, panel, edge, acc, muted, t):
        a = self.app
        x, y = self._celda(i)
        ok = a.stock[i] > 0
        if i == a.sel:
            rrect(self, x - 5, y - 5, x + CELL_W + 5, y + CELL_H + 5, r=18,
                  fill="", outline=SELECCION[0], width=3)
            rrect(self, x - 2, y - 2, x + CELL_W + 2, y + CELL_H + 2, r=16,
                  fill="", outline=SELECCION[1], width=1)
        rrect(self, x, y, x + CELL_W, y + CELL_H, r=14, fill=panel,
              outline=SELECCION[0] if i == a.sel else edge,
              width=2 if i == a.sel else 1)
        if i in self.img:
            self.create_image(x + CELL_W / 2, y + 32, image=self.img[i])
        else:
            rrect(self, x + 34, y + 10, x + CELL_W - 34, y + 50, r=10,
                  fill=a.hl("etiquetas") if ok else muted)
        if not ok:
            rrect(self, x + 2, y + 2, x + CELL_W - 2, y + 58, r=12,
                  fill=t["fondo_app"], stipple="gray50", outline="")
        self.create_text(x + CELL_W / 2, y + 64, text=NAMES[i],
                         fill=t["texto_editor"] if ok else muted,
                         font=("Segoe UI", 9))
        self.create_text(x + CELL_W / 2, y + 82,
                         text=f"Q {PRICES[i]}" if ok else "AGOTADO",
                         fill=a.hl("registros") if ok else muted,
                         font=("Segoe UI", 9, "bold"))
        self._zona(x, y, x + CELL_W, y + CELL_H, lambda: a.elegir(i))

    def _bandeja(self, panel, edge, muted):
        a = self.app
        bx = (TRAY[0] + TRAY[2]) / 2
        by = (TRAY[1] + TRAY[3]) / 2
        key = "bandeja_1" if a.tray is not None else "bandeja_0"
        if key in self.big:
            self.create_image(bx, by, image=self.big[key])
        else:
            rrect(self, *TRAY, r=20, fill=panel, outline=edge, width=2)
        if a.tray is not None and not a.anim:
            self._producto(bx, by - 8, a.tray)
            self.create_text(bx, TRAY[3] - 14, text="click para retirar",
                             fill=muted, font=FUENTE_CHICA)
        elif "bandeja_0" not in self.big:
            self.create_text(bx, TRAY[3] - 14, text="RETIRO", fill=muted,
                             font=FUENTE_CHICA)
        self._zona(*TRAY, a.retirar)

    def _producto(self, x, y, i):
        if i in self.img:
            self.create_image(x, y, image=self.img[i], tags="fall")
        else:
            rrect(self, x - 24, y - 14, x + 24, y + 14, r=10,
                  fill=self.app.hl("etiquetas"), outline="#ffffff",
                  tags="fall")

    def caer(self, slot):
        self.app.anim = True
        x0, y0 = (v + d for v, d in zip(self._celda(slot), (CELL_W / 2, 32)))
        x1 = (TRAY[0] + TRAY[2]) / 2
        y1 = (TRAY[1] + TRAY[3]) / 2 - 8

        def paso(n=0, pasos=20):
            self.delete("fall")
            if n > pasos:
                self.app.anim = False
                self.draw()
                return
            t = n / pasos
            self._producto(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t * t, slot)
            self.after(22, lambda: paso(n + 1))
        paso()
