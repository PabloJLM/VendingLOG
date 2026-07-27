import json

from config import TEMAS

CW, CH = 460, 680
GX, GY, CELL_W, CELL_H, GAP = 38, 105, 118, 96, 8
TRAY = (105, 480, 355, 610)
SELECCION = ("#f9ca24", "#ffe082")

FUENTE_TITULO = ("Courier New", 16, "bold")
FUENTE_LCD    = ("Courier New", 13, "bold")
FUENTE_UI     = ("Segoe UI", 10, "bold")
FUENTE_CHICA  = ("Segoe UI", 8)
FUENTE_EDITOR = ("Courier New", 11)

FUENTES  = ["Courier New", "Consolas", "Lucida Console"]
TAMANOS  = [9, 10, 11, 12, 13, 14, 16, 18]

FALLBACK = {"In the Pool": {
    "fondo_editor": "#101A24", "texto_editor": "#D7E3F4",
    "fondo_consola": "#0C141C", "texto_consola": "#C8D6EB",
    "fondo_app": "#162433", "tab_sel": "#3A5A7A",
    "hl": {"instrucciones": "#7DCFFF", "registros": "#F2A7C4",
           "inmediatos": "#E0AF68", "etiquetas": "#9ECEFF",
           "comentarios": "#5C6A82"}}}


def load_themes():
    try:
        data = json.load(open(TEMAS, encoding="utf-8"))
        return {f"{cat} · {n}": t for cat, d in data.items()
                for n, t in d.items()}
    except Exception:
        return FALLBACK


def rrect(cv, x1, y1, x2, y2, r=16, **kw):
    p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
         x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(p, smooth=True, **kw)
