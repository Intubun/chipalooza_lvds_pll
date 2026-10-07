module slot_14 (
`ifdef USE_POWER_PINS
    inout vdd_3v3,
    inout vdd_1v2,
    inout vss_3v3,
    inout vss_1v2,
`endif
    input enable,
    input clk,
    input reset,
    input [23:0] dig_in,
    input ibias0,
    input ibias1,
    input vbias,
    output [11:0] dig_out,
    inout [2:0] s14_an,
    inout s14_an_2_esd,
    inout s14_an_1_esd,
    inout s14_an_0_esd,
    inout analog_bus0,
    inout analog_bus1,
    inout analog_bus2,
    inout analog_bus3
);
endmodule
