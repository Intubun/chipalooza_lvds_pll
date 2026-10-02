`timescale 1ns/1ps

// Portable toggle stage. Synthesis can implement this with an ordinary DFF
// plus inversion; a PDK-specific technology map may replace the module with a
// complementary-output DFF without putting physical cell names in the RTL.
module async_toggle_ff (
    input  wire clk,
    input  wire reset_b,
    output reg  q
);
    always @(posedge clk or negedge reset_b) begin
        if (!reset_b)
            q <= 1'b0;
        else
            q <= ~q;
    end
endmodule

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
    wire reset_b = reset_n && enable;
    wire div2_clk;
    wire div4_clk;
    wire div8_clk;
    wire div16_clk;

    // Only the first stage sees the full VCO rate. Later stages form an
    // asynchronous ripple chain.
    async_toggle_ff div2_ff (
        .clk(vco_clk), .reset_b(reset_b), .q(div2_clk)
    );
    async_toggle_ff div4_ff (
        .clk(div2_clk), .reset_b(reset_b), .q(div4_clk)
    );
    async_toggle_ff div8_ff (
        .clk(div4_clk), .reset_b(reset_b), .q(div8_clk)
    );
    async_toggle_ff div16_ff (
        .clk(div8_clk), .reset_b(reset_b), .q(div16_clk)
    );

    assign pll_clk = div2_clk;

    always @* begin
        case (test_div_sel)
            2'b00: test_clk = div2_clk;
            2'b01: test_clk = div4_clk;
            2'b10: test_clk = div8_clk;
            default: test_clk = div16_clk;
        endcase
    end
endmodule
