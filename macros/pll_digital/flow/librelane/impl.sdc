# The VCO reaches 2 GHz because the SerDes PLL output is VCO/2.
create_clock -name ref_clk -period 4.0 [get_ports ref_clk]
create_clock -name vco_clk -period 0.5 [get_ports vco_clk]
set_clock_groups -asynchronous -group [get_clocks ref_clk] -group [get_clocks vco_clk]

set non_clock_inputs [remove_from_collection [all_inputs] [get_ports {ref_clk vco_clk}]]
set_input_delay 0.1 -clock [get_clocks ref_clk] $non_clock_inputs
set_output_delay 0.1 -clock [get_clocks vco_clk] [all_outputs]
set_max_fanout $::env(MAX_FANOUT_CONSTRAINT) [current_design]
