import os
import tkinter as tk

from config import BG, IMG
from estilos import CONT_W, TRAY

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
    for i in range(3):
        for ext in ("png", "gif", "jpg", "jpeg"):
            p = os.path.join(IMG, f"{i}.{ext}")
            if os.path.isfile(p):
                if (r := _load(p, (CONT_W - 60, 44))):
                    productos[i] = r
                break
    tw, th = TRAY[2] - TRAY[0], TRAY[3] - TRAY[1]
    for name, box in (("fondo", (460, 680)), ("bandeja_0", (tw, th)),
                      ("bandeja_1", (tw, th))):
        p = os.path.join(IMG, f"{name}.png")
        if os.path.isfile(p) and (r := _load(p, box)):
            extras[name] = r
    return productos, extras


def _load_cover(path, size):
    try:
        if not Image:
            return None
        im = Image.open(path).convert("RGBA")
        tw, th = size
        esc = max(tw / im.width, th / im.height)
        im = im.resize((int(im.width * esc) + 1, int(im.height * esc) + 1))
        x, y = (im.width - tw) // 2, (im.height - th) // 2
        im = im.crop((x, y, x + tw, y + th))
        return ImageTk.PhotoImage(im)
    except Exception:
        return None


def cargar_fondo_tema(nombre_archivo, size=(900, 760)):
    if not nombre_archivo:
        return None
    p = os.path.join(BG, nombre_archivo)
    return _load_cover(p, size) if os.path.isfile(p) else None
