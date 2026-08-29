`timescale 1ns/1ps

// Synthesizable resettable dual-DFF phase-frequency detector. The XSPICE
// pfd.sch model adds explicit gate delays for transistor-level loop simulation.
module pll_pfd (
    input  wire ref_clk,
    input  wire feedback_clk,
    input  wire reset_n,
    output reg  up,
    output reg  down
);
    wire clear = !reset_n || (up && down);

    always @(posedge ref_clk or posedge clear) begin
        if (clear)
            up <= 1'b0;
        else
            up <= 1'b1;
    end

    always @(posedge feedback_clk or posedge clear) begin
        if (clear)
            down <= 1'b0;
        else
            down <= 1'b1;
    end
endmodule
