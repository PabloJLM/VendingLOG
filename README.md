# Chiclera Verilog - simulador hibrido educativo

Simulador de la chiclera fisica de 3 colores. El estudiante edita la
FSM de control (`control.v`); el resto del RTL (steppers y top) es el
mismo que corre en el hardware real. Todo se compila y simula de
verdad con Icarus Verilog: lo que se ve en pantalla es el resultado
del hardware, no una imitacion en Python.

Una sola ventana: a la izquierda LA CHICLERA (3 contenedores, uno por
color, cada uno con su stepper; las 3 rampas convergen en el embudo
central que descarga en la bandeja de retiro), a la derecha el EDITOR
(codigo + consola + opciones de tema/fuente).

Se elige el color haciendo click en su contenedor; al meter la moneda
gira el stepper de ese contenedor (se resalta) y el chicle baja por la
rampa hasta el centro.

Ver `REPORTE_RTL.md` para la explicacion detallada de los tres
modulos Verilog.

## La idea central: "tiempo real" con batch replay

Icarus Verilog no es interactivo: una simulacion se compila, corre de
punta a punta y termina. La sensacion de tiempo real se logra asi:
cada click (elegir color, meter moneda) se agrega a la lista de
eventos de la sesion, y se re-simula TODA la historia desde cero en
milisegundos. El usuario solo ve el estado final, asi que la maquina
parece responder al instante. A cambio se gana reproducibilidad (la
sesion siempre se puede repetir identica) y aislamiento (cada corrida
es un proceso nuevo; si el codigo del estudiante se cuelga, el evento
se descarta y la sesion queda como estaba).

## El ciclo de una moneda

1. El usuario elige un color (0, 1 o 2) y aprieta METER MONEDA.
2. Python escribe `events.hex` con toda la historia y corre
   `iverilog` (control.v del editor + stepper.v + top.v + testbench)
   y despues `vvp`.
3. El testbench pulsa `sensor_entrada`. Si la FSM del estudiante
   funciona, prende `inicioN` y el stepper de ese color gira
   (`ocupadoN` en alto durante 4800 ciclos).
4. El testbench EMULA LA PLANTA: cuando el motor termina, espera unos
   ciclos (la bola cayendo) y pulsa `sensor_salida`, como el sensor
   optico real. La FSM debe responder prendiendo `led`.
5. Python lee `output.csv` (filas solo cuando algo cambia), detecta
   que motor giro y si el led de exito prendio, y anima el chicle
   bajando por la rampa de ese contenedor hasta la bandeja central.

Si ningun motor arranca o el led nunca prende, la consola dice que
parte de la FSM revisar.

## Que hace cada archivo

| Archivo | Responsabilidad |
|---|---|
| `hdl/control.v` | La FSM - LO QUE EDITA EL ESTUDIANTE (se carga al abrir) |
| `hdl/stepper.v` | Generador de pasos del motor (fijo, igual al hardware) |
| `hdl/top.v` | Integra control + 3 steppers (fijo, igual al hardware) |
| `hdl/testbench.v` | Fijo: reloj, eventos, emulacion de la planta, log, watchdog |
| `app.py` | La sesion: estado y acciones (se ejecuta este) |
| `logica.py` | Motor batch replay: iverilog/vvp, timeouts, parseo, errores |
| `maquina.py` | Dibuja la chiclera (globo, selectores, bandeja, animacion) |
| `editor.py` | Editor de codigo + consola + opciones (tema/fuente/tamano) |
| `imagenes.py` | Carga de imagenes con aspect ratio |
| `estilos.py` | Layout, fuentes, temas, formas |
| `config.py` | Rutas y nombres de los 3 colores |
| `ondas.py` | GTKWave con las senales precargadas |

## Imagenes (carpeta img/)

- `0.png`, `1.png`, `2.png`: el chicle de cada color (cualquier
  tamano, se escala con aspect ratio). Se usan dentro de cada
  contenedor y en la animacion de caida.
- `stepper_1.png` / `stepper_2.png` (~98x48): los dos frames del
  motor. Se alternan mientras el stepper gira para simular el
  movimiento circular; los 3 contenedores usan el mismo par. Sin
  ellas se dibuja una cajita con el texto "STEPPER n".
- `fondo.png` (~460x680), `bandeja_0.png` / `bandeja_1.png`
  (~230x110): opcionales, con fallback dibujado.
- La carpeta `bg/` tiene los fondos del editor por tema (temas.json).

## Instalacion (Windows)

1. Python 3.10+ (python.org, "Add to PATH").
2. Icarus Verilog: https://bleyer.org/icarus/ ("agregar al PATH").
3. Opcional: `pip install -r requirements.txt` (pillow, para jpg y
   mejor escalado).
4. `python app.py`

## Robustez

- Timeouts de compilacion (20s) y simulacion (15s) + watchdog dentro
  del testbench: un loop infinito no cuelga la app.
- Errores de iverilog traducidos con linea y pista.
- Si falta Icarus o GTKWave, la app avisa con instrucciones.

## Visor de senales (GTKWave, opcional)

Boton **Senales**: abre GTKWave con la sesion completa y las senales
en orden didactico: sensor_entrada, estado de la FSM, inicioN, el
tren de pulsos paso_pinN con ocupadoN, sensor_salida y led. GTKWave
puede ir embebido en el proyecto (ver GTKWAVE_DIRS en config.py).
