// FSM de la chiclera - completa los TODO.
// No cambies el nombre del modulo ni sus puertos.
// OJO: rst es asincrono y ACTIVO EN BAJO (se resetea con rst = 0).

module control (
    input clk, rst, sensor_entrada, sensor_salida,
    input [1:0] color,
    output reg led, inicio1, inicio2, inicio3
);

parameter [1:0] RESET  = 2'b00, ESPERA = 2'b01, INICIO = 2'b10, EXITO  = 2'b11;
reg [1:0] estado_actual, estado_siguiente;

// Detector de flanco: guarda el valor anterior del sensor
reg sensor_entrada_q;

always @(posedge clk or negedge rst) begin
    if (!rst)
        sensor_entrada_q <= 1'b0;
    else
        sensor_entrada_q <= sensor_entrada;
end

// TODO 1: vale 1 solo en el ciclo en que sensor_entrada pasa de 0 a 1
wire sensor_entrada_flanco = 1'b0;

// TODO 2: guardar el estado siguiente en cada flanco de clk
always @(posedge clk or negedge rst) begin
    if (!rst)
        estado_actual <= RESET;
    else
        estado_actual <= estado_actual;
end

// TODO 3: transiciones y salidas de cada estado
always @(*) begin
    estado_siguiente = estado_actual;
    inicio1 = 1'b0;
    inicio2 = 1'b0;
    inicio3 = 1'b0;
    led     = 1'b0;

    case (estado_actual)
        RESET: begin
            // TODO: pasar a ESPERA
        end

        ESPERA: begin
            // TODO: si hay flanco de moneda, pasar a INICIO
        end

        INICIO: begin
            // TODO: segun color (00 / 01 / 10) prender inicio1, inicio2 o inicio3
            // TODO: pasar a EXITO
        end

        EXITO: begin
            // TODO: led = sensor_salida
            // TODO: cuando el chicle llegue al sensor, volver a ESPERA
        end

        default: estado_siguiente = RESET;
    endcase
end

endmodule
