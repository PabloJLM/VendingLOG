# Reporte: RTL de la chiclera fisica

Explicacion de los tres modulos que te dieron, como se conectan, sus
numeros de timing, y las cosas a tener en cuenta (incluyendo un par de
detalles finos que afectan al simulador y al hardware real).

## Vision general

```
                 +--------------------------------------+
                 |                 top                  |
                 |                                      |
  sensor_entrada |  +---------+  inicio1  +---------+   | paso_pin1
  sensor_salida ---->| control|---------->| stepper |----> dir_pin1
  color[1:0]     |  |  (FSM)  |  inicio2  |  motor1 |   | ocupado1
  dir_entrada    |  |         |---------->+---------+   |
                 |  |         |           | stepper |----> paso_pin2 ...
                 |  |         |  inicio3  |  motor2 |   |
             led <--|         |---------->+---------+   |
                 |  +---------+           | stepper |----> paso_pin3 ...
                 |                        |  motor3 |   |
                 |                        +---------+   |
                 +--------------------------------------+
```

Hay 3 contenedores independientes, uno por color, y cada uno tiene su
propio motor paso a paso que empuja el chicle desde el contenedor
hasta el punto central de recoleccion. La FSM (`control`) decide CUAL
de los 3 motores arranca segun `color`; cada `stepper` genera el tren
de pulsos que hace girar ese motor; `top` los cablea y fija los
parametros (vueltas y velocidad, iguales para los tres).

El sensor de salida es UNO SOLO y esta en el punto central: no importa
de que contenedor venga el chicle, todos pasan por ahi, por eso la FSM
espera el mismo `sensor_salida` sin importar que motor haya girado.

## control.v - la FSM (esto es lo que modifican los estudiantes)

Maquina de 4 estados, codificados en 2 bits:

| Estado | Codigo | Que hace |
|---|---|---|
| RESET  | 00 | Estado de arranque; salta directo a ESPERA |
| ESPERA | 01 | Espera el flanco de subida de `sensor_entrada` (la moneda) |
| INICIO | 10 | UN ciclo: prende `inicio1`, `inicio2` o `inicio3` segun `color` |
| EXITO  | 11 | Espera `sensor_salida` (el chicle cayo); mientras tanto `led = sensor_salida` |

Detalles importantes:

1. **Detector de flanco**: `sensor_entrada_flanco = sensor_entrada &
   ~sensor_entrada_q`. Sin esto, si la moneda mantiene el sensor en
   alto varios ciclos, la FSM dispararia varias veces. Con el flanco,
   una moneda = un disparo, sin importar cuanto dure la senal.

2. **Reset asincrono activo en BAJO**: los `always` usan
   `posedge clk or negedge rst` con `if (!rst)`. O sea el sistema esta
   en reset cuando `rst = 0` y funciona cuando `rst = 1`. Esto es lo
   contrario del rst activo-alto tipico de los ejemplos de clase - el
   testbench del simulador ya lo maneja (arranca con rst=0 y lo sube).

3. **`inicioN` dura exactamente 1 ciclo**: el estado INICIO
   transiciona a EXITO en el siguiente flanco, y las salidas son
   combinacionales del estado. Al stepper le alcanza porque muestrea
   `inicio` estando en IDLE.

4. **`led` es una salida Mealy**: `led = sensor_salida` SOLO mientras
   la FSM esta en EXITO. Como al detectar `sensor_salida` la FSM
   vuelve a ESPERA en el siguiente flanco, el led fisicamente prende
   un instante muy corto (lo que dure el pulso del sensor). En el
   simulador hubo que "atrapar" ese pulso con un registro para poder
   mostrarlo, porque muestreando despues del flanco ya no esta. En el
   hardware real, si quieren que el led se vea, conviene estirarlo
   (por ejemplo un contador que lo mantenga prendido unos cientos de
   ms) - buen ejercicio para los estudiantes.

