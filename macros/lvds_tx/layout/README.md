# `lvds_tx` layout — placement stage

Magic layout of `schematic/xschem/lvds_tx.sch`, generated from the schematic
rather than drawn by hand. **This is the placement stage only: every device
and every sub-block is instantiated and legally placed, and nothing is
routed.** The cells are a frame to route into.

```bash
docker exec iic-osic-tools_xserver bash -lc \
  'bash /foss/designs/chipalooza_lvds_pll/macros/lvds_tx/layout/run_all.sh'
```

That runs the whole flow — netlist, leaf cells, placement, DRC, GDS, KLayout
sign-off DRC — and prints a pass/fail summary.

Current status: **93.8 × 179.4 µm, 53 device instances in six cells, DRC
clean in magic `drc(full)` at every level of the hierarchy and in the KLayout
sign-off deck.** There is no LVS: with no routing there are no nets to
compare, and an extract finds each device on its own island.

## Hierarchy

One magic cell per subcircuit, named after it, so the cell opened in magic is
the cell being looked at in xschem:

| Cell | Blocks | Size | What it holds |
|---|---|---|---|
| `lvds_tx` | 4 | 93.8 × 179.4 µm | `Xm_pd`, `Xm_drv`, `Xpd`, `Xdrv` |
| `Driver` | 22 | 88.6 × 59.4 µm | H-bridge, CMFB amplifier, tail, damping caps |
| `predriver` | 4 | 44.1 × 114.0 µm | two comparators, the stage, `MRef` |
| `predriver_stage` | 16 | 23.0 × 62.5 µm | the two three-inverter chains and the cross-coupling |
| `predriver_comp` | 5 | 40.1 × 18.7 µm | one differential comparator |
| `iref_x15` | 4 | 20.8 × 46.8 µm | the ×15 current mirror, instantiated twice |

`Driver` carries 22 blocks against the schematic's 19 devices because `M6` is
written `m=4` there: gencell does not strap the gates between the rows of an
`m>1` device, so the four blocks are instantiated separately and will be
strapped by the router.

## Files

| | |
|---|---|
| `devices.py` | reads `netlist/schematic/lvds_tx.spice` into a hierarchy of subcircuits, devices and instances. Converts the schematic's total `w` to the per-finger `w` gencell wants, and expands `m=n` into `n` instances |
| `gen_devices.py` | emits the Tcl that builds one leaf cell per distinct device geometry |
| `patch_cells.py` | repairs the two DRC errors the PDK gencells leave behind (see below) |
| `magfile.py` | reader/writer for magic `.mag` files. 1 internal unit = 5 nm |
| `build_placement.py` | places each subcircuit and writes its `.mag`; keeps what `floorplan.json` already fixes |
| `floorplan.json` | the block positions, kept across rebuilds |
| `build_cells.sh` | regenerates and DRCs the leaf cells, then checks the cells above (`make layout-cells`) |
| `run_all.sh` | the whole flow (`make layout`) |
| `check_untouched.sh` | records and verifies that `lvds_tx.gds` was not written |
| `check_drc*.tcl`, `save_gds.tcl` | the magic batch scripts |
| `cells/` | generated leaf cells — build artifacts, not in git |

## How the placement is arranged

Blocks are shelf-packed in netlist order, with a 2 µm gap between
neighbours and a 2 µm margin at the edge. Netlist order means the
arrangement can be read against the schematic; it is not a floorplan, and no
later stage depends on it.

Only the width the shelves break at is searched for. Every prefix of the
block list is a candidate — in a fixed order that is the complete set of
widths giving a different set of shelves — and the smallest bounding box
wins, among those whose aspect ratio stays inside 1:3 … 3:1.

Area decides and shape only rules candidates out, because the two cannot be
weighed against each other: a shape term strong enough to reject the single
column (one shelf wastes no space at all, and hands the parent a block it
cannot pack) is also strong enough to accept a packing half again as large.
Deriving one target width from the total area instead, the obvious thing,
makes the cell jump in size whenever a block changes.

The gap is what keeps the placement DRC clean before anything is routed:
every leaf cell carries its own guard ring, so neighbours would otherwise run
into nwell and substrate-tie spacing. It also leaves room for a few tracks,
which is the point of the next stage.

It was 4 µm, and on a leaf cell that turned out to be the largest single term
in the area: `predriver_comp` was 35 % device and 65 % gap. At 2 µm it is
751 µm² instead of 1141, still DRC clean at every level. Raise it again if
the routing needs the room — nothing else depends on the value.

