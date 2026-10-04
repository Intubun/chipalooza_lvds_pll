notes for analog pll from design review of layout:-
add guard ring fix pwr gnd routing (arent routed as pwr gnd just as regular rails need to be more robust)
n well guard ring vs p well guard ring (for noise isolation, since this pdk doesnt have deep n p well as that costs extra)
pwell surrounded by nwell good guarding / noise isolation for charge pump
make sure charge pump noise isolated, and ensure good esd protection for the entire design
