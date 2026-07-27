# Vending Verilog - simulador hibrido educativo

Una sola ventana: a la izquierda LA MAQUINA (grilla 3x3, credito, LED
listo/error, bandeja de retiro), a la derecha el EDITOR (codigo
Verilog + consola + boton de opciones con tema/fuente/tamano).

El estudiante escribe Verilog real. Ese codigo se compila y simula de
verdad con Icarus Verilog (iverilog + vvp) - no hay ningun interprete
inventado en Python haciendo de cuenta que es Verilog. Lo que se ve en
pantalla es el resultado real de correr ese hardware.

## La idea central: "tiempo real" sin que la simulacion corra en vivo

Icarus Verilog no es interactivo: no hay forma de "meterle un click"
a una simulacion mientras esta corriendo. Un testbench de Verilog se
escribe, se compila una vez, se corre de punta a punta, y termina.

Entonces, como se siente "en vivo" si cada click del mouse dispara una
simulacion que arranca y termina en milisegundos? La respuesta es
**batch replay**: la sesion completa (todos los eventos que el
estudiante genero desde que compilo) se guarda como una lista. Cada
vez que pasa algo nuevo (meter una ficha, elegir un producto, apretar
comprar), Python:

1. Agrega el evento nuevo al final de la lista de eventos de la sesion.
2. Vuelve a escribir **toda la historia completa** (no solo lo nuevo)
   en un archivo `events.hex`.
3. Corre `iverilog` para compilar el modulo del estudiante junto con
   el testbench fijo.
4. Corre `vvp` para simular esa historia completa desde cero (reset
   incluido) y vuelca el estado de cada senal, ciclo por ciclo, a un
   `output.csv`.
5. Python lee ese CSV, se queda con la ultima fila (el estado actual)
   y redibuja la maquina.

Como esto pasa en un par de decimas de segundo y el usuario solo ve el
resultado final, la sensacion es la de una maquina que responde al
instante - aunque por dentro sea "recompilar y re-simular todo desde
el principio" en cada click. Es la misma logica que usan varias
plataformas de simulacion hibridas: sacrificar la interactividad en
vivo del simulador a cambio de reproducibilidad total (la sesion
completa siempre se puede volver a correr igual) y aislamiento (cada
corrida es un proceso nuevo, si algo se cuelga no se lleva puesta la
sesion anterior).

Si el codigo del estudiante tiene un error o un loop infinito, esa
corrida en particular falla, el ultimo evento se descarta (no queda
guardado en la historia) y la maquina se queda como estaba antes del
click.

## Que hace cada .v

### `hdl/base.v` - lo que edita el estudiante

Es la interfaz fija del modulo (los puertos no se pueden tocar) mas
una serie de TODO. La maquina (Python) le pasa al hardware el
`producto` elegido (0-8) y si `hay_stock`; el estudiante nunca maneja
arrays de stock ni una grilla, solo la logica del dinero:

- **Case de precios**: un `case (producto)` que asigna el precio de
  cada slot (por ejemplo, producto 2 vale 5).
- **Fichas con saturacion**: sumar `ficha_1`/`ficha_5` al credito sin
  que se pase de 7. La suma se hace con un bit extra (4 bits en vez de
  3) para poder *ver* el desborde antes de guardarlo; si se pasa, el
  credito se satura en 7 en vez de dar la vuelta a 0, y se prende el
  flag `error`.
- **Comprar**: solo si `hay_stock` y `credito >= precio` se dispensa
  (`motor_on` en 1 por un ciclo), se calcula `vuelto = credito - precio`
  y el credito vuelve a 0. La resta SOLO se hace despues de validar
  que alcanza; restar sin validar en binario sin signo no da un
  numero negativo, da un numero gigante (wraparound), y ese es
  justamente el bug que el ejercicio busca evitar. Si no alcanza o no
  hay stock, se prende `error` y el credito se conserva intacto.
- **`listo`**: salida combinacional, 1 cuando el credito ya alcanza el
  precio del producto elegido.

### `hdl/solucion.v` - la respuesta (no se distribuye a estudiantes)

Mismo modulo, completo, para que el docente valide que el testbench y
la maquina funcionan antes de repartir el ejercicio.

### `hdl/testbench.v` - fijo, el estudiante nunca lo ve

Es el que hace posible el batch replay. Instancia el modulo del
estudiante, genera el reloj, y en un bloque `initial` lee
`events.hex`: un archivo de bytes donde cada byte es un evento
(nibble alto = que paso, nibble bajo = el dato: que producto, que
ficha, etc). Por cada evento aplica el pulso o el nivel
correspondiente, deja pasar un par de ciclos de asentamiento, y anota
una fila en `output.csv` con el estado de todas las senales de salida
en ese momento. Al final escribe `TB_DONE` para que Python sepa que
termino bien (y no a la mitad, colgado).

