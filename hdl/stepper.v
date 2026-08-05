module stepper #(
    parameter PASOS_POR_VUELTA = 200
)(
    input clk, rst, inicio, dir_entrada,
    input [15:0] pasos,
    input [31:0] velocidad,
    output reg pasos_motor,
    output reg dir_salida,
    output reg ocupado
);

reg [31:0] contador;
reg [15:0] dif_pasos;
reg estado_actual;

always @(posedge clk or negedge rst) begin
    if (!rst) begin
        contador      <= 0;
        dif_pasos     <= 0;
        pasos_motor   <= 0;
        dir_salida    <= 0;
        ocupado       <= 0;
        estado_actual <= 0;
    end else begin
        case (estado_actual)
            1'b0: begin // IDLE
                if (inicio && pasos > 0) begin
                    dir_salida    <= dir_entrada;
                    dif_pasos     <= pasos;
                    contador      <= 0;
                    ocupado       <= 1'b1;
                    estado_actual <= 1'b1;
                end else begin
                    ocupado <= 1'b0;
                end
            end

            1'b1: begin // GENERANDO PASOS
                if (dif_pasos == 0) begin
                    ocupado       <= 1'b0;
                    estado_actual <= 1'b0;
                end else if (contador >= velocidad) begin
                    contador    <= 0;
                    pasos_motor <= ~pasos_motor;
                    if (pasos_motor == 1'b1)
                        dif_pasos <= dif_pasos - 1'b1;
                end else begin
                    contador <= contador + 1'b1;
                end
            end
        endcase
    end
end

endmodule