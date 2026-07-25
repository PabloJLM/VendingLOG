# -*- coding: utf-8 -*-
"""Máquina Expendedora Verilog — dos ventanas, temas estilo JoJoP IDE.

Ventana 1 (LA MÁQUINA): fondo de imagen, grilla 3x3 con imágenes de
productos y bandeja de retiro cuya imagen cambia según la lógica del
hardware. Todo se opera con clicks sobre la propia máquina.

Ventana 2 (EDITOR): código Verilog + consola + selector de tema
(lee el mismo temas.json del IDE).

Imágenes en img/ (todas opcionales, con fallback dibujado):
  fondo.png            la máquina completa (ideal ~460x680)
  0.png ... 8.png      productos (cualquier tamaño, aspect ratio intacto)
  bandeja_0.png        bandeja vacía        (~250x120)
  bandeja_1.png        bandeja entregando   (~250x120)

Requiere: Python 3.10+ e Icarus Verilog (https://bleyer.org/icarus/).
Opcional: pip install pillow (para .jpg y mejor escalado).
Ejecutar:  python app.py
"""
import csv, json, os, re, shutil, subprocess, tempfile, tkinter as tk
from tkinter import filedialog, font, messagebox, ttk

HERE   = os.path.dirname(os.path.abspath(__file__))
PRICES = [2, 3, 5, 1, 4, 7, 6, 2, 3]
STOCK0 = [3, 2, 2, 3, 1, 2, 0, 3, 2]
NAMES  = ["Chips", "Galletas", "Soda", "Chicle", "Agua",
          "Chocolate", "Café", "Caramelo", "Jugo"]
FLAGS  = 0x08000000 if os.name == "nt" else 0
CW, CH = 460, 680                                  # canvas de la máquina
GX, GY, CELL_W, CELL_H, GAP = 38, 105, 118, 96, 8
TRAY = (105, 480, 355, 610)                        # zona bandeja x1,y1,x2,y2

NO_IV = ("No encontré Icarus Verilog.\nInstalalo desde "
         "https://bleyer.org/icarus/ (marcá 'agregar al PATH') y reabrí "
         "la aplicación.")
HINTS = [
    (r"does not have any delay|infinite loop",
     "Ese 'always' se repetiría infinito. Usá 'always @(posedge clk)' o 'always @*'."),
    (r"syntax error", "Revisá si falta un ';' o un 'begin'/'end' sin cerrar."),
    (r"Unknown module type", "No cambies el nombre del módulo 'vending_machine'."),
    (r"not a valid l-value|is not a register",
     "En un 'always' solo se asigna a señales tipo 'reg'."),
    (r"is not declared|Unable to bind",
     "Señal no declarada (ojo: Verilog distingue mayúsculas/minúsculas)."),
]
FALLBACK_THEMES = {"Reze": {
    "fondo_editor": "#0F111A", "texto_editor": "#D6DEEB",
    "fondo_consola": "#0B0D14", "texto_consola": "#C3CCE3",
    "fondo_app": "#141826", "tab_sel": "#2E3A5C",
    "hl": {"instrucciones": "#7AA2F7", "registros": "#F7768E",
           "inmediatos": "#9ECE6A", "etiquetas": "#BB9AF7",
           "comentarios": "#565F89"}}}


def load_themes():
    try:
        data = json.load(open(os.path.join(HERE, "temas.json"), encoding="utf-8"))
        return {f"{cat} · {n}": t for cat, d in data.items() for n, t in d.items()}
    except Exception:
        return FALLBACK_THEMES


def toolchain():
    iv, vp = shutil.which("iverilog"), shutil.which("vvp")
    if iv and vp:
        return iv, vp
    for c in (r"C:\iverilog\bin", r"C:\Program Files\iverilog\bin"):
        if os.path.isfile(os.path.join(c, "iverilog.exe")):
            return os.path.join(c, "iverilog.exe"), os.path.join(c, "vvp.exe")
    return None, None


