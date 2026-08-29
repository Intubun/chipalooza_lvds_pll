`timescale 1ns/1ps

module tb_clock_output_divider;
    reg vco_clk = 1'b0;
    reg reset_n = 1'b0;
    reg enable = 1'b0;
    reg [1:0] test_div_sel = 2'b00;
    wire pll_clk;
    wire test_clk;
    integer vco_edges = 0;
    integer last_pll_edge = 0;
    integer last_test_edge = 0;
    integer pll_interval;
    integer test_interval;

    clock_output_divider dut (
        .vco_clk(vco_clk),
        .reset_n(reset_n),
        .enable(enable),
        .test_div_sel(test_div_sel),
        .pll_clk(pll_clk),
        .test_clk(test_clk)
    );

    always #0.25 vco_clk = ~vco_clk;
    always @(posedge vco_clk) vco_edges = vco_edges + 1;

    task check_select;
        input [1:0] select;
        input integer expected_divide;
        begin
            enable = 1'b0;
            reset_n = 1'b0;
            test_div_sel = select;
            repeat (3) @(posedge vco_clk);
            reset_n = 1'b1;
            enable = 1'b1;
            @(posedge test_clk);
            last_test_edge = vco_edges;
            @(posedge test_clk);
            test_interval = vco_edges - last_test_edge;
            if (test_interval != expected_divide) begin
                $display("FAIL select=%0d interval=%0d expected=%0d",
                         select, test_interval, expected_divide);
                $fatal(1);
            end
            $display("PASS test divider select=%0d divide=%0d", select, test_interval);
        end
    endtask

    initial begin
        enable = 1'b0;
        reset_n = 1'b0;
        repeat (3) @(posedge vco_clk);
        reset_n = 1'b1;
        enable = 1'b1;
        @(posedge pll_clk);
        last_pll_edge = vco_edges;
        @(posedge pll_clk);
        pll_interval = vco_edges - last_pll_edge;
        if (pll_interval != 2)
            $fatal(1, "pll_clk divide was %0d, expected 2", pll_interval);

        check_select(2'b00, 2);
        check_select(2'b01, 4);
        check_select(2'b10, 8);
        check_select(2'b11, 16);
        $display("ALL OUTPUT DIVIDER TESTS PASSED");
        $finish;
    end
endmodule
