# The VCO reaches 2 GHz because the SerDes PLL output is VCO/2.
create_clock -name ref_clk -period 4.0 [get_ports ref_clk]
create_clock -name vco_clk -period 0.5 [get_ports vco_clk]

# The fixed TSPC /2 drives only the explicit half-rate buffer. Transistor-level
# PEX verifies that macro at the full VCO rate; the characterized buffer output
# is the physical 1 GHz clock root for all CMOS programmable-divider logic.
set half_clk_pin [get_pins -hierarchical *half_clk_buffer/X]
create_clock -name half_clk -period 1.0 $half_clk_pin

# The minimum legal feedback divisor is four. Fractional settings only make
# this output slower. Its rising edges are data-dependent, so model the fastest
# legal 500 MHz rate directly at the feedback-side PFD clock pin.
create_clock -name feedback_clk_int -period 2.0 \
    [get_pins -hierarchical pfd_i._08_/CLK]

create_generated_clock -name test_div4_int -source $half_clk_pin -divide_by 2 \
    [get_pins -hierarchical *div4_ff/Q]
create_generated_clock -name test_div8_int -source [get_pins -hierarchical *div4_ff/Q] -divide_by 2 \
    [get_pins -hierarchical *div8_ff/Q]
create_generated_clock -name test_div16_int -source [get_pins -hierarchical *div8_ff/Q] -divide_by 2 \
    [get_pins -hierarchical *div16_ff/Q]

set_clock_groups -asynchronous \
    -group [get_clocks ref_clk] \
    -group [get_clocks {vco_clk half_clk feedback_clk_int test_div4_int test_div8_int test_div16_int}]

# Configuration is required to remain static while enable is asserted. Reset
# and enable drive reset/control arcs rather than synchronous data interfaces.
set_false_path -from [get_ports {reset_n enable div_ratio* test_div_select*}]

# The fractional accumulator updates once per complete divide interval. The
# minimum interval is two half-clock cycles (integer divisor >= 4), so its
# result has two cycles to reach the next accumulator state and interval reload.
set accumulator_nets [get_nets -hierarchical *feedback_divider_i.accumulator*]
set accumulator_regs [get_cells -of_objects \
    [get_pins -of_objects $accumulator_nets -filter "direction == output"]]
set interval_nets [get_nets -hierarchical \
    {*feedback_divider_i.countdown*}]
set interval_regs [get_cells -of_objects \
    [get_pins -of_objects $interval_nets -filter "direction == output"]]
set interval_active_nets [get_nets -hierarchical \
    {*feedback_divider_i.interval_active*}]
set interval_active_regs [get_cells -of_objects \
    [get_pins -of_objects $interval_active_nets -filter "direction == output"]]
# interval_active is a one-time initialization select. Its 0->1 transition
# occurs only after the initial countdown has been captured and cannot affect
# any subsequent countdown state.
set_false_path -from $interval_active_regs -to $interval_regs
set_multicycle_path -setup 2 -from $accumulator_regs -to $accumulator_regs
set_multicycle_path -hold 1 -from $accumulator_regs -to $accumulator_regs
set_multicycle_path -setup 2 -from $accumulator_regs -to $interval_regs
set_multicycle_path -hold 1 -from $accumulator_regs -to $interval_regs

set_max_fanout $::env(MAX_FANOUT_CONSTRAINT) [current_design]
