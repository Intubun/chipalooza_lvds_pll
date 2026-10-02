#!/usr/bin/env python3
"""Generate the charge-pump device wrapper cells (layout/mag/cp_*.mag).

Each wrapper places one PDK device cell and brings its terminals to fixed
ports the charge_pump parent routes to:

    D  metal3, bottom edge (y -479..-421)
    S  metal4, top edge    (y  421..479)
    G  metal2 pad
    B  metal2 pad, lower right

Units are Magic internal units (5 nm). Rules that drive the shapes:
  * isolated M2/M3 landings are 0.29 x 0.50 um (>= 0.144 um^2, M2.d/M3.d);
  * a via1 needs 0.05 um of metal on two opposite sides (V1.c1/M2.c1);
  * the generator's own gate rail (viagate 100) already carries via1 and M2,
    so the wrapper only covers that rail in M2 rather than adding metal1.
"""
from pathlib import Path

MAG = Path(__file__).resolve().parents[2] / "layout/mag"


class Cell:
    def __init__(self, device):
        self.device = device
        self.layers = {}
        self.labels = []

    def rect(self, layer, x0, y0, x1, y1):
        self.layers.setdefault(layer, []).append(
            (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))

    def label(self, layer, box, text, port):
        self.labels.append((layer, box, text, port))

    def write(self, name):
        out = ["magic", "tech ihp-sg13cmos5l", "magscale 1 2", "timestamp 0",
               f"use {self.device} M0", "timestamp 0",
               "transform 1 0 0 0 1 0", "box 0 0 1 1"]
        order = ["nwell", "psubdiff", "nsubdiff", "psubdiffcont",
                 "nsubdiffcont", "metal1", "via1", "metal2", "via2",
                 "metal3", "via3", "metal4"]
        for layer in order:
            if layer in self.layers:
                out.append(f"<< {layer} >>")
                out += ["rect %d %d %d %d" % r for r in self.layers[layer]]
        out.append("<< labels >>")
        for layer, (x0, y0, x1, y1), text, port in self.labels:
            out += [f"rlabel {layer} {x0} {y0} {x1} {y1} 0 {text}",
                    f"port {port} nsew"]
        out.append("<< end >>")
        (MAG / f"{name}.mag").write_text("\n".join(out) + "\n")
        print(f"wrote {name}.mag")


def via(cell, cut, x, y):
    cell.rect(cut, x - 20, y - 20, x + 20, y + 20)


