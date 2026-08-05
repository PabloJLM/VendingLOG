module control (
    input clk, rst, sensor_entrada, sensor_salida,
    input [1:0] color,
    output reg led, inicio1, inicio2, inicio3
);

parameter [1:0] RESET  = 2'b00, ESPERA = 2'b01, INICIO = 2'b10, EXITO  = 2'b11;
reg [1:0] estado_actual, estado_siguiente;

// ---- Detección de flanco de subida de sensor_entrada ----
reg sensor_entrada_q;
wire sensor_entrada_flanco = sensor_entrada & ~sensor_entrada_q;

always @(posedge clk or negedge rst) begin
    if (!rst)
        sensor_entrada_q <= 1'b0;
    else
        sensor_entrada_q <= sensor_entrada;
end

// ---- Registro de estado ----
always @(posedge clk or negedge rst) begin
    if (!rst)
        estado_actual <= RESET;
    else
        estado_actual <= estado_siguiente;
end

// ---- Lógica de siguiente estado + salidas ----
always @(*) begin
    estado_siguiente = estado_actual;
    inicio1 = 1'b0;
    inicio2 = 1'b0;
    inicio3 = 1'b0;
    led     = 1'b0;

    case (estado_actual)
        RESET: begin
            estado_siguiente = ESPERA;
        end

        ESPERA: begin
            if (sensor_entrada_flanco)
                estado_siguiente = INICIO;
        end

        INICIO: begin
            case (color)
                2'b00: inicio1 = 1'b1;
                2'b01: inicio2 = 1'b1;
                2'b10: inicio3 = 1'b1;
                default: ; // 2'b11: ningún motor
            endcase
            estado_siguiente = EXITO;
        end

        EXITO: begin
            led = sensor_salida;
            if (sensor_salida)
                estado_siguiente = ESPERA;
        end

        default: estado_siguiente = RESET;
    endcase
end

endmodule