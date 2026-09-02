
# CACE Summary for lvds_tx

**netlist source**: schematic

|      Parameter       |         Tool         |     Result      | Min Limit  |  Min Value   | Typ Target |  Typ Value   | Max Limit  |  Max Value   |  Status  |
| :------------------- | :------------------- | :-------------- | ---------: | -----------: | ---------: | -----------: | ---------: | -----------: | :------: |
| Differential output  | ngspice              | vod                  |         0.247 V |    0.349 V |          any |    0.379 V |      0.454 V |    0.402 V |   Pass ✅    |
| Offset voltage       | ngspice              | vos                  |         1.125 V |    1.191 V |          any |    1.194 V |      1.375 V |    1.195 V |   Pass ✅    |
| Offset, peak-to-peak | ngspice              | vos_pp               |               ​ |          ​ |          any |    0.086 V |       0.15 V |    0.123 V |   Pass ✅    |
| Supply current       | ngspice              | i_supply             |               ​ |          ​ |          any |    0.006 A |          any |    0.007 A |   Pass ✅    |


## Plots

## vod_vs_temp

![vod_vs_temp](./lvds_tx/schematic/vod_vs_temp.png)

## vos_vs_temp

![vos_vs_temp](./lvds_tx/schematic/vos_vs_temp.png)

## vos_pp_vs_corner

![vos_pp_vs_corner](./lvds_tx/schematic/vos_pp_vs_corner.png)

## vod_vs_vdd

![vod_vs_vdd](./lvds_tx/schematic/vod_vs_vdd.png)
