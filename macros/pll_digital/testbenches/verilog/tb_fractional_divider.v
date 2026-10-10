`timescale 1ns/1ps

module tb_fractional_divider;
    reg half_clk = 1'b0;
    reg reset_n = 1'b0;
    reg enable = 1'b0;
    reg [6:0] integer_div = 7'd4;
    reg [2:0] fractional_num = 3'd0;
    wire feedback_clk;

    fractional_divider dut (
        .half_clk(half_clk),
        .reset_n(reset_n),
        .enable(enable),
        .integer_div(integer_div),
        .fractional_num(fractional_num),
        .feedback_clk(feedback_clk)
    );

    always #0.5 half_clk = ~half_clk;

    task run_case;
        input [6:0] n;
        input [2:0] frac;
        input integer pulses_required;
        integer cycles;
        integer previous_cycle;
        integer pulses;
        integer interval;
        integer minimum_half_interval;
        integer maximum_half_interval;
        integer half_interval_sum;
        integer ratio_code;
        integer expected_minimum;
        integer expected_maximum;
        reg previous_feedback;
        real measured_ratio;
        real expected_ratio;
        begin
            $display("TEST N=%0d frac=%0d", n, frac);
            enable = 1'b1;
            reset_n = 1'b1;
            integer_div = n;
            fractional_num = frac;
            #0.001;
            reset_n = 1'b0;
            repeat (4) @(posedge half_clk);
            reset_n = 1'b1;
            enable = 1'b1;

            cycles = 0;
            previous_cycle = 0;
            pulses = 0;
            minimum_half_interval = 1000000;
            maximum_half_interval = 0;
            half_interval_sum = 0;
            previous_feedback = 1'b0;
            while (pulses < pulses_required + 1) begin
                @(posedge half_clk);
                #0.001;
                cycles = cycles + 1;
                if (feedback_clk && !previous_feedback) begin
                    if (pulses != 0) begin
                        interval = cycles - previous_cycle;
                        half_interval_sum = half_interval_sum + interval;
                        if (interval < minimum_half_interval)
                            minimum_half_interval = interval;
                        if (interval > maximum_half_interval)
                            maximum_half_interval = interval;
                    end
                    previous_cycle = cycles;
                    pulses = pulses + 1;
                end
                previous_feedback = feedback_clk;
                if (cycles > pulses_required * (n + 2)) begin
                    $display("FAIL N=%0d frac=%0d divider stopped after %0d pulses (countdown=%h)",
                             n, frac, pulses, dut.countdown);
                    $fatal(1);
                end
            end

            measured_ratio = 2.0 * half_interval_sum / pulses_required;
            expected_ratio = n + frac / 8.0;
            ratio_code = n * 8 + frac;
            expected_minimum = 2 * (ratio_code / 16);
            expected_maximum = expected_minimum +
                               ((ratio_code % 16) != 0 ? 2 : 0);
            if ((measured_ratio - expected_ratio > 0.002) ||
                (expected_ratio - measured_ratio > 0.002) ||
                (2 * minimum_half_interval != expected_minimum) ||
                (2 * maximum_half_interval != expected_maximum)) begin
                $display("FAIL N=%0d frac=%0d measured=%0.6f expected=%0.6f min=%0d max=%0d",
                         n, frac, measured_ratio, expected_ratio,
                         2 * minimum_half_interval,
                         2 * maximum_half_interval);
                $fatal(1);
            end
            $display("PASS N=%0d frac=%0d ratio=%0.6f min=%0d max=%0d",
                     n, frac, measured_ratio, 2 * minimum_half_interval,
                     2 * maximum_half_interval);
        end
    endtask

    integer n;
    integer frac;
    initial begin
        for (n = 4; n <= 127; n = n + 1)
            for (frac = 0; frac < 8; frac = frac + 1)
                run_case(n[6:0], frac[2:0], 16);
        $display("ALL FRACTIONAL DIVIDER TESTS PASSED");
        $finish;
    end
endmodule
