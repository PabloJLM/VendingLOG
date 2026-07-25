// =====================================================================
// testbench.v — Testbench fijo del simulador (el estudiante NO lo ve)
//
// Batch replay: lee TODA la historia desde "events.hex", instancia el
// módulo del estudiante y vuelca el estado a "output.csv" por ciclo.
//
// events.hex: un byte hex por línea (nibble alto = opcode, bajo = arg)
//   0x1_  ficha_1 (pulso)
//   0x2_  ficha_5 (pulso)
//   0x3h  selección: h = {hay_stock, precio[2:0]}  (queda fijo)
//   0x4_  btn_comprar (pulso)
//   0xFF  fin
//
// Docente: "vvp sim.vvp +vcd" genera wave.vcd para GTKWave.
// =====================================================================
`timescale 1ns/1ps

module testbench;
    localparam SETTLE = 2;            // ciclos entre eventos

    reg        clk = 0, rst = 1;
    reg        ficha_1 = 0, ficha_5 = 0, btn_comprar = 0;
    reg  [2:0] precio = 3'd7;         // sin selección: precio alto
    reg        hay_stock = 0;
    wire       motor_on, listo;
    wire [2:0] credito, vuelto;

    vending_machine dut (
        .clk(clk), .rst(rst),
        .ficha_1(ficha_1), .ficha_5(ficha_5),
        .precio(precio), .hay_stock(hay_stock),
        .btn_comprar(btn_comprar),
        .motor_on(motor_on), .credito(credito),
        .listo(listo), .vuelto(vuelto)
    );

    always #5 clk = ~clk;

    initial begin                     // watchdog
        #2000000;
        $display("TB_WATCHDOG_TIMEOUT");
        $finish;
    end

    initial if ($test$plusargs("vcd")) begin
        $dumpfile("wave.vcd");
        $dumpvars(0, testbench);
    end

    reg [7:0] events [0:1023];
    reg [7:0] ev;
    integer   fd, i, j, cycle, ev_idx;

    task step;                        // un ciclo + una fila del CSV
        begin
            @(posedge clk);
            #1;
            cycle = cycle + 1;
            $fwrite(fd, "%0d,%0d,%b,%0d,%b,%0d\n",
                    cycle, ev_idx, motor_on, credito, listo, vuelto);
        end
    endtask

    initial begin
        for (i = 0; i < 1024; i = i + 1) events[i] = 8'hFF;
        $readmemh("events.hex", events);

        fd = $fopen("output.csv", "w");
        $fwrite(fd, "cycle,event,motor_on,credito,listo,vuelto\n");
        cycle = 0;
        ev_idx = -1;

        rst = 1; step; step;
        rst = 0; step;

        for (i = 0; i < 1024 && events[i] != 8'hFF; i = i + 1) begin
            ev_idx = i;
            ev = events[i];
            case (ev[7:4])
                4'h1: begin ficha_1 = 1;     step; ficha_1 = 0;     end
                4'h2: begin ficha_5 = 1;     step; ficha_5 = 0;     end
                4'h3: begin precio = ev[2:0]; hay_stock = ev[3];    end
                4'h4: begin btn_comprar = 1; step; btn_comprar = 0; end
                default: ;
            endcase
            for (j = 0; j < SETTLE; j = j + 1) step;
        end

        $fclose(fd);
        $display("TB_DONE");
        $finish;
    end

endmodule
