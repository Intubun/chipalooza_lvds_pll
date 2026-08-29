`timescale 1ns/1ps

// Binary output divider for the internal LVDS clock and external test clock.
// pll_clk is always VCO/2. test_div_sel selects VCO/2, /4, /8, or /16.
module clock_output_divider (
    input  wire       vco_clk,
    input  wire       reset_n,
    input  wire       enable,
    input  wire [1:0] test_div_sel,
    output wire       pll_clk,
    output reg        test_clk
);
    reg [3:0] count;

    always @(posedge vco_clk) begin
        if (!reset_n || !enable)
            count <= 4'b0000;
        else
            count <= count + 1'b1;
    end

    assign pll_clk = count[0];

    always @* begin
        case (test_div_sel)
            2'b00: test_clk = count[0];
            2'b01: test_clk = count[1];
            2'b10: test_clk = count[2];
            default: test_clk = count[3];
        endcase
    end
endmodule
