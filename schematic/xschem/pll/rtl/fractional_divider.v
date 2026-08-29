`timescale 1ns/1ps

// Programmable N/N+1 feedback divider.
//
// The output is a one-VCO-cycle pulse. Its rising edge occurs after either
// integer_div or integer_div+1 VCO cycles. The fractional accumulator selects
// the longer periods so the average ratio is:
//
//     integer_div + fractional_num / 2^FRAC_WIDTH
//
// Set fractional_num to zero for integer-N operation. integer_div must be >= 4
// for the PLL operating range.
module fractional_divider #(
    parameter integer DIV_WIDTH = 7,
    parameter integer FRAC_WIDTH = 16
) (
    input  wire                  vco_clk,
    input  wire                  reset_n,
    input  wire                  enable,
    input  wire [DIV_WIDTH-1:0]  integer_div,
    input  wire [FRAC_WIDTH-1:0] fractional_num,
    output reg                   feedback_clk
);
    reg [DIV_WIDTH-1:0] counter;
    reg [DIV_WIDTH-1:0] current_divisor;
    reg [FRAC_WIDTH-1:0] accumulator;
    wire [FRAC_WIDTH:0] accumulator_sum =
        {1'b0, accumulator} + {1'b0, fractional_num};

    always @(posedge vco_clk) begin
        if (!reset_n || !enable) begin
            counter         <= {DIV_WIDTH{1'b0}};
            current_divisor <= integer_div;
            accumulator     <= {FRAC_WIDTH{1'b0}};
            feedback_clk    <= 1'b0;
        end else if (counter == current_divisor - 1'b1) begin
            counter         <= {DIV_WIDTH{1'b0}};
            feedback_clk    <= 1'b1;
            accumulator     <= accumulator_sum[FRAC_WIDTH-1:0];
            current_divisor <= integer_div + accumulator_sum[FRAC_WIDTH];
        end else begin
            counter      <= counter + 1'b1;
            feedback_clk <= 1'b0;
        end
    end
endmodule
