// IHP SG13CMOS5L technology map for the portable async_toggle_ff module.
// sg13cmos5l_dfrbp_2 exposes Q_N, allowing the toggle feedback to avoid a
// separate inverter. RTL simulation and other PDKs continue to use the
// behavioral implementation in clock_output_divider.v.
(* techmap_celltype = "async_toggle_ff" *)
module ihp_async_toggle_ff_map (
    input  wire clk,
    input  wire reset_b,
    output wire q
);
    wire q_n;

    sg13cmos5l_dfrbp_2 _TECHMAP_REPLACE_ (
        .Q(q),
        .Q_N(q_n),
        .CLK(clk),
        .D(q_n),
        .RESET_B(reset_b)
    );
endmodule

(* techmap_celltype = "high_speed_div2" *)
module ihp_high_speed_div2_map (
    input  wire clk,
    input  wire reset_b,
    output wire q
);
    pll_tspc_div2 _TECHMAP_REPLACE_ (
        .CLK(clk),
        .RESET_B(reset_b),
        .Q(q)
    );
endmodule

(* techmap_celltype = "half_rate_clock_buffer" *)
module ihp_half_rate_clock_buffer_map (
    input  wire a,
    output wire y
);
    sg13cmos5l_buf_16 _TECHMAP_REPLACE_ (
        .A(a),
        .X(y)
    );
endmodule
