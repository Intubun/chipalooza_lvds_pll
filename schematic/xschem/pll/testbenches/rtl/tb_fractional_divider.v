`timescale 1ns/1ps

module tb_fractional_divider;
    reg vco_clk = 1'b0;
    reg reset_n = 1'b0;
    reg enable = 1'b0;
    reg [6:0] integer_div = 7'd4;
    reg [15:0] fractional_num = 16'd0;
    wire feedback_clk;

    fractional_divider dut (
        .vco_clk(vco_clk),
        .reset_n(reset_n),
        .enable(enable),
        .integer_div(integer_div),
        .fractional_num(fractional_num),
        .feedback_clk(feedback_clk)
    );

    always #0.25 vco_clk = ~vco_clk;

    task run_case;
        input [6:0] n;
        input [15:0] frac;
        input integer pulses_required;
        integer cycles;
        integer previous_cycle;
        integer pulses;
        integer interval;
        integer minimum_interval;
        integer maximum_interval;
        integer interval_sum;
        real measured_ratio;
        real expected_ratio;
        begin
            enable = 1'b0;
            reset_n = 1'b0;
            integer_div = n;
            fractional_num = frac;
            repeat (4) @(posedge vco_clk);
            reset_n = 1'b1;
            enable = 1'b1;

            cycles = 0;
            previous_cycle = 0;
            pulses = 0;
            minimum_interval = 1000000;
            maximum_interval = 0;
            interval_sum = 0;
            while (pulses < pulses_required + 1) begin
                @(posedge vco_clk);
                #0.001;
                cycles = cycles + 1;
                if (feedback_clk) begin
                    if (pulses != 0) begin
                        interval = cycles - previous_cycle;
                        interval_sum = interval_sum + interval;
                        if (interval < minimum_interval)
                            minimum_interval = interval;
                        if (interval > maximum_interval)
                            maximum_interval = interval;
                    end
                    previous_cycle = cycles;
                    pulses = pulses + 1;
                end
            end

            measured_ratio = interval_sum * 1.0 / pulses_required;
            expected_ratio = n + frac / 65536.0;
            if ((measured_ratio - expected_ratio > 0.002) ||
                (expected_ratio - measured_ratio > 0.002) ||
                (minimum_interval < n) || (maximum_interval > n + 1)) begin
                $display("FAIL N=%0d frac=%0d measured=%0.6f expected=%0.6f min=%0d max=%0d",
                         n, frac, measured_ratio, expected_ratio,
                         minimum_interval, maximum_interval);
                $fatal(1);
            end
            $display("PASS N=%0d frac=%0d ratio=%0.6f min=%0d max=%0d",
                     n, frac, measured_ratio, minimum_interval, maximum_interval);
        end
    endtask

    initial begin
        run_case(7'd4, 16'd0, 128);
        run_case(7'd7, 16'd32768, 256);
        run_case(7'd39, 16'd16384, 256);
        run_case(7'd79, 16'd49152, 256);
        $display("ALL FRACTIONAL DIVIDER TESTS PASSED");
        $finish;
    end
endmodule
