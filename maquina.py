import tkinter as tk

from config import NAMES
from estilos import (BOTON_Y, CENTRO, CH, CONT_GAP, CONT_H, CONT_W, CONT_Y,
                     CW, FAM_MONO, FAM_UI, FUENTE_CHICA, FUENTE_TITULO,
                     FUENTE_UI, MOTOR_H, SELECCION, TOLVA_H, TOLVA_W, TRAY,
                     TUBO_W, rrect)
import imagenes

COLORES = ["#e74c3c", "#2ecc71", "#3498db"]


class Maquina(tk.Canvas):
    def __init__(self, parent, app):
        super().__init__(parent, width=CW, height=CH, highlightthickness=0)
        self.app = app
        self.pack(expand=True)
        self.bind("<Button-1>", self._click)
        self.img, self.big = imagenes.cargar()
        self.frame = 0
        self.hot = []
        self._cargar_piezas()

    # Rampas y tubo: dependen de la geometria, se cargan una sola vez
    def _cargar_piezas(self):
        self.piezas = {}
        cx, cy = CENTRO
        for i in range(3):
            sx, sy = self._salida(i)
            w = max(int(abs(cx - sx)) + 24, 30)
            h = max(int(cy - sy), 20)
            if (r := imagenes.cargar_pieza(f"rampa_{i}", (w, h))):
                self.piezas[f"rampa_{i}"] = r
        alto = int(TRAY[1] - (cy + TOLVA_H / 2 - 6))
        if alto > 6 and (r := imagenes.cargar_pieza("tubo", (TUBO_W, alto))):
            self.piezas["tubo"] = r

    def _cont(self, i):
        total = 3 * CONT_W + 2 * CONT_GAP
        x = (CW - total) / 2 + i * (CONT_W + CONT_GAP)
        return x, CONT_Y, x + CONT_W, CONT_Y + CONT_H

    def _salida(self, i):
        x1, y1, x2, y2 = self._cont(i)
        return (x1 + x2) / 2, y2 + MOTOR_H + 6

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
        a, t = self.app, self.app.T
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
        self.create_text(CW / 2, 32, text="vending jsjs", fill=acc,
                         font=FUENTE_TITULO)

        self._rampas(edge, muted)
        for i in range(3):
            self._contenedor(i, panel, edge, muted, t)

        self._bandeja(panel, edge, muted)
        self._pill(66, BOTON_Y, 286, BOTON_Y + 36, "METER MONEDA",
                   a.hl("inmediatos"), a.moneda, fg=t["fondo_app"])
        self._led(330, BOTON_Y + 3, "EXITO", a.hl("inmediatos"),
                  a.ultimo_exito, panel, edge, muted)

        self.create_text(CW - 26, 32, anchor="e", text="reiniciar",
                         fill=muted, font=(FAM_UI, 9, "underline"))
        self._zona(CW - 90, 20, CW - 22, 44, a.reiniciar)

        if not a.on:
            rrect(self, 10, 10, CW - 10, CH - 10, r=26, fill=t["fondo_app"],
                  stipple="gray50", outline="")
            self.create_text(CW / 2, CH / 2 - 10, text="MAQUINA APAGADA",
                             fill=t["texto_editor"],
                             font=(FAM_MONO, 14, "bold"))
            self.create_text(CW / 2, CH / 2 + 16, fill=muted,
                             font=(FAM_UI, 10),
                             text="Compila tu control.v y se encendera")

    def _rampas(self, edge, muted):
        cx, cy = CENTRO
        for i in range(3):
            sx, sy = self._salida(i)
            pieza = self.piezas.get(f"rampa_{i}")
            if pieza:
                self.create_image((sx + cx) / 2, (sy + cy) / 2, image=pieza)
            else:
                self.create_line(sx, sy, cx, cy, fill=edge, width=6,
                                 capstyle="round")
                self.create_line(sx, sy, cx, cy, fill=muted, width=2,
                                 capstyle="round")
        if (tubo := self.piezas.get("tubo")):
            top = cy + TOLVA_H / 2 - 6
            self.create_image(cx, (top + TRAY[1]) / 2, image=tubo)
        else:
            self.create_line(cx, cy + 26, cx, TRAY[1], fill=edge, width=3)
        if "tolva" in self.big:
            self.create_image(cx, cy, image=self.big["tolva"])
        else:
            self.create_polygon(cx - 34, cy - 12, cx + 34, cy - 12,
                                cx + 13, cy + 26, cx - 13, cy + 26,
                                fill="", outline=edge, width=3)

    def _contenedor(self, i, panel, edge, muted, t):
        a = self.app
        x1, y1, x2, y2 = self._cont(i)
        sel = (i == a.sel)
        if sel:
            rrect(self, x1 - 5, y1 - 5, x2 + 5, y2 + MOTOR_H + 5, r=20,
                  fill="", outline=SELECCION[0], width=3)
            rrect(self, x1 - 2, y1 - 2, x2 + 2, y2 + MOTOR_H + 2, r=18,
                  fill="", outline=SELECCION[1], width=1)
        rrect(self, x1, y1, x2, y2, r=14, fill=panel,
              outline=SELECCION[0] if sel else edge, width=2 if sel else 1)

        cx = (x1 + x2) / 2
        for dx, dy in ((-24, 40), (24, 40), (0, 78), (-24, 112), (24, 112)):
            if i in self.img:
                self.create_image(cx + dx, y1 + dy, image=self.img[i])
            else:
                self.create_oval(cx + dx - 17, y1 + dy - 17,
                                 cx + dx + 17, y1 + dy + 17,
                                 fill=COLORES[i], outline="")
        self.create_text(cx, y1 + 16, text=f"{NAMES[i]}  (color {i})",
                         fill=t["texto_editor"], font=(FAM_UI, 9, "bold"))

        my1, my2 = y2, y2 + MOTOR_H
        girando = (a.motor_activo == i)
        if not self._tiene_motor_img():
            rrect(self, x1 + 14, my1, x2 - 14, my2, r=10,
                  fill=a.hl("registros") if girando else panel,
                  outline=edge, width=1)
            self.create_text(cx, (my1 + my2) / 2, text=f"STEPPER {i + 1}",
                             fill=t["fondo_app"] if girando else muted,
                             font=(FAM_UI, 8, "bold"))
        else:
            self._motor(i, self.frame if girando else 0)
        self._zona(x1, y1, x2, my2, lambda: a.elegir(i))

    def _tiene_motor_img(self):
        return "stepper_1" in self.big

    def _motor(self, i, frame):
        img = self.big.get(f"stepper_{frame + 1}") or self.big.get("stepper_1")
        if not img:
            return
        x1, _, x2, y2 = self._cont(i)
        self.create_image((x1 + x2) / 2, y2 + MOTOR_H / 2, image=img,
                          tags=f"motor{i}")

    def _led(self, x, y, texto, color, encendido, panel, edge, muted):
        self.create_oval(x, y, x + 30, y + 30,
                         fill=color if encendido else panel,
                         outline=edge, width=2)
        self.create_text(x + 15, y + 40, text=texto, fill=muted,
                         font=(FAM_UI, 7))

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
            self._bola(bx, by - 6, a.tray)
            self.create_text(bx, TRAY[3] - 12, text="click para retirar",
                             fill=muted, font=FUENTE_CHICA)
        elif "bandeja_0" not in self.big:
            self.create_text(bx, TRAY[3] - 12, text="RETIRO", fill=muted,
                             font=FUENTE_CHICA)
        self._zona(*TRAY, a.retirar)

    def _bola(self, x, y, i):
        if i in self.img:
            self.create_image(x, y, image=self.img[i], tags="fall")
        else:
            self.create_oval(x - 17, y - 17, x + 17, y + 17,
                             fill=COLORES[i], outline="#ffffff", tags="fall")

    def caer(self, i):
        self.app.anim = True
        self.app.motor_activo = i
        sx, sy = self._salida(i)
        cx, cy = CENTRO
        tx = (TRAY[0] + TRAY[2]) / 2
        ty = (TRAY[1] + TRAY[3]) / 2 - 6

        def paso(n=0, pasos=30):
            self.delete("fall")
            if n > pasos:
                self.app.anim = False
                self.app.motor_activo = None
                self.draw()
                return
            if self._tiene_motor_img() and n % 3 == 0:
                self.frame ^= 1
                self.delete(f"motor{i}")
                self._motor(i, self.frame)
            t = n / pasos
            if t < 0.55:
                u = t / 0.55
                x, y = sx + (cx - sx) * u, sy + (cy - sy) * u
            else:
                u = (t - 0.55) / 0.45
                x, y = cx + (tx - cx) * u, cy + (ty - cy) * u * u
            self._bola(x, y, i)
            self.after(22, lambda: paso(n + 1))
        paso()
