`timescale 1ns/1ps

// Digital portion of the PLL. This wrapper is the implementation counterpart
// of the XSPICE PFD and divider simulation schematics.
module pll_digital (
    input  wire        ref_clk,
    input  wire        vco_clk,
    input  wire        reset_n,
    input  wire        enable,
    input  wire [9:0]  div_ratio,
    input  wire [1:0]  test_div_select,
    output wire        feedback_clk,
    output wire        pll_clk,
    output wire        test_clk,
    output wire        up,
    output wire        down
);
    fractional_divider feedback_divider_i (
        .vco_clk(vco_clk),
        .reset_n(reset_n),
        .enable(enable),
        .integer_div(div_ratio[9:3]),
        .fractional_num(div_ratio[2:0]),
        .feedback_clk(feedback_clk)
    );

    pll_pfd pfd_i (
        .ref_clk(ref_clk),
        .feedback_clk(feedback_clk),
        .reset_n(reset_n && enable),
        .up(up),
        .down(down)
    );

    clock_output_divider output_divider_i (
        .vco_clk(vco_clk),
        .reset_n(reset_n),
        .enable(enable),
        .test_div_sel(test_div_select),
        .pll_clk(pll_clk),
        .test_clk(test_clk)
    );
endmodule
