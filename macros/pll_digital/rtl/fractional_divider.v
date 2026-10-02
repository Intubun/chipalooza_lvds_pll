`timescale 1ns/1ps

// Portable behavioral model of the high-speed dual-modulus prescaler. The
// technology mapping replaces this module with the IHP TSPC macro; keeping the
// circuit boundary generic leaves the divider RTL portable to other PDKs.
//
// modulus_request is prepared one prescaler cycle early. It is sampled on the
// rising edge of q2 so that the selected modulus takes effect immediately
// after that interval boundary without placing a standard-cell clock-to-Q path
// between q2 and the next VCO edge.
module dual_modulus_prescaler (
    input  wire vco_clk,
    input  wire reset_b,
    input  wire modulus_request,
    output reg  q2
);
    reg q1;
    reg modulus_2;

    always @(posedge vco_clk or negedge reset_b) begin
        if (!reset_b) begin
            q1 <= 1'b0;
            q2 <= 1'b0;
        end else begin
            q1 <= q2;
            q2 <= ~(q2 | (q1 & ~modulus_2));
        end
    end

    always @(posedge q2 or negedge reset_b) begin
        if (!reset_b)
            modulus_2 <= 1'b1;
        else
            modulus_2 <= modulus_request;
    end
endmodule

// Programmable N/N+1 feedback divider with a dual-modulus /2-/3 prescaler.
//
// Only the two prescaler state bits run at the full VCO rate. The program
// counter and fractional accumulator are clocked by the prescaler output, at
// no more than half the VCO frequency. For a requested integer modulus M:
//
//     M = 2 * floor(M / 2) + (M mod 2)
//
// The prescaler therefore runs in /3 mode for its first cycle when M is odd,
// then in /2 mode for the remaining program-counter cycles. The fractional
// accumulator chooses M or M+1 for each complete division interval, giving:
//
//     integer_div + fractional_num / 2^FRAC_WIDTH
//
// Set fractional_num to zero for integer-N operation. integer_div must be >= 4
// for the PLL operating range.
module fractional_divider #(
    parameter integer DIV_WIDTH = 7,
    parameter integer FRAC_WIDTH = 3
) (
    input  wire                  vco_clk,
    input  wire                  reset_n,
    input  wire                  enable,
    input  wire [DIV_WIDTH-1:0]  integer_div,
    input  wire [FRAC_WIDTH-1:0] fractional_num,
    output reg                   feedback_clk
);
    localparam integer PROGRAM_WIDTH = DIV_WIDTH - 1;
    localparam integer GROUP_WIDTH = PROGRAM_WIDTH - 2;

    wire prescaler_q2;
    reg modulus_request;
    reg modulus_armed;
    reg interval_active;
    reg terminal_pending;
    reg [3:0] pulse_phase;
    reg [1:0] pulse_remainder;
    reg [GROUP_WIDTH-1:0] group_counter;
    reg [FRAC_WIDTH-1:0] accumulator;

    wire reset_b = reset_n && enable;
    wire [FRAC_WIDTH:0] accumulator_sum =
        {1'b0, accumulator} + {1'b0, fractional_num};
    wire [DIV_WIDTH-1:0] next_divisor =
        integer_div + {{(DIV_WIDTH-1){1'b0}},
                       accumulator_sum[FRAC_WIDTH]};
    wire group_nonzero = |group_counter;
    wire group_is_one = group_counter == {{(GROUP_WIDTH-1){1'b0}}, 1'b1};
    // Assert one prescaler edge before terminal count. This keeps the terminal
    // edge itself to a registered select plus small reload muxes rather than a
    // wide decode feeding every interval register.
    wire one_pulse_after_current =
        (group_is_one &&
         ((pulse_remainder == 2'b00 && pulse_phase[2]) ||
          (pulse_remainder == 2'b01 && pulse_phase[3]))) ||
        (!group_nonzero &&
         ((pulse_remainder == 2'b10 && pulse_phase[0]) ||
          (pulse_remainder == 2'b11 && pulse_phase[1])));

    dual_modulus_prescaler prescaler_i (
        .vco_clk(vco_clk),
        .reset_b(reset_b),
        .modulus_request(modulus_request),
        .q2(prescaler_q2)
    );

    always @(posedge prescaler_q2 or negedge reset_b) begin
        if (!reset_b) begin
            pulse_phase      <= 4'b0000;
            pulse_remainder  <= 2'b00;
            group_counter    <= {GROUP_WIDTH{1'b0}};
            accumulator     <= {FRAC_WIDTH{1'b0}};
            modulus_request <= 1'b1;
            modulus_armed   <= 1'b0;
            interval_active <= 1'b0;
            terminal_pending <= 1'b0;
            feedback_clk    <= 1'b0;
        end else if (!modulus_armed) begin
            // The custom prescaler samples this request at the next q2 edge.
            // No externally visible interval starts until that has happened.
            modulus_request <= ~integer_div[0];
            modulus_armed   <= 1'b1;
            interval_active <= 1'b0;
            terminal_pending <= 1'b0;
            feedback_clk    <= 1'b0;
        end else if (!interval_active) begin
            // The requested first modulus is now active. Load configuration
            // and begin the first externally visible division interval.
            pulse_phase      <= 4'b0001;
            pulse_remainder  <= integer_div[2:1];
            group_counter    <= integer_div[DIV_WIDTH-1:3];
            modulus_request <= 1'b1;
            modulus_armed   <= 1'b1;
            interval_active <= 1'b1;
            terminal_pending <= 1'b0;
            feedback_clk    <= 1'b0;
        end else if (terminal_pending) begin
            pulse_phase      <= 4'b0001;
            pulse_remainder  <= next_divisor[2:1];
            group_counter    <= next_divisor[DIV_WIDTH-1:3];
            accumulator     <= accumulator_sum[FRAC_WIDTH-1:0];
            modulus_request <= 1'b1;
            modulus_armed   <= 1'b1;
            interval_active <= 1'b1;
            terminal_pending <= 1'b0;
            feedback_clk    <= 1'b1;
        end else begin
            pulse_phase <= {pulse_phase[2:0], pulse_phase[3]};
            if (group_nonzero && pulse_phase[3])
                group_counter <= group_counter - 1'b1;
            modulus_request <= one_pulse_after_current ?
                               ~next_divisor[0] : 1'b1;
            modulus_armed   <= 1'b1;
            interval_active <= 1'b1;
            terminal_pending <= one_pulse_after_current;
            feedback_clk    <= 1'b0;
        end
    end
endmodule
