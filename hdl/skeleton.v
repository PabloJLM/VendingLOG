// =====================================================================
// MÁQUINA EXPENDEDORA — Tu módulo Verilog
//
// La máquina te dice el PRECIO del producto elegido y si HAY STOCK.
// Vos solo diseñás la lógica del dinero. Completá los TODO.
// NO cambies el nombre del módulo ni sus puertos.
//
// REGLAS:
//  - Crédito máximo 7: si una ficha lo pasaría, se SATURA en 7 (no
//    debe "dar la vuelta" a 0). Pista: sumá en 4 bits (un bit extra).
//  - Compra (btn_comprar): SOLO si hay_stock y credito >= precio →
//    motor_on = 1 por UN ciclo, vuelto = credito - precio, credito = 0.
//    ¡Validá credito >= precio ANTES de restar! En binario sin signo,
//    2 - 5 no da "negativo": da un número grande (wraparound).
//  - Si no se puede comprar, el crédito SE CONSERVA.
//  - listo = 1 cuando el crédito alcanza el precio.
// =====================================================================

module vending_machine (
    input        clk,
    input        rst,
    input        ficha_1,      // pulso: entró ficha de valor 1
    input        ficha_5,      // pulso: entró ficha de valor 5
    input  [2:0] precio,       // precio del producto elegido
    input        hay_stock,    // 1 = el producto elegido tiene stock
    input        btn_comprar,  // pulso: confirmar compra
    output reg       motor_on, // pulso: dispensar
    output reg [2:0] credito,  // crédito acumulado (máximo 7)
    output reg       listo,    // 1 = el crédito alcanza el precio
    output reg [2:0] vuelto    // vuelto de la última compra
);

    // ---- TU CÓDIGO DESDE ACÁ ---------------------------------------

    always @(posedge clk) begin
        if (rst) begin
            // TODO: inicializar credito, motor_on y vuelto en 0.

        end else begin
            // TODO: motor_on debe ser un pulso de UN solo ciclo.

            // TODO: fichas (ficha_1 / ficha_5) con saturación en 7.

            // TODO: compra (btn_comprar): validar hay_stock y
            //       credito >= precio ANTES de restar.

        end
    end

    // TODO: listo = 1 cuando credito >= precio (combinacional).
    always @* listo = 1'b0;

endmodule
