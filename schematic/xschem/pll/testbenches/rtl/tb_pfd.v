`timescale 1ns/1ps

module tb_pfd;
    reg reset_n = 1'b0;
    reg ref_early = 1'b0;
    reg fb_late = 1'b0;
    reg ref_late = 1'b0;
    reg fb_early = 1'b0;
    wire up_lead;
    wire down_lead;
    wire up_lag;
    wire down_lag;
    real up_start;
    real down_start;
    real up_width;
    real down_width;

    pll_pfd up_case (
        .ref_clk(ref_early),
        .feedback_clk(fb_late),
        .reset_n(reset_n),
        .up(up_lead),
        .down(down_lead)
    );

    pll_pfd down_case (
        .ref_clk(ref_late),
        .feedback_clk(fb_early),
        .reset_n(reset_n),
        .up(up_lag),
        .down(down_lag)
    );

    always #5 ref_early = ~ref_early;
    initial begin
        #2;
        forever #5 fb_late = ~fb_late;
    end
    always #5 fb_early = ~fb_early;
    initial begin
        #2;
        forever #5 ref_late = ~ref_late;
    end

    always @(posedge up_lead)
        up_start = $realtime;
    always @(negedge up_lead)
        if (reset_n && up_start > 0.0)
            up_width = $realtime - up_start;
    always @(posedge down_lag)
        down_start = $realtime;
    always @(negedge down_lag)
        if (reset_n && down_start > 0.0)
            down_width = $realtime - down_start;

    initial begin
        #1;
        reset_n = 1'b1;
        #45;
        if (up_width != 2.0 || down_width != 2.0)
            $fatal(1, "PFD widths were UP=%0.3f ns DOWN=%0.3f ns", up_width, down_width);
        $display("PFD RTL PASS up_width_ns=%0.3f down_width_ns=%0.3f", up_width, down_width);
        $finish;
    end
endmodule
