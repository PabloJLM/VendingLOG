module vending_machine (
    input        clk,
    input        rst,
    input        ficha_1,      // pulso: ficha de valor 1
    input        ficha_5,      // pulso: ficha de valor 5
    input  [3:0] producto,     // 0-8: producto elegido
    input        hay_stock,    // 1 = el producto elegido tiene stock
    input        btn_comprar,  // pulso: confirmar compra
    output reg       motor_on, // pulso: dispensar
    output reg [2:0] credito,  // credito acumulado (maximo 7)
    output reg       listo,    // 1 = el credito alcanza el precio
    output reg [2:0] vuelto,   // vuelto de la ultima compra
    output reg       error     // flag: overflow o resta invalida
);

    // 1. Precio de cada producto - completa el case:
    //    0 Chips $2 | 1 Galletas $3 | 2 Soda $5 | 3 Chicle $1 | 4 Agua $4
    //    5 Chocolate $7 | 6 Cafe $6 | 7 Caramelo $2 | 8 Jugo $3
    reg [2:0] precio;
    always @* begin
        case (producto)
            4'd0: precio = 3'd2;      // Chips vale 2
            4'd1: precio = 3'd0;      // TODO
            4'd2: precio = 3'd0;      // TODO
            4'd3: precio = 3'd0;      // TODO
            4'd4: precio = 3'd0;      // TODO
            4'd5: precio = 3'd0;      // TODO
            4'd6: precio = 3'd0;      // TODO
            4'd7: precio = 3'd0;      // TODO
            4'd8: precio = 3'd0;      // TODO
            default: precio = 3'd7;
        endcase
    end

    always @(posedge clk) begin
        if (rst) begin
            // TODO: credito, motor_on, vuelto y error en 0.

        end else begin
            // TODO: motor_on debe ser un pulso de UN solo ciclo.

            // TODO 2: fichas con saturacion en 7 + flag error si hay overflow.

            // TODO 3: compra validando ANTES de restar + flag error.

        end
    end

    // TODO 4:
    always @* listo = 1'b0;

endmodule