def sd_stacks(cell, d_xs, s_xs, m1=True):
    """D stripes go down on metal3, S stripes up on metal4."""
    for x in d_xs + s_xs:
        if m1:
            cell.rect("metal1", x - 29, -29, x + 29, 29)
            via(cell, "via1", x, 0)
        cell.rect("metal2", x - 29, -50, x + 29, 50)
        via(cell, "via2", x, 0)
    for x in d_xs:
        cell.rect("metal3", x - 29, -450, x + 29, 29)
    cell.rect("metal3", min(d_xs) - 29, -479, max(d_xs) + 29, -421)
    for x in s_xs:
        cell.rect("metal3", x - 29, -50, x + 29, 50)
        via(cell, "via3", x, 0)
        cell.rect("metal4", x - 29, -29, x + 29, 479)
    cell.rect("metal4", min(s_xs) - 29, 421, max(s_xs) + 29, 479)
    d_port = (d_xs[len(d_xs) // 2] - 29, -479, d_xs[len(d_xs) // 2] + 29, -421)
    s_port = (s_xs[len(s_xs) // 2] - 29, 421, s_xs[len(s_xs) // 2] + 29, 479)
    cell.label("metal3", d_port, "D", 2)
    cell.label("metal4", s_port, "S", 4)


def ring_bulk(cell, bx, ring_y0, ring_y1):
    """B pad tied to the bottom guard-ring bar."""
    by = (ring_y0 + ring_y1) // 2
    cell.rect("metal1", -29, ring_y0, bx + 29, ring_y1)
    cell.rect("metal1", bx - 29, by - 29, bx + 29, by + 29)
    via(cell, "via1", bx, by)
    cell.rect("metal2", bx - 29, by - 71, bx + 29, by + 29)
    cell.label("metal2", (bx - 29, by - 29, bx + 29, by + 29), "B", 1)


def guarded(name, device, d_xs, s_xs, rail_x, rail_y, ring_y, bx):
    """Device with its own guard ring and a via1/M2 gate rail (viagate 100)."""
    cell = Cell(device)
    sd_stacks(cell, d_xs, s_xs)
    y0, y1 = rail_y
    cell.rect("metal2", -rail_x, y0, rail_x, y1)       # top gate rail
    cell.rect("metal2", -rail_x, -y1, rail_x, -y0)     # bottom gate rail
    cell.label("metal2", (-29, y0, 29, y1), "G", 3)
    ring_bulk(cell, bx, *ring_y)
    cell.write(name)


def unguarded(name, device, stripe, bx, pmos):
    """Single-finger device without a guard ring (too small for vias on all
    terminals inside one). Its own via1/M2 cover S/D; the wrapper adds a gate
    landing above the device and a local tap for the bulk."""
    cell = Cell(device)
    sd_stacks(cell, [-stripe], [stripe], m1=False)
    # Gate: extend the top poly-contact metal1 up to a via1 landing.
    cell.rect("metal1", -60, 58, 60, 90)
    cell.rect("metal1", -60, -90, 60, -58)              # unused bottom contact
    # The gate landing keeps 0.21 um of M2 from the device's S/D straps.
    cell.rect("metal1", -29, 58, 29, 150)
    cell.rect("via1", -20, 100, 20, 140)
    cell.rect("metal2", -30, 92, 30, 192)
    cell.label("metal2", (-29, 134, 29, 192), "G", 3)
    # Bulk tap under the B pad.
    by = -148
    diff = "nsubdiff" if pmos else "psubdiff"
    cell.rect(diff, bx - 46, by - 46, bx + 46, by + 46)
    cell.rect(diff + "cont", bx - 16, by - 16, bx + 16, by + 16)
    cell.rect("metal1", bx - 35, by - 32, bx + 35, by + 32)
    via(cell, "via1", bx, by)
    cell.rect("metal2", bx - 30, by - 71, bx + 30, by + 29)
    cell.label("metal2", (bx - 29, by - 29, bx + 29, by + 29), "B", 1)
    if pmos:
        cell.rect("nwell", -143, by - 94, bx + 94, 92)
    cell.write(name)


def main():
    ng4 = [-352, -176, 0, 176, 352]
    ng8 = [-704 + 176 * i for i in range(9)]
    guarded("cp_n_w1_l0p5_ng4_strapped", "dev_n_w1_l0p5_ng4",
            ng4[0::2], ng4[1::2], 352, (115, 173), (-234, -202), 550)
    guarded("cp_p_w1_l0p5_ng8_strapped", "dev_p_w1_l0p5_ng8",
            ng8[0::2], ng8[1::2], 704, (115, 173), (-234, -202), 900)
    guarded("cp_p_w0p875_l0p5_ng8_strapped", "dev_p_w0p875_l0p5_ng8",
            ng8[0::2], ng8[1::2], 704, (103, 161), (-222, -190), 900)
    guarded("cp_p_w1_l0p13_ng1_access", "dev_p_w1_l0p13_ng1",
            [-51], [51], 51, (115, 173), (-234, -202), 270)
    guarded("cp_n_w1p5_l0p13_ng1_access", "dev_n_w1p5_l0p13_ng1",
            [-51], [51], 51, (165, 223), (-284, -252), 270)
    unguarded("cp_n_w0p15_l0p13_ng1_access",
              "dev_n_w0p15_l0p13_ng1_noguard_sdvia", 57, 276, pmos=False)
    unguarded("cp_p_w0p3_l0p13_ng1_access",
              "dev_p_w0p3_l0p13_ng1_noguard_sdvia", 51, 270, pmos=True)


if __name__ == "__main__":
    main()
