# The VCO reaches 2 GHz because the SerDes PLL output is VCO/2.
create_clock -name ref_clk -period 4.0 [get_ports ref_clk]
create_clock -name vco_clk -period 0.5 [get_ports vco_clk]

# The /2-/3 prescaler is constrained at its fastest (/2) mode. The program
# counter and accumulator are clocked by this node instead of by the 2 GHz VCO.
set prescaler_q2_nets [get_nets -hierarchical *feedback_divider_i.prescaler_q2*]
set prescaler_q2_pin [get_pins -of_objects $prescaler_q2_nets \
    -filter "direction == output"]
create_generated_clock -name prescaler_clk -source [get_ports vco_clk] \
    -divide_by 2 $prescaler_q2_pin

create_generated_clock -name feedback_clk_int -source $prescaler_q2_pin \
    -divide_by 2 [get_ports feedback_clk]

create_generated_clock -name pll_clk_int -source [get_ports vco_clk] -divide_by 2 \
    [get_pins -hierarchical *div2_ff/Q]
create_generated_clock -name test_div4_int -source [get_pins -hierarchical *div2_ff/Q] -divide_by 2 \
    [get_pins -hierarchical *div4_ff/Q]
create_generated_clock -name test_div8_int -source [get_pins -hierarchical *div4_ff/Q] -divide_by 2 \
    [get_pins -hierarchical *div8_ff/Q]
create_generated_clock -name test_div16_int -source [get_pins -hierarchical *div8_ff/Q] -divide_by 2 \
    [get_pins -hierarchical *div16_ff/Q]

set_clock_groups -asynchronous \
    -group [get_clocks ref_clk] \
    -group [get_clocks {vco_clk prescaler_clk feedback_clk_int pll_clk_int test_div4_int test_div8_int test_div16_int}]

# Configuration is required to remain static while enable is asserted. Reset
# and enable drive reset/control arcs rather than synchronous data interfaces.
set_false_path -from [get_ports {reset_n enable div_ratio* test_div_select*}]

# The fractional accumulator updates once per complete divide interval. The
# minimum program count is two prescaler cycles (integer divisor >= 4), so its
# result has two prescaler-clock cycles to reach the next accumulator state,
# program-counter reload, and prescaler modulus selection.
set accumulator_nets [get_nets -hierarchical *feedback_divider_i.accumulator*]
set accumulator_regs [get_cells -of_objects \
    [get_pins -of_objects $accumulator_nets -filter "direction == output"]]
set interval_nets [get_nets -hierarchical \
    {*feedback_divider_i.pulse_phase* *feedback_divider_i.pulse_remainder* \
     *feedback_divider_i.group_counter* *feedback_divider_i.modulus_2* \
     *feedback_divider_i.terminal_pending*}]
set interval_regs [get_cells -of_objects \
    [get_pins -of_objects $interval_nets -filter "direction == output"]]
set_multicycle_path -setup 2 -from $accumulator_regs -to $accumulator_regs
set_multicycle_path -hold 1 -from $accumulator_regs -to $accumulator_regs
set_multicycle_path -setup 2 -from $accumulator_regs -to $interval_regs
set_multicycle_path -hold 1 -from $accumulator_regs -to $interval_regs

set_max_fanout $::env(MAX_FANOUT_CONSTRAINT) [current_design]