5. **`color = 2'b11` no hace nada**: el case de INICIO no prende
   ningun motor y la FSM igual pasa a EXITO... donde se queda
   ESPERANDO un `sensor_salida` que nunca va a llegar (ningun motor
   giro, ninguna bola cae). La maquina queda trabada hasta el reset.
   Es el bug mas interesante del RTL tal como esta: un buen ejercicio
   es pedirles que lo arreglen (por ejemplo, volver a ESPERA si el
   color es invalido).

## stepper.v - el generador de pasos

FSM de 2 estados (IDLE / GENERANDO) que produce un tren de pulsos:

- En IDLE, si `inicio` y `pasos > 0`: captura la direccion y la
  cantidad de pasos, y pasa a GENERANDO con `ocupado = 1`.
- En GENERANDO, un contador divide el reloj: cada vez que llega a
  `velocidad` hace toggle de `pasos_motor`. Un paso completo del motor
  son DOS toggles (subida y bajada), y el descuento de `dif_pasos`
  ocurre en el toggle de bajada.
- Cuando `dif_pasos` llega a 0: `ocupado = 0` y vuelve a IDLE.

`ocupado` es la senal clave para el mundo exterior: esta en 1 todo el
tiempo que el motor gira. El simulador la usa para saber cuando
"cae" la bola.

### Matematica del timing

- Periodo de un toggle = `velocidad + 1` ciclos de clk.
- Periodo de un paso completo = `2 * (velocidad + 1)` ciclos.
- Duracion total del giro = `pasos * 2 * (velocidad + 1)` ciclos.

Con los valores de `top.v` (400 pasos, velocidad = 5):
`400 * 2 * 6 = 4800 ciclos` por dispensado.

**Ojo con esto en hardware real**: con un clk de 50 MHz, 4800 ciclos
son 96 microsegundos - ningun motor fisico puede girar 2 vueltas en
ese tiempo. `VELOCIDad = 5` es claramente un valor de simulacion.
Para un motor real a ~500 pasos/segundo con clk de 50 MHz se
necesitaria `velocidad ~ 50000`. Es un parametro, asi que se cambia
en `top.v` sin tocar nada mas (y el simulador seguiria funcionando,
solo tardaria mas cada corrida).

Nota menor: el parametro `PASOS_POR_VUELTA` del stepper esta declarado
pero no se usa dentro del modulo; solo documenta la intencion. La
cantidad real de pasos entra por el puerto `pasos`.

## top.v - el integrador

- Instancia 1 `control` + 3 `stepper` identicos.
- Fija `PASOS_2_VUELTAS = 400` (2 vueltas de 200 pasos) y
  `VELOCIDAD = 5` para los tres motores.
- `dir_entrada` va directo a los 3 steppers: la direccion de giro es
  global, no por motor.
- Expone hacia afuera: `led`, los 3 `ocupadoN` (util para debug o
  para encadenar logica), y los pines fisicos `paso_pinN` / `dir_pinN`
  que van a los drivers de los motores.

## Como lo usa el simulador

El estudiante edita `control.v` en el editor. Al compilar, el
simulador junta: su `control.v` + `stepper.v` + `top.v` (fijos) + un
`testbench.v` propio que ademas de generar el reloj EMULA LA PLANTA
FISICA: cuando detecta que un `ocupadoN` termina (el motor dejo de
girar), espera unos ciclos (la bola cayendo) y pulsa `sensor_salida`,
igual que haria el sensor optico de la maquina real. Con eso el ciclo
completo moneda -> motor -> bola -> led funciona en simulacion sin
ningun hardware.

Que se ve en GTKWave (boton Senales): el pulso de `sensor_entrada`,
el estado de la FSM (`estado_actual`), el pulso de 1 ciclo de
`inicioN`, el tren de pulsos de `paso_pinN` con `ocupadoN` en alto
durante todo el giro, el pulso de `sensor_salida` y el `led`.

## Ideas de ejercicios sobre este RTL

1. Arreglar el caso `color = 2'b11` (maquina trabada).
2. Estirar el `led` de exito N ciclos para que se vea.
3. Agregar un timeout en EXITO: si la bola nunca cae (atasco), volver
   a ESPERA y prender un led de error.
4. Contador de chicles vendidos por color.
5. Cambiar la FSM a codificacion one-hot y comparar recursos.
