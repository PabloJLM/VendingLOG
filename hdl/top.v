module top (
    input clk, rst, sensor_entrada, sensor_salida, dir_entrada,
    input  wire [1:0] color,
    output wire led, ocupado1, ocupado2, ocupado3, 
    output wire paso_pin1, paso_pin2, paso_pin3,
    output wire dir_pin1,  dir_pin2,  dir_pin3
);

localparam PASOS_POR_VUELTA        = 200;                
localparam [15:0] PASOS_2_VUELTAS  = 2 * PASOS_POR_VUELTA; // = 400 pasos
localparam [31:0] VELOCIDAD        = 32'd5;      

wire inicio1, inicio2, inicio3;

control u_control (
    .clk            (clk),
    .rst          (rst),
    .sensor_entrada (sensor_entrada),
    .sensor_salida  (sensor_salida),
    .color          (color),
    .inicio1        (inicio1),
    .inicio2        (inicio2),
    .inicio3        (inicio3),
    .led            (led)
);

stepper #(.PASOS_POR_VUELTA(PASOS_POR_VUELTA)) u_motor1 (
    .clk         (clk),
    .rst       (rst),
    .inicio      (inicio1),
    .dir_entrada (dir_entrada),
    .pasos       (PASOS_2_VUELTAS),
    .velocidad   (VELOCIDAD),
    .pasos_motor (paso_pin1),
    .dir_salida  (dir_pin1),
    .ocupado     (ocupado1)
);

// ---- Motor 2 ----
stepper #(.PASOS_POR_VUELTA(PASOS_POR_VUELTA)) u_motor2 (
    .clk         (clk),
    .rst       (rst),
    .inicio      (inicio2),
    .dir_entrada (dir_entrada),
    .pasos       (PASOS_2_VUELTAS),
    .velocidad   (VELOCIDAD),
    .pasos_motor (paso_pin2),
    .dir_salida  (dir_pin2),
    .ocupado     (ocupado2)
);

// ---- Motor 3 ----
stepper #(.PASOS_POR_VUELTA(PASOS_POR_VUELTA)) u_motor3 (
    .clk         (clk),
    .rst       (rst),
    .inicio      (inicio3),
    .dir_entrada (dir_entrada),
    .pasos       (PASOS_2_VUELTAS),
    .velocidad   (VELOCIDAD),
    .pasos_motor (paso_pin3),
    .dir_salida  (dir_pin3),
    .ocupado     (ocupado3)
);

endmodule