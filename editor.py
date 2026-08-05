import os
import tkinter as tk
from tkinter import filedialog, ttk

from estilos import FUENTE_EDITOR, FUENTES, TAMANOS
import imagenes


class Editor:
    def __init__(self, root, app):
        self.app = app
        self.opciones = None
        self.fuente = list(FUENTE_EDITOR[:2])
        self.fondo_img = None
        self._bg_nombre = None

        self.fondo = tk.Canvas(root, highlightthickness=0)
        self.fondo.pack(side="left", fill="both", expand=True,
                        padx=8, pady=6)
        self.fondo.bind("<Configure>", self._reubicar)

        self.frame = tk.Frame(self.fondo)
        self._ventana = self.fondo.create_window(0, 0, window=self.frame,
                                                 anchor="nw")
        self.bar = tk.Frame(self.frame)
        self.bar.pack(fill="x")
        self.lbl = tk.Label(self.bar, text="IDE editable, FIT XVII",
                            font=("Segoe UI", 11, "bold"))
        self.lbl.pack(side="left")
        self.btn_opciones = self._btn("⚙", self._toggle_opciones)
        self.btns = [self.btn_opciones] + [self._btn(t, c) for t, c in [
            ("Compilar y correr", app.compilar),
            ("Senales", app.ondas),
            ("Abrir .v", self.abrir),
            ("Guardar .v", self.guardar),
            ("RTL original", app.esqueleto)]]

        cuerpo = tk.Frame(self.frame)
        cuerpo.pack(fill="both", expand=True, pady=(6, 0))
        self.ed = tk.Text(cuerpo, wrap="none", font=tuple(self.fuente),
                          undo=True, relief="flat", borderwidth=8)
        sb = ttk.Scrollbar(cuerpo, command=self.ed.yview)
        self.ed.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.ed.pack(side="left", fill="both", expand=True)
        self.log = tk.Text(self.frame, height=9, wrap="word",
                           state="disabled", font=("Segoe UI", 10),
                           relief="flat", borderwidth=8)
        self.log.pack(fill="x", pady=(6, 0))

    def _btn(self, txt, cmd):
        b = tk.Button(self.bar, text=txt, command=cmd, relief="flat",
                      font=("Segoe UI", 9, "bold"), padx=8, pady=4,
                      cursor="hand2")
        b.pack(side="right", padx=3)
        return b

    def codigo(self):
        return self.ed.get("1.0", "end-1c")

    def poner(self, txt):
        self.ed.delete("1.0", "end")
        self.ed.insert("1.0", txt)

    def msg(self, txt, tag="info"):
        self.log.configure(state="normal")
        self.log.insert("end", txt + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def abrir(self):
        if (p := filedialog.askopenfilename(filetypes=[("Verilog", "*.v")])):
            self.poner(open(p, encoding="utf-8", errors="replace").read())

    def guardar(self):
        if (p := filedialog.asksaveasfilename(defaultextension=".v",
                                              filetypes=[("Verilog", "*.v")])):
            open(p, "w", encoding="utf-8").write(self.codigo())
            self.msg(f"Guardado: {os.path.basename(p)}", "ok")

    def _reubicar(self, event):
        pad = 20
        self.fondo.coords(self._ventana, pad, pad)
        self.fondo.itemconfig(self._ventana,
                              width=max(event.width - 2 * pad, 10),
                              height=max(event.height - 2 * pad, 10))
        if self.fondo_img:
            self.fondo.coords("bgimg", event.width / 2, event.height / 2)

    def set_fondo_tema(self, tema):
        self.fondo.delete("bgimg")
        self._bg_nombre = tema.get("bg")
        self.fondo_img = (imagenes.cargar_fondo_tema(self._bg_nombre)
                          if self._bg_nombre else None)
        if self.fondo_img:
            w = self.fondo.winfo_width() or 760
            h = self.fondo.winfo_height() or 680
            self.fondo.create_image(w / 2, h / 2, image=self.fondo_img,
                                    tags="bgimg")
            self.fondo.tag_lower("bgimg")

    def _set_fuente(self, familia=None, tamano=None):
        if familia:
            self.fuente[0] = familia
        if tamano:
            self.fuente[1] = tamano
        self.ed.configure(font=tuple(self.fuente))

    def _toggle_opciones(self):
        if self.opciones and self.opciones.winfo_exists():
            self.opciones.destroy()
            self.opciones = None
            return
        t = self.app.T
        win = tk.Toplevel(self.frame)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=t["fondo_app"], highlightthickness=1,
                     highlightbackground=t["tab_sel"])

        def campo(texto, valores, actual, on_pick):
            tk.Label(win, text=texto, bg=t["fondo_app"], fg=t["texto_editor"],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w",
                                                        padx=10, pady=(8, 2))
            combo = ttk.Combobox(win, values=valores, state="readonly",
                                 width=24)
            combo.set(actual)
            combo.pack(padx=10)
            combo.bind("<<ComboboxSelected>>",
                      lambda e: on_pick(combo.get()))

        campo("Tema", list(self.app.themes), self.app.tname,
              self.app.cambiar_tema)
        campo("Fuente", FUENTES, self.fuente[0],
              lambda v: self._set_fuente(familia=v))
        campo("Tamano", TAMANOS, self.fuente[1],
              lambda v: self._set_fuente(tamano=int(v)))

        tk.Button(win, text="Cerrar", command=self._toggle_opciones,
                  relief="flat", font=("Segoe UI", 9, "bold"),
                  bg=t["tab_sel"], fg=t["texto_editor"]
                  ).pack(pady=10, padx=10, fill="x")

        win.update_idletasks()
        ancho = win.winfo_reqwidth()
        x = self.btn_opciones.winfo_rootx() + self.btn_opciones.winfo_width() - ancho
        y = self.btn_opciones.winfo_rooty() + self.btn_opciones.winfo_height()
        win.geometry(f"+{max(x, 0)}+{y}")
        self.opciones = win

    def aplicar_tema(self, t, hl):
        self.fondo.configure(bg=t["fondo_app"])
        for w in (self.frame, self.bar):
            w.configure(bg=t["fondo_app"])
        self.lbl.configure(bg=t["fondo_app"], fg=t["texto_editor"])
        self.ed.configure(bg=t["fondo_editor"], fg=t["texto_editor"],
                          insertbackground=t["texto_editor"])
        self.log.configure(bg=t["fondo_consola"], fg=t["texto_consola"])
        for tag, key in (("err", "registros"), ("ok", "inmediatos"),
                         ("info", "instrucciones")):
            self.log.tag_configure(tag, foreground=hl(key))
        for b in self.btns:
            b.configure(bg=t["tab_sel"], fg=t["texto_editor"],
                        activebackground=hl("instrucciones"))
