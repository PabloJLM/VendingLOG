import os
import tkinter as tk

from config import IMG
from estilos import CELL_W, CH, CW, TRAY

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None


def _load(path, box):
    try:
        if Image:
            im = Image.open(path).convert("RGBA")
            im.thumbnail(box)
            return ImageTk.PhotoImage(im)
        im = tk.PhotoImage(file=path)
        k = max(1, -(-im.width() // box[0]), -(-im.height() // box[1]))
        return im.subsample(k, k)
    except Exception:
        return None


def cargar():
    productos, extras = {}, {}
    for i in range(9):
        for ext in ("png", "gif", "jpg", "jpeg"):
            p = os.path.join(IMG, f"{i}.{ext}")
            if os.path.isfile(p):
                if (r := _load(p, (CELL_W - 22, 52))):
                    productos[i] = r
                break
    tw, th = TRAY[2] - TRAY[0], TRAY[3] - TRAY[1]
    for name, box in (("fondo", (CW, CH)), ("bandeja_0", (tw, th)),
                      ("bandeja_1", (tw, th))):
        p = os.path.join(IMG, f"{name}.png")
        if os.path.isfile(p) and (r := _load(p, box)):
            extras[name] = r
    return productos, extras
