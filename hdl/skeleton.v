// =====================================================================
// MÁQUINA EXPENDEDORA — Tu módulo Verilog
//
// Completá los TODO. NO cambies el nombre del módulo ni sus puertos.
//
//  1. CASE DE LA VENDING: cada producto tiene su precio.
//     Ej.: producto 2 (Soda) vale 5 → al comprar se restan 5.
//
//  2. FICHAS con saturación: el crédito máximo es 7. Si la suma se
//     pasa, el crédito queda en 7 y encendés el flag "error"
//     (overflow). Pista: sumá en 4 bits (un bit extra).
//
//  3. COMPRA: solo si hay_stock y credito >= precio →
//     motor_on = 1 por UN ciclo, vuelto = credito - precio, credito = 0.
//     Si credito < precio, la resta daría "negativo" (en binario sin
//     signo da un número gigante): NO restes, encendé el flag "error"
//     y conservá el crédito.
//
//  4. listo = 1 cuando el crédito alcanza el precio (combinacional).
// =====================================================================

module vending_machine (
    input        clk,
    input        rst,
    input        ficha_1,      // pulso: ficha de valor 1
    input        ficha_5,      // pulso: ficha de valor 5
    input  [3:0] producto,     // 0-8: producto elegido
    input        hay_stock,    // 1 = el producto elegido tiene stock
    input        btn_comprar,  // pulso: confirmar compra
    output reg       motor_on, // pulso: dispensar
    output reg [2:0] credito,  // crédito acumulado (máximo 7)
    output reg       listo,    // 1 = el crédito alcanza el precio
    output reg [2:0] vuelto,   // vuelto de la última compra
    output reg       error     // flag: overflow o resta inválida
);

    // 1. Precio de cada producto — completá el case:
    //    0 Chips $2 | 1 Galletas $3 | 2 Soda $5 | 3 Chicle $1 | 4 Agua $4
    //    5 Chocolate $7 | 6 Café $6 | 7 Caramelo $2 | 8 Jugo $3
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

            // TODO 2: fichas con saturación en 7 + flag error si hay overflow.

            // TODO 3: compra validando ANTES de restar + flag error.

        end
    end

    // TODO 4:
    always @* listo = 1'b0;

endmodule