def nice_error(raw):
    out, seen = [], set()
    for ln in raw.splitlines():
        m = re.match(r"^(.*?\.v):(\d+):\s*(?:syntax\s+)?(?:error:?\s*)?(.*)",
                     ln.strip())
        if not m or (m.group(2), m.group(3)) in seen:
            continue
        seen.add((m.group(2), m.group(3)))
        hint = next(("\n   → " + h for p, h in HINTS if re.search(p, ln, re.I)), "")
        out.append(f" Línea {m.group(2)}: {m.group(3) or 'error de sintaxis'}{hint}")
    return ("Errores de compilación:\n" + "\n".join(out[:10])) if out \
        else "Error de compilación:\n" + raw[:800]


def rrect(cv, x1, y1, x2, y2, r=16, **kw):
    """Rectángulo redondeado (formas orgánicas)."""
    p = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
         x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return cv.create_polygon(p, smooth=True, **kw)


class Sim:
    """Batch replay: bytes de eventos → events.hex → iverilog/vvp → CSV."""

    def __init__(self, src):
        self.src, self.events = src, []      # events: dicts {"b":byte, ...}
        self.wd = tempfile.mkdtemp(prefix="vending_")
        self.tb = os.path.join(HERE, "hdl", "testbench.v")

    def run(self):
        iv, vp = toolchain()
        if not iv:
            return {"status": "err", "msg": NO_IV}
        with open(os.path.join(self.wd, "events.hex"), "w") as f:
            f.write("".join(f"{e['b']:02x}\n" for e in self.events) + "ff\n")
        out = os.path.join(self.wd, "sim.vvp")
        try:
            c = subprocess.run([iv, "-g2001", "-o", out, self.src, self.tb],
                               capture_output=True, text=True, timeout=20,
                               creationflags=FLAGS)
        except subprocess.TimeoutExpired:
            return {"status": "err", "msg": "La compilación tardó demasiado."}
        if c.returncode:
            return {"status": "err",
                    "msg": nice_error((c.stderr or "") + (c.stdout or ""))}
        try:
            s = subprocess.run([vp, out], cwd=self.wd, capture_output=True,
                               text=True, timeout=10, creationflags=FLAGS)
        except subprocess.TimeoutExpired:
            return {"status": "err", "msg": "La simulación no terminó: "
                    "probable loop infinito. Revisá tus 'always'."}
        if s.returncode or "TB_DONE" not in (s.stdout or ""):
            return {"status": "err", "msg": "La simulación se detuvo de forma "
                    "inesperada:\n" + (s.stderr or s.stdout or "")[:400]}
        return self._parse()

    def _parse(self):
        num = lambda v: 0 if set(v.lower()) & set("xz") else int(v)
        rows = []
        try:
            with open(os.path.join(self.wd, "output.csv"), newline="") as f:
                for r in csv.DictReader(f):
                    try:
                        rows.append({k: num(v) for k, v in r.items()})
                    except (ValueError, AttributeError):
                        pass
        except OSError:
            pass
        if not rows:
            return {"status": "err", "msg": "La simulación no dio resultados."}
        disp = [any(r["motor_on"] for r in rows if r["event"] == i)
                for i in range(len(self.events))]
        last = rows[-1]
        return {"status": "ok", "dispensed": disp, "credito": last["credito"],
                "listo": last["listo"], "vuelto": last["vuelto"]}


