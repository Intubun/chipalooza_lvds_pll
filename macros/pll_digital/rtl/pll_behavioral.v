`timescale 1ns/1ps

// Simulation-only real-number model of the complete PLL. The digital PFD and
// dividers are the implementation RTL; the characterized charge pump, filter,
// and VCO are represented by real-valued state for fast full-chip simulation.
module pll_behavioral (
    input  wire        ref_clk,
    input  wire        reset_n,
    input  wire        enable,
    input  wire [6:0]  div_integer,
    input  wire [15:0] div_fractional,
    input  wire [1:0]  test_div_select,
    output wire        pll_clk,
    output wire        test_clk
);
    wire feedback_clk;
    wire up;
    wire down;
    reg vco_clk = 1'b0;

    real vctrl = 0.55;
    real filter_zero = 0.55;
    real vco_frequency_hz;
    real vco_half_period_ns;
    real pump_current;

    localparam real TIME_STEP_NS = 0.05;
    localparam real R1_OHM = 32.8e3;
    localparam real C1_F = 9.75e-12;
    localparam real C2_F = 0.975e-12;
    localparam real ICP_A = 2.84e-6;

    pll_digital digital_i (
        .ref_clk(ref_clk),
        .vco_clk(vco_clk),
        .reset_n(reset_n),
        .enable(enable),
        .div_integer(div_integer),
        .div_fractional(div_fractional),
        .test_div_select(test_div_select),
        .feedback_clk(feedback_clk),
        .pll_clk(pll_clk),
        .test_clk(test_clk),
        .up(up),
        .down(down)
    );

    // Nominal fit around the characterized 1-2 GHz VCO operating region.
    // The floor allows acquisition to begin below the fitted range.
    always begin
        vco_frequency_hz = 0.1e9 + 10.49e9 * (vctrl - 0.497);
        if (vco_frequency_hz < 0.1e9)
            vco_frequency_hz = 0.1e9;
        if (vco_frequency_hz > 6.3e9)
            vco_frequency_hz = 6.3e9;
        vco_half_period_ns = 0.5e9 / vco_frequency_hz;
        #(vco_half_period_ns) vco_clk = ~vco_clk;
    end

    // Forward-Euler model of (R1-C1) || C2. TIME_STEP_NS is much smaller
    // than R1*C2 and resolves loop updates without SPICE-sized run times.
    always begin
        #(TIME_STEP_NS);
        if (!reset_n || !enable) begin
            vctrl = 0.55;
            filter_zero = 0.55;
        end else begin
            if (up && !down)
                pump_current = ICP_A;
            else if (down && !up)
                pump_current = -ICP_A;
            else
                pump_current = 0.0;
            vctrl = vctrl + (TIME_STEP_NS * 1e-9 / C2_F) *
                    (pump_current - (vctrl - filter_zero) / R1_OHM);
            filter_zero = filter_zero + (TIME_STEP_NS * 1e-9 / (R1_OHM * C1_F)) *
                          (vctrl - filter_zero);
            if (vctrl < 0.0)
                vctrl = 0.0;
            if (vctrl > 1.2)
                vctrl = 1.2;
        end
    end
endmodule
