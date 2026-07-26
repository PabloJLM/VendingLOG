import csv
import os
import re
import shutil
import subprocess
import tempfile

from config import HDL, IVERILOG_DIRS

FLAGS = 0x08000000 if os.name == "nt" else 0

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


def toolchain():
    iv, vp = shutil.which("iverilog"), shutil.which("vvp")
    if iv and vp:
        return iv, vp
    for c in IVERILOG_DIRS:
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


class Sim:
    def __init__(self, codigo):
        self.events = []
        self.wd = tempfile.mkdtemp(prefix="vending_")
        self.src = os.path.join(self.wd, "estudiante.v")
        self.tb = os.path.join(HDL, "testbench.v")
        self.vcd = os.path.join(self.wd, "wave.vcd")
        open(self.src, "w", encoding="utf-8").write(codigo)

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
            s = subprocess.run([vp, out, "+vcd"], cwd=self.wd,
                               capture_output=True, text=True, timeout=10,
                               creationflags=FLAGS)
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
        return {"status": "ok", "dispensed": disp,
                "credito": last["credito"], "listo": last["listo"],
                "vuelto": last["vuelto"], "error": last["error"]}
