`timescale 1ns/1ps

// Programmable feedback divider behind a fixed full-rate divide-by-two stage.
//
// The external divide word remains Q7.3. At the half-rate clock it is exactly
// represented as Q6.4:
//
//     base_half = floor(integer_div / 2)
//     half_fraction = {integer_div[0], fractional_num}
//
// The accumulator chooses base_half or base_half+1 half-rate periods per
// interval. Since each half-rate period is two VCO periods, the requested
// average VCO divide ratio is unchanged:
//
//     integer_div + fractional_num / 2^FRAC_WIDTH
//
// Odd integer ratios alternate between adjacent even VCO-cycle intervals.
// integer_div must remain >= 4, making the minimum half-rate count two.
module fractional_divider #(
    parameter integer DIV_WIDTH = 7,
    parameter integer FRAC_WIDTH = 3
) (
    input  wire                  half_clk,
    input  wire                  reset_n,
    input  wire                  enable,
    input  wire [DIV_WIDTH-1:0]  integer_div,
    input  wire [FRAC_WIDTH-1:0] fractional_num,
    output reg                   feedback_clk
);
    localparam integer HALF_WIDTH = DIV_WIDTH;
    localparam integer HALF_FRAC_WIDTH = FRAC_WIDTH + 1;
    localparam integer MAX_HALF_DIVISOR = 1 << (HALF_WIDTH - 1);

    reg interval_active;
    reg reload_base_pending;
    reg reload_plus_pending;
    reg [MAX_HALF_DIVISOR-1:0] countdown;
    reg [HALF_FRAC_WIDTH-1:0] accumulator;

    wire reset_b = reset_n && enable;
    wire [HALF_WIDTH-1:0] base_half_divisor =
        {1'b0, integer_div[DIV_WIDTH-1:1]};
    wire [HALF_FRAC_WIDTH-1:0] half_fraction =
        {integer_div[0], fractional_num};
    wire [HALF_FRAC_WIDTH:0] accumulator_sum =
        {1'b0, accumulator} + {1'b0, half_fraction};
    wire [HALF_WIDTH-1:0] base_minus_one = base_half_divisor - 1'b1;

    wire [MAX_HALF_DIVISOR-1:0] base_countdown =
        {{(MAX_HALF_DIVISOR-1){1'b0}}, 1'b1} << base_minus_one;
    wire [MAX_HALF_DIVISOR-1:0] plus_one_countdown =
        {base_countdown[MAX_HALF_DIVISOR-2:0], 1'b0};
    wire use_plus_one = accumulator_sum[HALF_FRAC_WIDTH];
    wire load_base = !interval_active || reload_base_pending;
    wire load_plus_one = reload_plus_pending;

    // At terminal count the token is bit zero, so shifting it produces zero.
    // Reload can therefore be ORed into the unconditional shift without a
    // terminal-select mux. Both masks are decoded from static configuration.
    always @(posedge half_clk or negedge reset_b) begin
        if (!reset_b)
            countdown <= {MAX_HALF_DIVISOR{1'b0}};
        else
            countdown <= {1'b0, countdown[MAX_HALF_DIVISOR-1:1]} |
                ({MAX_HALF_DIVISOR{load_base}} & base_countdown) |
                ({MAX_HALF_DIVISOR{load_plus_one}} & plus_one_countdown);
    end

    always @(posedge half_clk or negedge reset_b) begin
        if (!reset_b)
            accumulator <= {HALF_FRAC_WIDTH{1'b0}};
        else if (countdown[0])
            accumulator <= accumulator_sum[HALF_FRAC_WIDTH-1:0];
    end

    // Prepare both reload selects on the lookahead edge. The actual reload
    // then has only a registered select and static ratio mask, not a live
    // terminal-to-fractional-carry-to-bank cascade.
    always @(posedge half_clk or negedge reset_b) begin
        if (!reset_b) begin
            reload_base_pending <= 1'b0;
            reload_plus_pending <= 1'b0;
        end else begin
            reload_base_pending <= countdown[1] && !use_plus_one;
            reload_plus_pending <= countdown[1] && use_plus_one;
        end
    end

    always @(posedge half_clk or negedge reset_b) begin
        if (!reset_b) begin
            interval_active <= 1'b0;
            feedback_clk <= 1'b0;
        end else begin
            interval_active <= 1'b1;
            feedback_clk <= countdown[0];
        end
    end
endmodule
