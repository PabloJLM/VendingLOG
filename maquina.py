import tkinter as tk

from config import NAMES
from estilos import (BOTON_Y, CENTRO, CH, CONT_GAP, CONT_H, CONT_W, CONT_Y,
                     CW, FAM_MONO, FAM_UI, MOTOR_H, SELECCION, TOLVA_H,
                     TOLVA_W, TRAY, TUBO_W, rrect)
import imagenes

COLORES = ["#e74c3c", "#2ecc71", "#3498db"]


class Maquina(tk.Canvas):
    def __init__(self, parent, app):
        super().__init__(parent, width=CW, height=CH, highlightthickness=0)
        self.app = app
        self.pack(fill="both", expand=True)
        self.bind("<Button-1>", self._click)
        self.bind("<Configure>", self._resize)
        self.k = 1.0
        self.ox = self.oy = 0
        self.frame = 0
        self.hot = []
        self.img, self.big = imagenes.cargar(self.k)
        self.piezas = {}
        self._cargar_piezas()

    # El dibujo se define en coordenadas base CW x CH y se escala al
    # tamano real del panel, centrandolo.
    def _resize(self, e):
        k = min(e.width / CW, e.height / CH)
        if k <= 0:
            return
        self.ox = (e.width - CW * k) / 2
        self.oy = (e.height - CH * k) / 2
        if abs(k - self.k) > 0.02:
            self.k = k
            self.img, self.big = imagenes.cargar(k)
            self._cargar_piezas()
        self.draw()

    def px(self, x):
        return x * self.k + self.ox

    def py(self, y):
        return y * self.k + self.oy

    def s(self, v):
        return v * self.k

    def f(self, familia, tam, *estilo):
        return (familia, max(6, int(tam * self.k)), *estilo)

    def _cargar_piezas(self):
        self.piezas = {}
        cx, cy = CENTRO
        for i in range(3):
            sx, sy = self._salida(i)
            w = max(int(self.s(abs(cx - sx) + 30)), 12)
            h = max(int(self.s(cy - sy)), 12)
            if (r := imagenes.cargar_pieza(f"rampa_{i}", (w, h))):
                self.piezas[f"rampa_{i}"] = r
        alto = int(self.s(TRAY[1] - (cy + TOLVA_H / 2 - 6)))
        ancho = max(int(self.s(TUBO_W)), 8)
        if alto > 6 and (r := imagenes.cargar_pieza("tubo", (ancho, alto))):
            self.piezas["tubo"] = r

    def _cont(self, i):
        total = 3 * CONT_W + 2 * CONT_GAP
        x = (CW - total) / 2 + i * (CONT_W + CONT_GAP)
        return x, CONT_Y, x + CONT_W, CONT_Y + CONT_H

    def _salida(self, i):
        x1, y1, x2, y2 = self._cont(i)
        return (x1 + x2) / 2, y2 + MOTOR_H + 6

    def _zona(self, x1, y1, x2, y2, cmd):
        self.hot.append((self.px(x1), self.py(y1),
                         self.px(x2), self.py(y2), cmd))

    def _click(self, e):
        if not self.app.on or self.app.anim:
            return
        for x1, y1, x2, y2, cmd in self.hot:
            if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                cmd()
                return

    def _rr(self, x1, y1, x2, y2, r=16, **kw):
        if "width" in kw:
            kw["width"] = max(1, int(self.s(kw["width"])))
        return rrect(self, self.px(x1), self.py(y1), self.px(x2),
                     self.py(y2), r=self.s(r), **kw)

    def _pill(self, x1, y1, x2, y2, txt, color, cmd, fg="#ffffff"):
        self._rr(x1, y1, x2, y2, r=(y2 - y1) / 2, fill=color)
        self.create_text(self.px((x1 + x2) / 2), self.py((y1 + y2) / 2),
                         text=txt, fill=fg, font=self.f(FAM_UI, 10, "bold"))
        self._zona(x1, y1, x2, y2, cmd)

    def draw(self):
        a, t = self.app, self.app.T
        panel, edge = t["fondo_consola"], t["tab_sel"]
        acc, muted = a.hl("instrucciones"), a.hl("comentarios")
        self.configure(bg=t["fondo_app"])
        self.delete("all")
        self.hot = []

        if "fondo" in self.big:
            self.create_image(self.px(CW / 2), self.py(CH / 2),
                              image=self.big["fondo"])
        else:
            self._rr(10, 10, CW - 10, CH - 10, r=26,
                     fill=t["fondo_editor"], outline=edge, width=2)
        self.create_text(self.px(CW / 2), self.py(32), text="Simulador",
                         fill=acc, font=self.f(FAM_MONO, 16, "bold"))

        self._rampas(edge, muted)
        for i in range(3):
            self._contenedor(i, panel, edge, muted, t)

        self._bandeja(panel, edge, muted)
        self._pill(CW * 0.11, BOTON_Y, CW * 0.62, BOTON_Y + 46,
                   "METER MONEDA", a.hl("inmediatos"), a.moneda,
                   fg=t["fondo_app"])
        self._led(CW * 0.72, BOTON_Y + 4, "LED", a.hl("inmediatos"),
                  a.ultimo_exito, panel, edge)

        self.create_text(self.px(CW - 26), self.py(32), anchor="e",
                         text="reiniciar", fill=muted,
                         font=self.f(FAM_UI, 9, "underline"))
        self._zona(CW - 100, 20, CW - 22, 46, a.reiniciar)

        if not a.on:
            self._rr(10, 10, CW - 10, CH - 10, r=26, fill=t["fondo_app"],
                     stipple="gray50", outline="")
            self.create_text(self.px(CW / 2), self.py(CH / 2 - 10),
                             text="MAQUINA APAGADA", fill=t["texto_editor"],
                             font=self.f(FAM_MONO, 15, "bold"))
            self.create_text(self.px(CW / 2), self.py(CH / 2 + 18),
                             fill=muted, font=self.f(FAM_UI, 10),
                             text="Compila tu control.v y se encendera")

    def _rampas(self, edge, muted):
        cx, cy = CENTRO
        for i in range(3):
            sx, sy = self._salida(i)
            if (pieza := self.piezas.get(f"rampa_{i}")):
                self.create_image(self.px((sx + cx) / 2),
                                  self.py((sy + cy) / 2), image=pieza)
            else:
                self._tubo_dibujado(sx, sy, cx, cy, edge, muted)
        if (tubo := self.piezas.get("tubo")):
            top = cy + TOLVA_H / 2 - 6
            self.create_image(self.px(cx), self.py((top + TRAY[1]) / 2),
                              image=tubo)
        else:
            self._tubo_dibujado(cx, cy + TOLVA_H / 2 - 6, cx, TRAY[1],
                                edge, muted)
        if "tolva" in self.big:
            self.create_image(self.px(cx), self.py(cy),
                              image=self.big["tolva"])
        else:
            w, h = TOLVA_W / 2, TOLVA_H / 2
            self.create_polygon(
                self.px(cx - w), self.py(cy - h), self.px(cx + w),
                self.py(cy - h), self.px(cx + w * 0.3), self.py(cy + h),
                self.px(cx - w * 0.3), self.py(cy + h),
                fill=edge, outline=muted, width=max(1, int(self.s(2))))

    # Tubo dibujado: pared gruesa + interior claro (cuando no hay imagen)
    def _tubo_dibujado(self, x1, y1, x2, y2, edge, muted):
        p = (self.px(x1), self.py(y1), self.px(x2), self.py(y2))
        self.create_line(*p, fill=edge, width=max(3, int(self.s(20))),
                         capstyle="round")
        self.create_line(*p, fill=muted, width=max(1, int(self.s(13))),
                         capstyle="round")

    def _contenedor(self, i, panel, edge, muted, t):
        a = self.app
        x1, y1, x2, y2 = self._cont(i)
        sel = (i == a.sel)
        if sel:
            self._rr(x1 - 6, y1 - 6, x2 + 6, y2 + MOTOR_H + 6, r=22,
                     fill="", outline=SELECCION[0], width=3)
            self._rr(x1 - 2, y1 - 2, x2 + 2, y2 + MOTOR_H + 2, r=19,
                     fill="", outline=SELECCION[1], width=1)
        self._rr(x1, y1, x2, y2, r=15, fill=panel,
                 outline=SELECCION[0] if sel else edge, width=2 if sel else 1)

        cx = (x1 + x2) / 2
        r_bola = CONT_W * 0.14
        for dx, dy in ((-0.15, 0.28), (0.15, 0.28), (0, 0.50),
                       (-0.15, 0.72), (0.15, 0.72)):
            bx, by = cx + CONT_W * dx, y1 + CONT_H * dy
            if i in self.img:
                self.create_image(self.px(bx), self.py(by),
                                  image=self.img[i])
            else:
                self.create_oval(self.px(bx - r_bola), self.py(by - r_bola),
                                 self.px(bx + r_bola), self.py(by + r_bola),
                                 fill=COLORES[i], outline="")
        self.create_text(self.px(cx), self.py(y1 + 18),
                         text=f"{NAMES[i]}  (color {i})",
                         fill=t["texto_editor"],
                         font=self.f(FAM_UI, 10, "bold"))

        my1, my2 = y2, y2 + MOTOR_H
        girando = (a.motor_activo == i)
        if not self._tiene_motor_img():
            self._rr(x1 + 6, my1, x2 - 6, my2, r=12,
                     fill=a.hl("registros") if girando else panel,
                     outline=edge, width=1)
            self.create_text(self.px(cx), self.py((my1 + my2) / 2),
                             text=f"STEPPER {i + 1}",
                             fill=t["fondo_app"] if girando else muted,
                             font=self.f(FAM_UI, 9, "bold"))
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
        self.create_image(self.px((x1 + x2) / 2), self.py(y2 + MOTOR_H / 2),
                          image=img, tags=f"motor{i}")

    def _led(self, x, y, texto, color, encendido, panel, edge):
        d = 38
        self.create_oval(self.px(x), self.py(y), self.px(x + d),
                         self.py(y + d), fill=color if encendido else panel,
                         outline=edge, width=max(1, int(self.s(2))))
        self.create_text(self.px(x + d / 2), self.py(y + d + 12), text=texto,
                         fill=edge, font=self.f(FAM_UI, 8))

    def _bandeja(self, panel, edge, muted):
        a = self.app
        bx, by = (TRAY[0] + TRAY[2]) / 2, (TRAY[1] + TRAY[3]) / 2
        key = "bandeja_1" if a.tray is not None else "bandeja_0"
        if key in self.big:
            self.create_image(self.px(bx), self.py(by), image=self.big[key])
        else:
            self._rr(*TRAY, r=22, fill=panel, outline=edge, width=2)
        if a.tray is not None and not a.anim:
            self._bola(bx, by - 8, a.tray)
            self.create_text(self.px(bx), self.py(TRAY[3] - 16),
                             text="click para retirar", fill=muted,
                             font=self.f(FAM_UI, 9))
        elif "bandeja_0" not in self.big:
            self.create_text(self.px(bx), self.py(TRAY[3] - 16),
                             text="RETIRO", fill=muted,
                             font=self.f(FAM_UI, 9))
        self._zona(*TRAY, a.retirar)

    def _bola(self, x, y, i):
        if i in self.img:
            self.create_image(self.px(x), self.py(y), image=self.img[i],
                              tags="fall")
        else:
            r = CONT_W * 0.14
            self.create_oval(self.px(x - r), self.py(y - r), self.px(x + r),
                             self.py(y + r), fill=COLORES[i],
                             outline="#ffffff", tags="fall")

    def caer(self, i):
        self.app.anim = True
        self.app.motor_activo = i
        sx, sy = self._salida(i)
        cx, cy = CENTRO
        tx, ty = (TRAY[0] + TRAY[2]) / 2, (TRAY[1] + TRAY[3]) / 2 - 8

        def paso(n=0, pasos=55):
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
            self.after(35, lambda: paso(n + 1))
        paso()
