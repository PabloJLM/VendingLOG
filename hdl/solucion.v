// =====================================================================
// solucion.v — SOLUCIÓN de referencia (uso del docente, no distribuir)
//
// Interfaz mínima: la máquina (GUI) le dice al hardware el precio y si
// hay stock del producto elegido. El estudiante solo diseña la lógica
// del dinero:
//   1) SATURACIÓN: sumar la ficha en 4 bits (un bit extra) y recortar
//      en 7. El crédito nunca "da la vuelta" a 0.
//   2) COMPARAR ANTES DE RESTAR: vuelto = credito - precio se calcula
//      SOLO tras validar credito >= precio. En unsigned, 2-5 no da
//      "negativo": da un número grande (wraparound), y hay que evitarlo.
//   3) motor_on como pulso limpio de 1 ciclo; si no se puede comprar,
//      el crédito SE CONSERVA.
// =====================================================================

module vending_machine (
    input        clk,
    input        rst,
    input        ficha_1,      // pulso: entró ficha de valor 1
    input        ficha_5,      // pulso: entró ficha de valor 5
    input  [2:0] precio,       // precio del producto elegido (lo da la máquina)
    input        hay_stock,    // 1 = el producto elegido tiene stock
    input        btn_comprar,  // pulso: confirmar compra
    output reg       motor_on, // pulso: dispensar
    output reg [2:0] credito,  // crédito acumulado (máximo 7)
    output reg       listo,    // 1 = el crédito alcanza el precio
    output reg [2:0] vuelto    // vuelto de la última compra
);

    reg [3:0] suma;            // suma con un bit extra (máx 7+5 = 12)

    always @(posedge clk) begin
        if (rst) begin
            credito  <= 3'd0;
            motor_on <= 1'b0;
            vuelto   <= 3'd0;
        end else begin
            motor_on <= 1'b0;                 // pulso de 1 solo ciclo

            // Fichas: acumular con SATURACIÓN en 7
            if (ficha_1 || ficha_5) begin
                suma = {1'b0, credito} + (ficha_1 ? 4'd1 : 4'd0)
                                       + (ficha_5 ? 4'd5 : 4'd0);
                credito <= (suma > 4'd7) ? 3'd7 : suma[2:0];
            end

            // Compra: COMPARAR ANTES DE RESTAR
            if (btn_comprar && hay_stock && credito >= precio) begin
                vuelto   <= credito - precio; // resta ya validada: segura
                credito  <= 3'd0;
                motor_on <= 1'b1;
            end
            // Sin stock o sin crédito: no pasa nada, el crédito se conserva.
        end
    end

    // Salida combinacional: ¿alcanza el crédito?
    always @* listo = (credito >= precio);

endmodule
