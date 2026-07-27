//SOLUCIOOOON No ensenar xd
module vending_machine (
    input        clk,
    input        rst,
    input        ficha_1,
    input        ficha_5,
    input  [3:0] producto,     // 0-8: producto elegido
    input        hay_stock,    // 1 = el producto elegido tiene stock
    input        btn_comprar,
    output reg       motor_on,
    output reg [2:0] credito,
    output reg       listo,
    output reg [2:0] vuelto,
    output reg       error     // flag: overflow o resta invalida
);

    // Precio de cada producto (case de la vending)
    reg [2:0] precio;
    always @* begin
        case (producto)
            4'd0: precio = 3'd2;   // Chips
            4'd1: precio = 3'd3;   // Galletas
            4'd2: precio = 3'd5;   // Soda
            4'd3: precio = 3'd1;   // Chicle
            4'd4: precio = 3'd4;   // Agua
            4'd5: precio = 3'd7;   // Chocolate
            4'd6: precio = 3'd6;   // Cafe
            4'd7: precio = 3'd2;   // Caramelo
            4'd8: precio = 3'd3;   // Jugo
            default: precio = 3'd7;
        endcase
    end

    reg [3:0] suma;              // un bit extra para ver el overflow

    always @(posedge clk) begin
        if (rst) begin
            credito  <= 3'd0;
            motor_on <= 1'b0;
            vuelto   <= 3'd0;
            error    <= 1'b0;
        end else begin
            motor_on <= 1'b0;

            if (ficha_1 || ficha_5) begin
                suma = {1'b0, credito} + (ficha_1 ? 4'd1 : 4'd0)
                                       + (ficha_5 ? 4'd5 : 4'd0);
                if (suma > 4'd7) begin
                    credito <= 3'd7;      // saturar, nunca dar la vuelta
                    error   <= 1'b1;      // flag: overflow en la suma
                end else begin
                    credito <= suma[2:0];
                    error   <= 1'b0;
                end
            end

            if (btn_comprar) begin
                if (hay_stock && credito >= precio) begin
                    vuelto   <= credito - precio;  // resta ya validada
                    credito  <= 3'd0;
                    motor_on <= 1'b1;
                    error    <= 1'b0;
                end else begin
                    error <= 1'b1;        // flag: resta negativa o sin stock
                end                       // el credito se conserva
            end
        end
    end

    always @* listo = (credito >= precio);

endmodule
