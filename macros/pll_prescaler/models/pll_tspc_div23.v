`timescale 1ns/1ps

// Functional-pin black box for synthesis and physical implementation. VDD and
// VSS are physical LEF pins connected by the P&R global-power network.
(* blackbox *)
module pll_tspc_div23 (
    input  wire CLK,
    input  wire RESET_B,
    input  wire MODULUS_REQUEST,
    output wire Q2
);
endmodule

(* blackbox *)
module pll_tspc_div2 (
    input  wire CLK,
    input  wire RESET_B,
    output wire Q
);
endmodule
