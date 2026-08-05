// Testbench fijo (el estudiante NO lo ve). Instancia el top completo y
// emula la planta: al terminar un motor, pulsa sensor_salida.
// events.hex: 0x3c color=c | 0x1_ moneda | 0xFF fin
`timescale 1ns/1ps

module testbench;
    localparam SETTLE = 2;

    reg        clk = 0, rst = 0;          // rst activo en BAJO (async)
    reg        sensor_entrada = 0, sensor_salida = 0, dir_entrada = 0;
    reg  [1:0] color = 2'b00;
    wire       led, ocupado1, ocupado2, ocupado3;
    wire       paso_pin1, paso_pin2, paso_pin3;
    wire       dir_pin1, dir_pin2, dir_pin3;

    top dut (
        .clk(clk), .rst(rst),
        .sensor_entrada(sensor_entrada), .sensor_salida(sensor_salida),
        .dir_entrada(dir_entrada), .color(color),
        .led(led),
        .ocupado1(ocupado1), .ocupado2(ocupado2), .ocupado3(ocupado3),
        .paso_pin1(paso_pin1), .paso_pin2(paso_pin2), .paso_pin3(paso_pin3),
        .dir_pin1(dir_pin1), .dir_pin2(dir_pin2), .dir_pin3(dir_pin3)
    );

    always #5 clk = ~clk;

    initial begin
        #20000000;
        $display("TB_WATCHDOG_TIMEOUT");
        $finish;
    end

    initial if ($test$plusargs("vcd")) begin
        $dumpfile("wave.vcd");
        $dumpvars(0, testbench);
    end

    wire ocupado_any = ocupado1 | ocupado2 | ocupado3;

    // el led de exito es un pulso combinacional muy corto (Mealy):
    // lo capturamos con un registro para que no se pierda en el log
    reg led_visto = 0, clr_led = 0;
    always @(posedge clk) begin
        if (clr_led)
            led_visto <= 1'b0;
        else if (led)
            led_visto <= 1'b1;
    end

    reg [7:0] events [0:1023];
    reg [7:0] ev;
    reg [6:0] vec, prev_vec;
    integer   fd, i, j, t, cycle, ev_idx, prev_ev;

    // un ciclo de reloj; escribe fila solo si algo cambio
    task step;
        begin
            @(posedge clk);
            #1;
            cycle = cycle + 1;
            vec = {led_visto, ocupado1, ocupado2, ocupado3,
                   sensor_salida, color};
            if (vec !== prev_vec || ev_idx != prev_ev) begin
                $fwrite(fd, "%0d,%0d,%b,%b,%b,%b,%b,%0d\n",
                        cycle, ev_idx, led_visto, ocupado1, ocupado2,
                        ocupado3, sensor_salida, color);
                prev_vec = vec;
                prev_ev  = ev_idx;
            end
        end
    endtask

    initial begin
        for (i = 0; i < 1024; i = i + 1) events[i] = 8'hFF;
        $readmemh("events.hex", events);

        fd = $fopen("output.csv", "w");
        $fwrite(fd, "cycle,event,led,oc1,oc2,oc3,salida,color\n");
        cycle = 0;
        ev_idx = -1;
        prev_ev = -2;
        prev_vec = 7'h7f;

        rst = 0; step; step;                 // reset activo en bajo
        rst = 1; step;

        for (i = 0; i < 1024 && events[i] != 8'hFF; i = i + 1) begin
            ev_idx = i;
            ev = events[i];
            case (ev[7:4])
                4'h3: color = ev[1:0];

                4'h1: begin
                    // limpiar la memoria del led de exito
                    clr_led = 1; step; clr_led = 0;
                    // moneda: pulso del sensor de entrada
                    sensor_entrada = 1; step; step; sensor_entrada = 0;

                    // planta: esperar a que algun motor arranque
                    t = 0;
                    while (!ocupado_any && t < 100) begin
                        step; t = t + 1;
                    end
                    if (ocupado_any) begin
                        // esperar a que el motor termine de girar
                        t = 0;
                        while (ocupado_any && t < 200000) begin
                            step; t = t + 1;
                        end
                        // la bola cae hasta el sensor de salida
                        repeat (10) step;
                        sensor_salida = 1;
                        repeat (3) step;
                        sensor_salida = 0;
                    end
                end
                default: ;
            endcase
            for (j = 0; j < SETTLE; j = j + 1) step;
        end

        $fclose(fd);
        $display("TB_DONE");
        $finish;
    end

endmodule
