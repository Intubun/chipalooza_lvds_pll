`timescale 1ns/1ps

// Fast reusable-model test for integer and fractional lock.
module tb_pll_behavioral;
    parameter [9:0] DIV_RATIO = {7'd19, 3'd4};
    parameter real REF_PERIOD_NS = 10.0;

    reg ref_clk = 1'b0;
    reg reset_n = 1'b0;
    reg enable = 1'b0;
    wire pll_clk;
    wire test_clk;

    real previous_pll_edge = 0.0;
    real period_ns;
    real period_sum = 0.0;
    real period_square_sum = 0.0;
    real period_min = 1.0e9;
    real period_max = 0.0;
    real mean_period;
    real rms_jitter;
    real expected_frequency;
    integer settled_periods = 0;

    pll_behavioral dut (
        .ref_clk(ref_clk),
        .reset_n(reset_n),
        .enable(enable),
        .div_ratio(DIV_RATIO),
        .test_div_select(2'b01),
        .pll_clk(pll_clk),
        .test_clk(test_clk)
    );

    always #(REF_PERIOD_NS / 2.0) ref_clk = ~ref_clk;

    always @(posedge pll_clk) begin
        if ($realtime > 8000.0) begin
            if (previous_pll_edge != 0.0) begin
                period_ns = $realtime - previous_pll_edge;
                period_sum = period_sum + period_ns;
                period_square_sum = period_square_sum + period_ns * period_ns;
                if (period_ns < period_min)
                    period_min = period_ns;
                if (period_ns > period_max)
                    period_max = period_ns;
                settled_periods = settled_periods + 1;
            end
            previous_pll_edge = $realtime;
        end
    end

    initial begin
        #2.0;
        reset_n = 1'b1;
        enable = 1'b1;
        #9998.0;
        mean_period = period_sum / settled_periods;
        rms_jitter = $sqrt(period_square_sum / settled_periods -
                           mean_period * mean_period);
        expected_frequency = (1e9 / REF_PERIOD_NS) *
                             (DIV_RATIO / 8.0) / 2.0;
        $display("PLL_BEHAVIORAL_RESULT expected_hz=%0.3f measured_hz=%0.3f vctrl=%0.6f rms_jitter_ps=%0.3f pp_jitter_ps=%0.3f periods=%0d",
                 expected_frequency, 1e9 / mean_period, dut.vctrl,
                 rms_jitter * 1e3, (period_max - period_min) * 1e3,
                 settled_periods);
        if ((1e9 / mean_period - expected_frequency > expected_frequency * 0.001) ||
            (expected_frequency - 1e9 / mean_period > expected_frequency * 0.001))
            $fatal(1, "behavioral PLL frequency did not settle within 0.1 percent");
        $finish;
    end
endmodule
