import json
import platform

from config import TEMAS

# Fuentes por sistema operativo -----------------------------------------
# En Windows "Segoe UI"/"Courier New" siempre existen; en Linux/Mac no,
# y Tk las reemplaza en silencio por una fuente generica fea. Elegimos
# una familia que si exista en cada SO para que se vea igual en los dos.
_SO = platform.system()  # "Windows", "Linux", "Darwin"
if _SO == "Windows":
    FAM_UI, FAM_MONO = "Segoe UI", "Courier New"
    FUENTES = ["Courier New", "Consolas", "Lucida Console"]
elif _SO == "Darwin":
    FAM_UI, FAM_MONO = "Helvetica Neue", "Menlo"
    FUENTES = ["Menlo", "Monaco", "Courier New"]
else:  # Linux y otros
    FAM_UI, FAM_MONO = "DejaVu Sans", "DejaVu Sans Mono"
    FUENTES = ["DejaVu Sans Mono", "Liberation Mono", "Courier New"]

# Animacion agrandada (~30% del tamano original) y editor mas angosto: el
# codigo ya no se modifica, así que la maquina merece la mayor parte de
# la pantalla.
CW, CH = 594, 876

# 3 contenedores (uno por color), cada uno con su stepper debajo
CONT_W, CONT_H, CONT_GAP = 160, 198, 18
CONT_Y = 80                        # borde superior de los contenedores
MOTOR_H = 94                       # caja del stepper bajo cada contenedor
CENTRO = (297, 510)                # punto donde convergen las 3 rampas
TOLVA_W, TOLVA_H = 123, 80         # embudo central (img/tolva.png)
TUBO_W = 44                        # tubo tolva -> bandeja (img/tubo.png)
TRAY = (155, 606, 438, 747)        # bandeja central x1, y1, x2, y2
BOTON_Y = 778                      # boton de moneda (debajo de la bandeja)
SELECCION = ("#f9ca24", "#ffe082")

FUENTE_TITULO = (FAM_MONO, 16, "bold")
FUENTE_LCD    = (FAM_MONO, 13, "bold")
FUENTE_UI     = (FAM_UI, 10, "bold")
FUENTE_CHICA  = (FAM_UI, 8)
FUENTE_EDITOR = (FAM_MONO, 11)

TAMANOS = [9, 10, 11, 12, 13, 14, 16, 18]

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
