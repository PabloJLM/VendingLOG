import os
import tkinter as tk
from tkinter import filedialog, ttk

from estilos import FUENTE_EDITOR


class Editor:
    def __init__(self, root, app):
        self.app = app
        self.frame = tk.Frame(root)
        self.frame.pack(side="left", fill="both", expand=True,
                        padx=8, pady=6)
        self.bar = tk.Frame(self.frame)
        self.bar.pack(fill="x")
        self.lbl = tk.Label(self.bar, text="Tu módulo Verilog",
                            font=("Segoe UI", 11, "bold"))
        self.lbl.pack(side="left")
        self.btns = [self._btn(t, c) for t, c in [
            ("Compilar y correr", app.compilar),
            ("Señales", app.ondas),
            ("Abrir .v", self.abrir),
            ("Guardar .v", self.guardar),
            ("Esqueleto", app.esqueleto)]]
        self.combo = ttk.Combobox(self.bar, values=list(app.themes),
                                  state="readonly", width=22)
        self.combo.set(app.tname)
        self.combo.pack(side="right", padx=4)
        self.combo.bind("<<ComboboxSelected>>",
                        lambda e: app.cambiar_tema(self.combo.get()))

        cuerpo = tk.Frame(self.frame)
        cuerpo.pack(fill="both", expand=True, pady=(6, 0))
        self.ed = tk.Text(cuerpo, wrap="none", font=FUENTE_EDITOR, undo=True,
                          relief="flat", borderwidth=8)
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

    def aplicar_tema(self, t, hl):
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