Tambien tiene un **watchdog**: un `initial` en paralelo que si pasan
2,000,000 ns sin que la simulacion haya terminado, fuerza el corte.
Esto es la defensa contra loops infinitos en el codigo del estudiante:
sin el watchdog, un `always` mal escrito haria que `vvp` nunca
termine y la app se quedaria colgada esperando para siempre.

Si se corre `vvp sim.vvp +vcd`, ademas vuelca todas las senales a
`wave.vcd` para poder abrirlas en GTKWave (ver mas abajo).

## Que hace cada .py

| Archivo | Responsabilidad |
|---|---|
| `app.py` | La sesion: guarda el estado (credito, seleccion, stock, bandeja) y traduce cada accion del usuario en eventos para `logica.Sim` |
| `logica.py` | El motor: arma `events.hex`, corre `iverilog`/`vvp` con timeouts, parsea `output.csv`, traduce errores de compilacion a espanol |
| `maquina.py` | Dibuja el canvas de la vending (grilla, LEDs, bandeja, animacion de caida) a partir del estado que le pasa `app.py` |
| `editor.py` | El panel de codigo: editor de texto, consola, boton de opciones (tema/fuente/tamano), fondo de imagen por tema |
| `imagenes.py` | Carga y escala imagenes (productos, fondo de la maquina, fondo del editor) preservando el aspect ratio |
| `estilos.py` | Constantes de layout (tamanos, posiciones) y helper de rectangulos redondeados |
| `config.py` | Rutas, precios, nombres y stock inicial de cada producto - lo que se edita para cambiar la vending |
| `ondas.py` | Abre GTKWave (si esta instalado) con las senales de la sesion ya precargadas |

### El ciclo de una accion (ejemplo: apretar "Comprar")

1. `app.comprar()` agrega al final de `sim.events` los bytes que
   describen "producto elegido" + "hay stock" + "boton comprar".
2. Llama a `_correr()`, que le pide a `logica.Sim.run()` que escriba
   `events.hex` con **toda** la lista de eventos (no solo el ultimo) y
   dispare `iverilog` + `vvp`.
3. Si compila y simula bien, `logica.py` devuelve un diccionario con
   el estado final (credito, vuelto, error, si se dispenso o no) que
   `app.py` guarda en `self.state`.
4. `app.py` decide el mensaje de consola y llama a `maq.draw()`, que
   vuelve a dibujar toda la maquina segun ese estado.
5. Si se dispenso, ademas dispara `maq.caer()`, una animacion puramente
   visual (no toca la simulacion) que anima el producto cayendo del
   slot a la bandeja.

Si en el paso 2 la simulacion falla (error de codigo o timeout), el
evento que se acababa de agregar se saca de la lista antes de volver:
la sesion queda exactamente como estaba antes del click, como si
nunca hubiera pasado.

## Instalacion (Windows)

1. Python 3.10+ (python.org, marcar "Add to PATH"). Tkinter viene
   incluido, no hay que instalar nada aparte para la GUI.
2. Icarus Verilog: https://bleyer.org/icarus/ (marcar "agregar al
   PATH"). Sin esto la app avisa y no deja compilar.
3. Opcional: `pip install pillow` (o `pip install -r requirements.txt`)
   para que las imagenes .jpg y el escalado se vean mejor.
4. `python app.py`

## Constantes de la vending (`config.py`)

```
NAMES  = nombre de cada producto (slot 0..8)
PRICES = precio de cada producto (debe coincidir con el case del .v)
STOCK0 = stock inicial de cada producto
```

## Robustez

- Timeout de compilacion (20s) y de simulacion (10s) en Python, mas el
  watchdog dentro del propio testbench: un loop infinito en el codigo
  del estudiante no cuelga la app.
- Errores de `iverilog` traducidos a espanol con numero de linea y una
  pista del problema tipico (punto y coma faltante, nombre de modulo
  cambiado, etc).
- Si falta Icarus Verilog o GTKWave, la app lo avisa con instrucciones
  en vez de fallar en silencio.

## Visor de senales (GTKWave, opcional)

Boton **Senales** en el editor: abre GTKWave con la historia completa
de la sesion y las senales ya cargadas en orden logico (clk, fichas,
producto, credito, listo, motor_on, vuelto, error). Como cada click
re-simula todo, hay que volver a apretar Senales despues de generar
mas eventos para ver las ondas actualizadas. GTKWave puede ir embebido
dentro de la carpeta del proyecto (ver `GTKWAVE_DIRS` en `config.py`).

## Para el docente / proximos pasos

La clase `Sim` de `logica.py` (agregar eventos -> `run()` -> dict con
el estado) no depende de Tkinter para nada: es el contrato que se
puede reusar tal cual como backend si esto se lleva a Unity mas
adelante, exponiendolo por ejemplo detras de un servidor local.
