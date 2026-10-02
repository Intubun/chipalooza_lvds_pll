
# CACE Summary for lvds_tx

**netlist source**: schematic

|      Parameter       |         Tool         |     Result      | Min Limit  |  Min Value   | Typ Target |  Typ Value   | Max Limit  |  Max Value   |  Status  |
| :------------------- | :------------------- | :-------------- | ---------: | -----------: | ---------: | -----------: | ---------: | -----------: | :------: |
| Differential output  | ngspice              | vod                  |         0.247 V |    0.353 V |          any |    0.376 V |      0.454 V |    0.402 V |   Pass ✅    |
| Offset voltage       | ngspice              | vos                  |         1.125 V |    1.191 V |          any |    1.194 V |      1.375 V |    1.195 V |   Pass ✅    |
| Offset, peak-to-peak | ngspice              | vos_pp               |               ​ |          ​ |          any |    0.046 V |       0.15 V |    0.107 V |   Pass ✅    |
| Output rise time     | ngspice              | t_rise               |               ​ |          ​ |          any |  52.552 ps |       300 ps |  70.756 ps |   Pass ✅    |
| Output fall time     | ngspice              | t_fall               |               ​ |          ​ |          any |  52.552 ps |       300 ps |  70.756 ps |   Pass ✅    |
| Pulse skew           | ngspice              | t_skew               |               ​ |          ​ |          any |   0.000 ps |       100 ps |   0.000 ps |   Pass ✅    |
| Output duty cycle    | ngspice              | duty                 |            45 % |   50.000 % |         50 % |   50.000 % |         55 % |   50.000 % |   Pass ✅    |
| Supply current       | ngspice              | i_supply             |               ​ |          ​ |          any |   5.989 mA |          any |   6.696 mA |   Pass ✅    |


## Plots

## vod_vs_temp

![vod_vs_temp](./lvds_tx/schematic/vod_vs_temp.png)

## vos_vs_temp

![vos_vs_temp](./lvds_tx/schematic/vos_vs_temp.png)

## vos_pp_vs_corner

![vos_pp_vs_corner](./lvds_tx/schematic/vos_pp_vs_corner.png)

## vod_vs_vdd

![vod_vs_vdd](./lvds_tx/schematic/vod_vs_vdd.png)