class App:
    def __init__(self, root):
        self.root = root
        self.themes = load_themes()
        self.tname = next((k for k in self.themes if k.endswith("· Reze")),
                          list(self.themes)[0])
        self.sim, self.on, self.state = None, False, None
        self.sel, self.tray, self.anim = None, None, False
        self.stock = STOCK0[:]
        self.hot = []                     # zonas clickeables del canvas
        self.work = os.path.join(HERE, "student_work.v")

        root.title("Vending Verilog — LA MÁQUINA")
        self.cv = tk.Canvas(root, width=CW, height=CH, highlightthickness=0)
        self.cv.pack()
        self.cv.bind("<Button-1>", self._click)
        self._editor_win()
        self._imgs()
        code = self.work if os.path.isfile(self.work) \
            else os.path.join(HERE, "hdl", "skeleton.v")
        if os.path.isfile(code):
            self._set(open(code, encoding="utf-8").read())
        self._apply_theme()
        if not toolchain()[0]:
            root.after(300, lambda: messagebox.showwarning("Falta Icarus", NO_IV))

    # ---- tema -------------------------------------------------------
    @property
    def T(self):
        return self.themes[self.tname]

    def hl(self, k):
        return self.T["hl"].get(k, "#888888")

    def _apply_theme(self, *_):
        t = self.T
        self.cv.configure(bg=t["fondo_app"])
        self.ew.configure(bg=t["fondo_app"])
        self.bar.configure(bg=t["fondo_app"])
        self.lbl.configure(bg=t["fondo_app"], fg=t["texto_editor"])
        self.ed.configure(bg=t["fondo_editor"], fg=t["texto_editor"],
                          insertbackground=t["texto_editor"])
        self.log.configure(bg=t["fondo_consola"], fg=t["texto_consola"])
        for tag, key in (("err", "registros"), ("ok", "inmediatos"),
                         ("info", "instrucciones")):
            self.log.tag_configure(tag, foreground=self.hl(key))
        for b in self.btns:
            b.configure(bg=t["tab_sel"], fg=t["texto_editor"],
                        activebackground=self.hl("instrucciones"))
        self._draw()

    # ---- imágenes ---------------------------------------------------
    def _imgs(self):
        self.img, self.big = {}, {}
        try:
            from PIL import Image, ImageTk
        except ImportError:
            Image = ImageTk = None

        def load(path, box):
            try:
                if Image:
                    im = Image.open(path).convert("RGBA")
                    im.thumbnail(box)               # mantiene aspect ratio
                    return ImageTk.PhotoImage(im)
                im = tk.PhotoImage(file=path)       # sin Pillow: png/gif
                k = max(1, -(-im.width() // box[0]), -(-im.height() // box[1]))
                return im.subsample(k, k)
            except Exception:
                return None

        for i in range(9):
            for ext in ("png", "gif", "jpg", "jpeg"):
                p = os.path.join(HERE, "img", f"{i}.{ext}")
                if os.path.isfile(p):
                    if (r := load(p, (CELL_W - 22, 52))):
                        self.img[i] = r
                    break
        tw, th = TRAY[2] - TRAY[0], TRAY[3] - TRAY[1]
        for name, box in (("fondo", (CW, CH)), ("bandeja_0", (tw, th)),
                          ("bandeja_1", (tw, th))):
            p = os.path.join(HERE, "img", f"{name}.png")
            if os.path.isfile(p) and (r := load(p, box)):
                self.big[name] = r

    # ---- ventana del editor -----------------------------------------
    def _editor_win(self):
        self.ew = tk.Toplevel(self.root)
        self.ew.title("Vending Verilog — EDITOR")
        self.ew.geometry(f"760x680+{CW + 60}+40")
        self.ew.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.bar = tk.Frame(self.ew)
        self.bar.pack(fill="x", padx=8, pady=6)
        self.lbl = tk.Label(self.bar, text="Tu módulo Verilog",
                            font=("Segoe UI", 11, "bold"))
        self.lbl.pack(side="left")
        self.btns = [self._btn("Compilar y correr", self._compile),
                     self._btn("Abrir .v", self._open),
                     self._btn("Guardar .v", self._saveas),
                     self._btn("Esqueleto", self._skel)]
        self.combo = ttk.Combobox(self.bar, values=list(self.themes),
                                  state="readonly", width=22)
        self.combo.set(self.tname)
        self.combo.pack(side="right", padx=4)
        self.combo.bind("<<ComboboxSelected>>",
                        lambda e: (setattr(self, "tname", self.combo.get()),
                                   self._apply_theme()))
        mono = font.nametofont("TkFixedFont").copy()
        mono.configure(family="Courier New", size=11)
        fr = tk.Frame(self.ew)
        fr.pack(fill="both", expand=True, padx=8)
        self.ed = tk.Text(fr, wrap="none", font=mono, undo=True,
                          relief="flat", borderwidth=8)
        sb = ttk.Scrollbar(fr, command=self.ed.yview)
        self.ed.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.ed.pack(side="left", fill="both", expand=True)
        self.log = tk.Text(self.ew, height=9, wrap="word", state="disabled",
                           font=("Segoe UI", 10), relief="flat", borderwidth=8)
        self.log.pack(fill="x", padx=8, pady=(6, 8))

    def _btn(self, txt, cmd):
        b = tk.Button(self.bar, text=txt, command=cmd, relief="flat",
                      font=("Segoe UI", 9, "bold"), padx=8, pady=4,
                      cursor="hand2")
        b.pack(side="right", padx=3)
        return b

    def _msg(self, txt, tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end", txt + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ---- dibujo de la máquina ---------------------------------------
    def _cell(self, i):
        r, c = divmod(i, 3)
        return GX + c * (CELL_W + GAP), GY + r * (CELL_H + GAP)

    def _hot(self, x1, y1, x2, y2, cmd):
        self.hot.append((x1, y1, x2, y2, cmd))

    def _pill(self, x1, y1, x2, y2, txt, color, cmd, fg="#ffffff"):
        rrect(self.cv, x1, y1, x2, y2, r=(y2 - y1) // 2, fill=color)
        self.cv.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=txt, fill=fg,
                            font=("Segoe UI", 10, "bold"))
        self._hot(x1, y1, x2, y2, cmd)

    def _draw(self):
        cv, t, st = self.cv, self.T, self.state
        panel, edge = t["fondo_consola"], t["tab_sel"]
        acc, muted = self.hl("instrucciones"), self.hl("comentarios")
        cv.delete("all")
        self.hot = []

        if "fondo" in self.big:
            cv.create_image(CW / 2, CH / 2, image=self.big["fondo"])
        else:
            rrect(cv, 10, 10, CW - 10, CH - 10, r=26, fill=t["fondo_editor"],
                  outline=edge, width=2)
        cv.create_text(CW / 2, 30, text="VENDING VERILOG",
                       fill=acc, font=("Courier New", 16, "bold"))

        # display: crédito, vuelto, led
        credito = st["credito"] if st else 0
        vuelto = st["vuelto"] if st else 0
        rrect(cv, GX, 48, GX + 260, 88, r=14, fill=panel, outline=edge)
        cv.create_text(GX + 14, 68, anchor="w", text=f"CRÉDITO {credito}",
                       fill=self.hl("inmediatos"),
                       font=("Courier New", 13, "bold"))
        cv.create_text(GX + 145, 68, anchor="w", text=f"VUELTO {vuelto}",
                       fill=self.hl("registros"),
                       font=("Courier New", 12, "bold"))
        led = bool(st and st["listo"] and self.sel is not None)
        cv.create_oval(GX + 290, 52, GX + 322, 84,
                       fill=self.hl("inmediatos") if led else panel,
                       outline=edge, width=2)
        cv.create_text(GX + 306, 94, text="LISTO", fill=muted,
                       font=("Segoe UI", 7))

        # grilla 3x3
        for i in range(9):
            x, y = self._cell(i)
            ok = self.stock[i] > 0
            selc = acc if i == self.sel else edge
            rrect(cv, x, y, x + CELL_W, y + CELL_H, r=14, fill=panel,
                  outline=selc, width=3 if i == self.sel else 1)
            if i in self.img:
                cv.create_image(x + CELL_W / 2, y + 32, image=self.img[i])
            else:
                rrect(cv, x + 34, y + 10, x + CELL_W - 34, y + 50, r=10,
                      fill=self.hl("etiquetas") if ok else muted)
            if not ok:
                rrect(cv, x + 2, y + 2, x + CELL_W - 2, y + 58, r=12,
                      fill=t["fondo_app"], stipple="gray50", outline="")
            cv.create_text(x + CELL_W / 2, y + 64, text=NAMES[i],
                           fill=t["texto_editor"] if ok else muted,
                           font=("Segoe UI", 9))
            cv.create_text(x + CELL_W / 2, y + 82,
                           text=f"$ {PRICES[i]}  ·  {self.stock[i]}" if ok
                           else "AGOTADO",
                           fill=self.hl("registros") if ok else muted,
                           font=("Segoe UI", 9, "bold"))
            self._hot(x, y, x + CELL_W, y + CELL_H,
                      lambda i=i: self._select(i))

        # botones orgánicos
        self._pill(GX, 428, GX + 92, 462, "FICHA 1", self.hl("etiquetas"),
                   lambda: self._act(0x10))
        self._pill(GX + 100, 428, GX + 192, 462, "FICHA 5",
                   self.hl("registros"), lambda: self._act(0x20))
        self._pill(GX + 202, 428, CW - GX, 462, "COMPRAR",
                   self.hl("inmediatos"), self._buy, fg=t["fondo_app"])

        # bandeja de retiro (imagen según la lógica)
        bx = (TRAY[0] + TRAY[2]) / 2
        by = (TRAY[1] + TRAY[3]) / 2
        key = "bandeja_1" if self.tray is not None else "bandeja_0"
        if key in self.big:
            cv.create_image(bx, by, image=self.big[key])
        else:
            rrect(cv, *TRAY, r=20, fill=panel, outline=edge, width=2)
        if self.tray is not None and not self.anim:
            self._item(bx, by - 8, self.tray)
            cv.create_text(bx, TRAY[3] - 14, text="click para retirar",
                           fill=muted, font=("Segoe UI", 8))
        elif "bandeja_0" not in self.big:
            cv.create_text(bx, TRAY[3] - 14, text="RETIRO", fill=muted,
                           font=("Segoe UI", 8))
        self._hot(*TRAY, self._take)

        cv.create_text(CW - GX, CH - 22, anchor="e", text="reiniciar sesión",
                       fill=muted, font=("Segoe UI", 9, "underline"))
        self._hot(CW - GX - 110, CH - 34, CW - GX, CH - 10, self._reset)

        if not self.on:
            rrect(cv, 10, 10, CW - 10, CH - 10, r=26, fill=t["fondo_app"],
                  stipple="gray50", outline="")
            cv.create_text(CW / 2, CH / 2 - 10, text="MÁQUINA APAGADA",
                           fill=t["texto_editor"],
                           font=("Courier New", 14, "bold"))
            cv.create_text(CW / 2, CH / 2 + 16, fill=muted,
                           font=("Segoe UI", 10),
                           text="Compilá tu módulo en la otra ventana")

    def _item(self, x, y, i):
        if i in self.img:
            self.cv.create_image(x, y, image=self.img[i], tags="fall")
        else:
            rrect(self.cv, x - 24, y - 14, x + 24, y + 14, r=10,
                  fill=self.hl("etiquetas"), outline="#ffffff", tags="fall")

    def _fall(self, slot):
        self.anim = True
        x0, y0 = (v + d for v, d in zip(self._cell(slot), (CELL_W / 2, 32)))
        x1 = (TRAY[0] + TRAY[2]) / 2
        y1 = (TRAY[1] + TRAY[3]) / 2 - 8

        def move(n=0, steps=20):
            self.cv.delete("fall")
            if n > steps:
                self.anim = False
                self._draw()
                return
            tt = n / steps
            self._item(x0 + (x1 - x0) * tt, y0 + (y1 - y0) * tt * tt, slot)
            self.root.after(22, lambda: move(n + 1))
        move()

    # ---- eventos / lógica -------------------------------------------
    def _sel_byte(self, i):
        return 0x30 | ((self.stock[i] > 0) << 3) | PRICES[i]

    def _click(self, e):
        if not self.on or self.anim:
            return
        for x1, y1, x2, y2, cmd in self.hot:
            if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                cmd()
                return

    def _select(self, i):
        self.sel = i
        self.sim.events.append({"b": self._sel_byte(i)})
        if self._run():
            listo = "sí" if self.state["listo"] else "todavía no"
            self._msg(f"Elegiste {NAMES[i]} ($ {PRICES[i]}). "
                      f"¿Alcanza el crédito?: {listo}.", "info")
        else:
            self.sim.events.pop()
        self._draw()

    def _act(self, byte):
        if not self.on or self.anim:
            return
        self.sim.events.append({"b": byte})
        if not self._run():
            self.sim.events.pop()
            return
        extra = "  (tope 7 alcanzado)" if self.state["credito"] == 7 else ""
        self._msg(f"Crédito: {self.state['credito']}{extra}", "info")
        self._draw()

    def _buy(self):
        if not self.on or self.anim:
            return
        if self.sel is None:
            self._msg("Primero hacé click en un producto.", "err")
            return
        i = self.sel
        # refrescar precio/hay_stock del slot y luego el pulso de compra
        self.sim.events.append({"b": self._sel_byte(i)})
        self.sim.events.append({"b": 0x40, "slot": i})
        if not self._run():
            self.sim.events = self.sim.events[:-2]
            return
        if self.state["dispensed"][-1]:
            self._recount()
            self.tray = i
            self._msg(f"✔ Dispensado: {NAMES[i]}. "
                      f"Vuelto: {self.state['vuelto']}.", "ok")
            self._draw()
            self._fall(i)
            return
        self._msg("✘ No se dispensó: " +
                  ("slot AGOTADO." if self.stock[i] == 0 else
                   f"crédito insuficiente ({self.state['credito']} < "
                   f"{PRICES[i]}).") + " Tu crédito se conserva.", "err")
        self._draw()

    def _take(self):
        if self.tray is not None:
            self._msg(f"Retiraste {NAMES[self.tray]}. ¡Provecho!", "ok")
            self.tray = None
            self._draw()

    def _recount(self):
        """Stock = inicial menos compras que sí dispensaron."""
        self.stock = STOCK0[:]
        for e, d in zip(self.sim.events, self.state["dispensed"]):
            if d and "slot" in e:
                self.stock[e["slot"]] -= 1

    def _run(self):
        self.root.configure(cursor="watch")
        self.ew.configure(cursor="watch")
        self.root.update_idletasks()
        try:
            res = self.sim.run()
        finally:
            self.root.configure(cursor="")
            self.ew.configure(cursor="")
        if res["status"] != "ok":
            self._msg(res["msg"], "err")
            return None
        self.state = res
        return res

    def _reset(self):
        if not self.on:
            return
        self.sim.events, self.sel, self.tray = [], None, None
        self.stock = STOCK0[:]
        self._run()
        self._msg("Sesión reiniciada: máquina como nueva.", "info")
        self._draw()

    # ---- editor -----------------------------------------------------
    def _set(self, txt):
        self.ed.delete("1.0", "end")
        self.ed.insert("1.0", txt)

    def _skel(self):
        self._set(open(os.path.join(HERE, "hdl", "skeleton.v"),
                       encoding="utf-8").read())
        self._msg("Esqueleto cargado: completá los TODO y compilá.", "info")

    def _open(self):
        if (p := filedialog.askopenfilename(filetypes=[("Verilog", "*.v")])):
            self._set(open(p, encoding="utf-8", errors="replace").read())

    def _saveas(self):
        if (p := filedialog.asksaveasfilename(defaultextension=".v",
                                              filetypes=[("Verilog", "*.v")])):
            open(p, "w", encoding="utf-8").write(self.ed.get("1.0", "end-1c"))
            self._msg(f"Guardado: {os.path.basename(p)}", "ok")

    def _compile(self):
        open(self.work, "w", encoding="utf-8").write(self.ed.get("1.0", "end-1c"))
        self.sim = Sim(self.work)
        self.sel, self.tray, self.stock = None, None, STOCK0[:]
        self._msg("Compilando y simulando...", "info")
        if self._run():
            self.on = True
            self._msg("✔ Compilación exitosa: máquina encendida. "
                      "Meté fichas y elegí un producto.", "ok")
        else:
            self.on = False
        self._draw()


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    App(root)
    root.mainloop()
