# `iref_x15` — 1:15 bias pre-mirror

Turns the 2 uA a harness `ibias` pin delivers into the 30 uA the LVDS
transmitter's pre-driver and driver were characterised at. The harness
current DACs stop at 10 uA, so the 30 uA cannot come off a pin directly.

It used to sit inside `lvds_tx` (as `Xm_pd` / `Xm_drv`). It is its own macro
now and sits at the top level, one instance per bias pin:

```
ibias[0] --> xiref_pd  (iref_x15) --iref_pd_30u -->  xlvds.Iref_pd   (pre-driver, Mref)
ibias[1] --> xiref_drv (iref_x15) --iref_drv_30u --> xlvds.Iref_drv  (driver, M9)
```

## Circuit — `schematic/xschem/iref_x15.sch`

| Device | Size | Role |
|---|---|---|
| `Mn1` | hv nmos `w=3.2u l=2u ng=1` | input diode, takes `IREF_IN` |
| `Mn2` | hv nmos `w=48u l=2u ng=6` | 15:1 copy of `Mn1` into `CASC` |
| `Mp1` | hv pmos `w=48u l=2u ng=6` | diode on `CASC` |
| `Mp2` | hv pmos `w=48u l=2u ng=6` | copy of `Mp1`, sources `IREF_OUT` |

Pins: `IREF_IN` (in, 2 uA pushed in), `IREF_OUT` (out, sources ~30 uA into a
diode-connected nmos), `Va` (3.3 V), `Vss`.

`Mn2` is written `w=48u ng=6`, six fingers of 8 µm — the finger geometry
`Mp1`/`Mp2` already had. Total width, length and the 15:1 ratio against `Mn1`
are the original ones; it packs better next to the pmos (1594 → 1101 µm² of
cell at the time).

## Testbench — `testbenches/xschem/iref_x15_tb_tran.sch`

2 uA into `IREF_IN`, `IREF_OUT` into `Vload`, an ammeter held at 0.8 V (about
where `Mref` / `M9` sit), plus a dc sweep of `Vload` over 0–3.3 V for the output
characteristic. `make sim-all`. At tt, 27 °C:

| | |
|---|---|
| output current at 0.8 V | 32.3 uA (1 : 16.1, not 15 — `Mn1` sits at Vds = Vgs, `Mn2` at `CASC`) |
| within 2 % of that up to | 3.03 V at the output |

So the transmitter has always run at ~32 uA in the chip, not at the 30 uA its
own benches use.

## Layout — `layout/iref_x15.gds`

**Routed by hand** (in `macros/lvds_tx/layout/lvds_tx.gds`, before this block
moved out) and copied from there unchanged: the cell and its three leaf cells,
identical layer by layer. Its cell origin is not at its lower-left corner — the
geometry spans (1.92, 21.605) to (29.54, 42.035) µm, 27.6 × 20.4 µm.

* KLayout DRC (`make klayout-drc`, macro level): **clean**.
* KLayout LVS (`make klayout-lvs`): the extracted circuit is the schematic —
  the same four devices, the same sizes and the same connections — but LVS
  still fails, because only `IREF_OUT` carries a pin label. `IREF_IN`, `Va` and
  `Vss` are extracted as unnamed nets. Label them (text on `Metal2.text`
  10/25 over a `Metal2.pin` 10/2 shape, as `IREF_OUT` is) and LVS should pass.
* magic reports "can't abut or partially overlap between subcells" inside the
  cell: `Mp1` and `Mp2` overlap by 1.01 µm by hand. KLayout's sign-off deck
  accepts it; it would matter for an extraction through magic.

The leaf cells were generated with magic's gencells and these options on top
of the defaults the `lvds_tx` flow uses (`guard 1`, `full_metal 1`, no vias,
`conn_gates 0 polycov 50` for L ≥ 2 µm):

| Device | Options | Why |
|---|---|---|
| `Mp1`, `Mp2` (one cell, `dev_p_w8_l2_ng6_openn_botc0`) | `botc 0`, `polycov 85`, guard ring opened on top | gate contacted from the top only, five cuts per finger instead of three, and the gate leaves the cell without crossing a tap ring. Dropping the lower contact row pulls the ring 0.19 µm in, which breaks pSD.i1/pSD.d1; the ring was pushed back out after generation |
| `Mn2` (`dev_n_w8_l2_ng6`) | `botc 0`, `viagate 60` | top-only gate contact; 60 rather than 100 so source can still reach the guard ring between the gate pads |
| `Mn1` (`dev_n_w3p2_l2_ng1`) | `viagate 100`, `viadrn 100` | gate and drain brought up to metal2 |

## Running

```bash
make sim-all          # testbench
make klayout-drc      # sign-off DRC of layout/iref_x15.gds
make klayout-lvs      # needs the three missing pin labels, see above
```