The price is white space — `lvds_tx` is 16 800 µm² of which the sub-blocks
fill 12 200. Most of what is left is one notch: `predriver` is 114 µm tall
and sits beside two 47 µm `iref_x15` blocks, and shelf packing cannot fold
anything into the space above them. Sub-blocks are rectangles of quite different shapes, and shelf
packing does not fold one into another's notch. Worth revisiting when the
routing fixes which edges matter.

## Device options

Set in `gen_devices.py` for every MOSFET, or per device in
`devices.py:GENCELL_OVERRIDES`:

| | |
|---|---|
| `viasrc 0 viadrn 0 viagate 0` | **every transistor terminal ends on metal1.** No via1, no metal2 anywhere in a MOSFET cell, so the router owns metal2 and up. Costs no area — the guard ring sets the cell size, not the strap |
| `guard 1` | each device carries its own bulk tie. The ring *is* the `B` terminal: with `guard 0` the cell has no bulk connection at all |
| `conn_gates 1` | the fingers share one gate rail — one `G` terminal, but a wall between source/drain and the guard ring |
| `conn_gates 0 polycov 50` on `l ≥ 2 µm` | one contact per finger (`G0`…`Gn`) and a shortened contact, opening a 0.99 µm metal1 corridor between the pads so source/drain can reach the ring |
| `botc 0` on `iref_x15` `Mp2` | gate contacted from the top only, one poly contact row instead of two. `Mp1` keeps both |
| `_open n` on `iref_x15` `Mp1`/`Mp2` | guard ring cut open along the top edge, so the gate leaves the cell without crossing a tap ring |

`iref_x15` carries the one deliberate departure from the schematic's own
finger counts: `Mn2` is written `w=48u ng=6`, six fingers of 8 µm, which is
the finger geometry `Mp1`/`Mp2` already had. Total width, length and the 15:1
ratio against `Mn1` are untouched, so the mirror is electrically the same
device; it packs better next to the PMOS, and the cell came down from
1594 µm² at 15 fingers to 1101 µm².

`rhigh` and `cap_cmomf` keep their metal2: the MOM cap *is* interdigitated
metal1–metal4, and the resistor's cap is part of how the PDK generates it.

`_open` is not a gencell parameter — the generator draws the ring whole or
not at all. `patch_cells.py:open_guard_ring` takes the tap bar on that side
away afterwards and clips the two side bars back to it, leaving a U. The
well stays: it has to keep enclosing the FET, and it is not what blocks a
wire. The `B` terminal moves onto what is left of the ring, so the cell
still has a bulk connection. Both checkers pass, but a U is a weaker guard
than a closed ring — the latch-up path along the open edge is no longer
interrupted.

The one-sided gate contact does not save area. Dropping the row lets the
generator pull the guard ring 0.19 µm closer to the FET, which breaks the
0.43 µm FET-to-tap spacing (14 violations of pSD.i1/pSD.d1), so
`patch_cells.py:pad_guard_ring` stretches that side of the ring back out and
the cell ends up exactly the size it was. What it buys is a gate that is only
contacted from one side.

## Who owns which file

The generator and the person editing the layout do not share a file. This is
a rule, not an intention, and `check_untouched.sh` is what makes it testable.

| | |
|---|---|
| `lvds_tx.gds` | **the user's.** Nothing in this directory writes it, ever. KLayout saves here, sign-off reads it |
| `lvds_tx_gen.gds` | the generator's. Rewritten by every run, never edited by hand |
| `cells/`, `*.mag`, `floorplan.json` | generated, rebuilt at will |
| `backups/` | KLayout's autosaves, plus copies of anything ever rescued |

```bash
bash check_untouched.sh          # record the state of lvds_tx.gds
bash check_untouched.sh verify   # and prove afterwards that it is untouched
```

`make layout` and `make layout-cells` both end with `verify` reporting
`unveraendert: lvds_tx.gds`. When the generator's result should become the
working file, that is a copy the user makes, not something a script does.

`make layout-view` opens `lvds_tx_gen.gds` in a **new** KLayout window. It
does not close, kill or reload anything already open — a running editor is
the user's, and a script has no business ending it.

## The placement is sticky

`floorplan.json` holds the position of every block once it has been decided.
A rebuild reads it, keeps every instance exactly where it is, and only finds
room for what is new — so changing how a device is drawn, or adding one,
does not move the rest of the block. Without it the packer re-derived every
position from scratch on every run, which meant there was no way to touch a
device without redoing the whole layout.

New blocks go on a fresh shelf above everything. That is never the prettiest
answer, but it is always a legal one and easy to see. If a cell grew enough
that two blocks no longer clear each other, the run stops and names the
pair rather than writing an overlap:

```
Blöcke liegen zu dicht beieinander, weil eine Zelle gewachsen ist:
  Driver             M5 <-> M4
```

