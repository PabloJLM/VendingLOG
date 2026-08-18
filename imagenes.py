import os
import tkinter as tk

from config import BG, IMG
from estilos import CH, CONT_W, CW, MOTOR_H, TOLVA_H, TOLVA_W, TRAY

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

EXTS = ("png", "gif", "jpg", "jpeg")


def _ruta(nombre):
    for ext in EXTS:
        p = os.path.join(IMG, f"{nombre}.{ext}")
        if os.path.isfile(p):
            return p
    return None


# Escala manteniendo el aspect ratio (entra dentro de la caja)
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


# Estira a un tamano exacto (para rampas y tubos que deben calzar)
def _load_exacto(path, size):
    try:
        if Image:
            im = Image.open(path).convert("RGBA")
            return ImageTk.PhotoImage(im.resize(size))
        return _load(path, size)
    except Exception:
        return None


def _load_cover(path, size):
    try:
        if not Image:
            return None
        im = Image.open(path).convert("RGBA")
        tw, th = size
        esc = max(tw / im.width, th / im.height)
        im = im.resize((int(im.width * esc) + 1, int(im.height * esc) + 1))
        x, y = (im.width - tw) // 2, (im.height - th) // 2
        return ImageTk.PhotoImage(im.crop((x, y, x + tw, y + th)))
    except Exception:
        return None


def cargar(k=1.0):
    esc = lambda w, h: (max(int(w * k), 8), max(int(h * k), 8))
    productos, extras = {}, {}
    for i in range(3):
        if (p := _ruta(str(i))) and (r := _load(p, esc(CONT_W - 60, 44))):
            productos[i] = r
    tw, th = TRAY[2] - TRAY[0], TRAY[3] - TRAY[1]
    mbox = esc(CONT_W - 8, MOTOR_H)
    for nombre, box in (("fondo", esc(CW, CH)), ("bandeja_0", esc(tw, th)),
                        ("bandeja_1", esc(tw, th)), ("stepper_1", mbox),
                        ("stepper_2", mbox),
                        ("tolva", esc(TOLVA_W, TOLVA_H))):
        if (p := _ruta(nombre)) and (r := _load(p, box)):
            extras[nombre] = r
    return productos, extras


# Rampas y tubo: se estiran al tamano que pide la geometria
def cargar_pieza(nombre, size):
    p = _ruta(nombre)
    return _load_exacto(p, size) if p else None


def cargar_fondo_tema(nombre_archivo, size=(900, 760)):
    if not nombre_archivo:
        return None
    p = os.path.join(BG, nombre_archivo)
    return _load_cover(p, size) if os.path.isfile(p) else None