`make layout-replace` throws the stored floorplan away and packs everything
from scratch. That is also what to run when the layout has drifted: after
an instance is renamed, the old position is orphaned and the new name lands
on a shelf of its own, which costs area until the next re-pack.

`floorplan.json` is the one file here worth editing by hand — move a block
by changing two numbers, rebuild, and the router sees it.

## Rebuilding only the devices

`make layout-cells` regenerates `cells/` and stops there. The `.mag`
hierarchy and `lvds_tx.gds` are not touched, so a change to how the devices
are drawn — gate contacts, guard rings, via coverage — costs one minute
instead of the whole flow, and anything drawn into the GDS by hand survives.

That is only sound while the leaf cells keep their **names** and their
**sizes**. A new or vanished cell leaves an instance above pointing at
nothing; a cell that changed size leaves two blocks that used to clear each
other overlapping. `build_placement.py --check` recomputes the placement and
compares it against the `.mag` files on disk, and `build_cells.sh` runs it
last, so the rebuild always ends with one of:

```
Die Zellen oberhalb passen unveraendert - 6 Zellen geprueft, kein Neubau noetig.
Die Zellen oberhalb passen NICHT mehr:
  iref_x15           verweist noch auf dev_p_w8_l2_ng6_botc0
```

In the second case run `make layout`. Note that `lvds_tx.gds` stays stale
either way until the full flow writes it — the leaf geometry only reaches
KLayout through a new GDS.

Both paths now write `lvds_tx_gen.gds`, so a cells-only rebuild is visible
without the placement being redone and without `lvds_tx.gds` being involved
at all.

## Things that cost time

- **`load <cell>` in a magic script needs `addpath`.** Without it magic does
  not find the file, silently creates an empty cell under that name, and
  DRCs nothing — `check_drc_cells.tcl` reported every leaf cell clean for as
  long as the bug was in it, including cells with 28 violations. The
  hierarchical check and the KLayout deck were never affected: they read the
  real geometry, which is why the two disagreed the moment a leaf cell
  actually broke.
- **Individual gate contacts do not scale down.** `conn_gates 0` splits the
  gate rail into one contact per finger, which is what lets source and drain
  leave the device on metal1. Below 2 µm gate length the metal1 over a
  single poly contact falls under the 0.09 µm² minimum area (M1.d): 17 of 27
  cells fail at l = 0.4/0.45/0.5 µm, and 1 µm fails once `polycov` shortens
  the contact as well. Hence the threshold in `gen_devices.py`.
- **The gap between gate contacts does not grow with gate length.** It is
  the source/drain pitch, 0.42 µm on every device here, which is under the
  0.16 µm wire plus 2 × 0.18 µm spacing a metal1 track needs. `polycov` is
  what opens it: at 50 % the contact on a 2 µm gate shrinks from 1.86 to
  0.93 µm and the gap grows to 1.35 µm.
- **A `.mag` file's grid is not fixed.** magic picks the coarsest one the
  cell needs and writes `magscale 1 2` only when something sits on the 5 nm
  grid. Take the vias out of a device and the cell comes back with no
  `magscale` line at all, i.e. 10 nm per unit. Reading that as 5 nm halves
  every coordinate, which does not error — it produces a placement whose
  blocks sit on top of each other and 1059 DRC errors two steps later.
  `magfile.py` normalises on read.
- **The PDK gencells are not DRC clean at their defaults.** At
  `viasrc/viadrn 100` the source/drain metal2 strap stops 0.15 µm short of the
  gate rail, where rule M2.b wants 0.21, and every MOSFET carries spacing
  errors; at 80 the gap opens up, but on a 0.8 µm finger the strap then falls
  under the M2.d minimum area and has to be widened sideways. Both are moot
  now that the devices carry no metal2 — `patch_cells.py` keeps
  `patch_narrow_straps` for the day someone turns the vias back on. `rhigh`
  stops its metal1 cap 0.025 µm past the poly ContBar where CntB.h1 wants
  0.05 µm; that one still fires.
- **The netlist is build output.** `macros/lvds_tx/netlist` is in
  `.gitignore`, so `run_all.sh` regenerates it from the schematic before
  parsing it. A stale netlist cannot outlive the schematic it came from.
- **`source /foss/tools/sak/sak-pdk-script.sh ihp-sg13cmos5l` first.** The
  container leaves `PDK` empty, and without it magic's gencells and xschem's
  symbol paths are both missing — silently, not with an error.

## Next

1. Port labels on the sub-block terminals, then nets inside each leaf cell.
2. Route bottom-up: `predriver_comp`, `predriver_stage`, `iref_x15`, then
   `Driver`, then the two parents.
3. LVS against `lvds_tx.sch` and PEX, both already wired up in the macro
   `Makefile` (`make magic-verify CELL=lvds_tx`).
