#!/usr/bin/env python3
"""Write the schematics and symbols of ref_odt - the switchable termination of ref_clk.

    schematic/xschem/ref_odt.sch, .sym              the block
    schematic/xschem/ref_odt_lvlup.sch, .sym        its level shifter, 1.2 V -> 3.3 V

    PAD --- R1 rppd 40/6.65 (45 ohm) --- X --- MSW sg13_hv_nmos 300/0.45, 30 fingers --- VSS
                                         |-- DN dantenna 20/1.26  (X to the substrate)
                                         '-- DP dpantenna 20/1.26 (X to VDDH)
    EN --- xls (ref_odt_lvlup) --- ENH = gate of MSW, 0 / 3.3 V
     '---- DEN dantenna 0.78/0.78 (antenna diode on the long EN line)

EN = 1: MSW on with its gate at 3.3 V, R1 + Ron = 50 ohm from PAD to VSS.
EN = 0: MSW off, PAD sees R1, the diodes and MSW's drain - 0.25 pF and no current.

ref_odt_lvlup is sg13cmos5l_LevelUp of the IO library, transistor for
transistor; layout/ref_odt.gds carries its layout as the cell of the same name,
so the LVS compares the two hierarchically.  R1 is the first thing behind the
pad and limits what an ESD event can push into MSW's drain; DN / DP clamp that
node like the pad's own secondary protection does.

The signal path is drawn with wires; supplies are labels.

    python3 scripts/gen_schematic.py
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
SCH = os.path.join(HERE, "..", "schematic", "xschem")
PR = "sg13cmos5l_pr/"
HEADER = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}", "V {}", "S {}", "F {}", "E {}"]


class Sheet:
    def __init__(self):
        self.out = list(HEADER)
        self.n = 0

    def wire(self, *pts, net=None):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            self.out.append("N %d %d %d %d {%s}" % (x1, y1, x2, y2, "lab=%s" % net if net else ""))

    def inst(self, sym, x, y, props, rot=0, flip=0):
        self.out.append("C {%s} %d %d %d %d {%s}" % (sym, x, y, rot, flip, "\n".join(props)))

    def lab(self, x, y, net, right=False):
        self.n += 1
        self.out.append("C {devices/lab_pin.sym} %d %d 0 %d {name=l%d sig_type=std_logic lab=%s}"
                        % (x, y, 1 if right else 0, self.n, net))

    def wlab(self, x, y, net):
        self.n += 1
        self.out.append("C {devices/lab_wire.sym} %d %d 0 0 {name=w%d sig_type=std_logic lab=%s}" % (x, y, self.n, net))

    def port(self, kind, x, y, net, left=True):
        """a port whose pin sits at (x, y), the body to the left (or right)"""
        flip = 1 if kind == "ipin" else 0
        self.out.append("C {devices/%s.sym} %d %d %d %d {name=p_%s lab=%s}" % (kind, x, y, 2 if left else 0, flip, net, net))

    def text(self, x, y, s, size=0.35):
        self.out.append("T {%s} %d %d 0 0 %s %s {}" % (s, x, y, size, size))

    def write(self, path):
        io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(self.out) + "\n")


def mos(kind, w, l, ng=1):
    model = {"nlv": "sg13_lv_nmos", "plv": "sg13_lv_pmos", "nhv": "sg13_hv_nmos", "phv": "sg13_hv_pmos"}[kind]
    return ["l=%s" % l, "w=%s" % w, "ng=%d" % ng, "m=1", "mm_ok=1", "model=%s" % model, "spiceprefix=X"], model


# ---------------------------------------------------------------------------------- ref_odt
def gen_odt(path):
    s = Sheet()
    s.text(-520, -900, """ref_odt - switchable 50 ohm termination of the ref_clk pad

  EN = 1   R1 + MSW = 50 ohm from PAD to VSS (MSW's gate at 3.3 V through xls)
  EN = 0   off: no current, ~0.25 pF on PAD

PAD is pad 2 itself (s14_an[2]) - not its secondary-protection output, where
~520 ohm in series would make the termination a divider.  R1 is the first thing
behind the pad, so it also limits what an ESD event drives into MSW's drain;
DN / DP clamp that node to VSS and VDDH.""", 0.4)
    # PAD -> R1 -> X
    s.port("iopin", -200, -540, "PAD")
    s.wire((-200, -540), (0, -540), (0, -470), net="PAD")
    s.inst(PR + "rppd.sym", 0, -440, ["name=R1", "w=40u", "l=6.65u", "model=rppd", "body=VSS", "spiceprefix=X",
                                      "b=0", "m=1", "mm_ok=1",
                                      'value=\\"expr_eng(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) + 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )\\"'])
    s.text(30, -470, "45 ohm, 40 um wide:\n24 mA and ESD")
    # X: down to the switch, across to the two diodes
    s.wire((0, -410), (0, -300), net="X")
    s.wire((0, -380), (260, -380), net="X")
    s.wlab(180, -380, "X")
    s.inst(PR + "dantenna.sym", 120, -330, ["name=DN", "model=dantenna", "l=1.26u", "w=20u", "spiceprefix=X"])
    s.wire((120, -380), (120, -360), net="X")
    s.lab(120, -300, "VSS")
    s.inst(PR + "dpantenna.sym", 260, -410, ["name=DP", "model=dpantenna", "l=1.26u", "w=20u", "spiceprefix=X"])
    s.lab(260, -440, "VDDH")
    s.text(290, -360, "DN, DP: clamp X\nto VSS / VDDH")
    # the switch
    props, _ = mos("nhv", "300u", "0.45u", 30)
    s.inst(PR + "sg13_hv_nmos.sym", -20, -270, ["name=MSW"] + props)
    s.wire((0, -270), (40, -270)); s.lab(40, -270, "VSS", right=True)
    s.wire((0, -240), (0, -200)); s.lab(0, -200, "VSS")
    s.text(40, -230, "300/0.45 HV, 30 fingers:\n~5 ohm at 3.3 V gate drive")
    # EN -> level shifter -> ENH -> gate
    s.port("ipin", -520, -270, "EN")
    s.wire((-520, -270), (-330, -270), net="EN")
    s.inst("ref_odt_lvlup.sym", -250, -270, ["name=xls"])
    s.wire((-170, -270), (-40, -270), net="ENH")
    s.wlab(-110, -270, "ENH")
    for x, y, net in ((-290, -330, "VDD"), (-210, -330, "VDDH")):
        s.wire((x, y), (x, y - 30)); s.lab(x, y - 30, net)
    s.wire((-250, -210), (-250, -180)); s.lab(-250, -180, "VSS")
    s.inst(PR + "dantenna.sym", -420, -210, ["name=DEN", "model=dantenna", "l=0.78u", "w=0.78u", "spiceprefix=X"])
    s.wire((-420, -240), (-420, -270), net="EN")
    s.lab(-420, -180, "VSS")
    s.text(-470, -150, "DEN: antenna diode\non the long EN line")
    # supply ports
    for i, net in enumerate(("VDD", "VDDH", "VSS")):
        y = -40 + 40 * i
        s.port("iopin", -520, y, net)
        s.wire((-520, y), (-480, y), net=net)
        s.lab(-480, y, net, right=True)
    s.write(path)


# ---------------------------------------------------------------------------- the shifter
def gen_lvlup(path):
    s = Sheet()
    s.text(-150, -420, """ref_odt_lvlup - 1.2 V -> 3.3 V level shifter, non-inverting
= sg13cmos5l_LevelUp of the IHP IO library, transistor for transistor.
Input inverter on vdd (LV), cross-coupled pair and output inverter on iovdd (HV).""", 0.4)
    cols = [  # x, top device, bottom device, drain net, (top gate, bottom gate)
        (0,   ("MP_I",  "plv", "4.75u", "0.13u"), ("MN_I",  "nlv", "2.75u", "0.13u"), "IN_N",   ("i", "i")),
        (300, ("MP_LN", "phv", "0.3u",  "0.45u"), ("MN_LN", "nhv", "1.9u",  "0.45u"), "LVLD_N", ("LVLD", "i")),
        (550, ("MP_L",  "phv", "0.3u",  "0.45u"), ("MN_L",  "nhv", "1.9u",  "0.45u"), "LVLD",   ("LVLD_N", "IN_N")),
        (800, ("MP_O",  "phv", "3.9u",  "0.45u"), ("MN_O",  "nhv", "1.9u",  "0.45u"), "o",      ("LVLD_N", "LVLD_N")),
    ]
    for x, top, bot, dnet, (gt, gb) in cols:
        for (name, kind, w, l), y in ((top, -100), (bot, 50)):
            props, model = mos(kind, w, l)
            s.inst(PR + model + ".sym", x, y, ["name=" + name] + props)
            supply = "vdd" if kind == "plv" else ("iovdd" if kind == "phv" else "vss")
            if kind[0] == "p":                          # pmos: S on top (x+20, y-30)
                s.wire((x + 20, y - 30), (x + 20, y - 60)); s.lab(x + 20, y - 60, supply)
            else:                                       # nmos: S at the bottom (x+20, y+30)
                s.wire((x + 20, y + 30), (x + 20, y + 60)); s.lab(x + 20, y + 60, supply)
            s.wire((x + 20, y), (x + 50, y)); s.lab(x + 50, y, supply, right=True)      # bulk
        s.wire((x + 20, -70), (x + 20, 20), net=dnet)                                    # the two drains
        s.wlab(x + 20, -25, dnet)
        if gt == gb and x in (0, 800):                                                  # an inverter: gates joined
            s.wire((x - 20, -100), (x - 60, -100), (x - 60, 50), (x - 20, 50), net=gt)
        else:
            s.lab(x - 20, -100, gt); s.lab(x - 20, 50, gb)
    s.port("ipin", -150, -25, "i")
    s.wire((-150, -25), (-60, -25), net="i")
    s.lab(740, -25, "LVLD_N")
    s.port("opin", 950, -25, "o", left=False)
    s.wire((820, -25), (950, -25), net="o")
    for i, net in enumerate(("vdd", "iovdd", "vss")):
        y = 200 + 40 * i
        s.port("iopin", -150, y, net)
        s.wire((-150, y), (-110, y), net=net)
        s.lab(-110, y, net, right=True)
    s.write(path)


# ----------------------------------------------------------------------------------- symbols
def gen_sym(path, pins, w=100, h=80, title="@symname"):
    out = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}",
           "K {type=subcircuit", 'format="@name @pinlist @symname"', 'template="name=x1"', "}",
           "V {}", "S {}", "E {}",
           "P 4 5 %d %d %d %d %d %d %d %d %d %d {}" % (-w, -h, w, -h, w, h, -w, h, -w, -h),
           "T {%s} -45 -6 0 0 0.3 0.3 {}" % title, "T {@name} %d %d 0 0 0.2 0.2 {}" % (w + 5, -h - 12)]
    for name, d, side, pos in pins:
        if side in ("l", "r"):
            x, y = (-w if side == "l" else w), pos
            sx = -1 if side == "l" else 1
            out.append("B 5 %s %s %s %s {name=%s dir=%s}" % (x + sx * 17.5, y - 2.5, x + sx * 22.5, y + 2.5, name, d))
            out.append("L %d %d %d %d %d {}" % (4 if d != "inout" else 7, x, y, x + sx * 20, y))
            out.append("T {%s} %d %d 0 %d 0.2 0.2 {}" % (name, x - sx * 5, y - 4, 0 if side == "l" else 1))
        else:
            x, y = pos, (-h if side == "t" else h)
            sy = -1 if side == "t" else 1
            out.append("B 5 %s %s %s %s {name=%s dir=%s}" % (x - 2.5, y + sy * 17.5, x + 2.5, y + sy * 22.5, name, d))
            out.append("L 7 %d %d %d %d {}" % (x, y, x, y + sy * 20))
            out.append("T {%s} %d %d 0 0 0.2 0.2 {}" % (name, x - 10, y - sy * 15 - (8 if sy > 0 else 0)))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    gen_odt(os.path.join(SCH, "ref_odt.sch"))
    gen_lvlup(os.path.join(SCH, "ref_odt_lvlup.sch"))
    gen_sym(os.path.join(SCH, "ref_odt.sym"),
            [("EN", "in", "l", -40), ("PAD", "inout", "l", 0),
             ("VDD", "inout", "r", -40), ("VDDH", "inout", "r", 0), ("VSS", "inout", "r", 40)])
    # pins at +-80 / +-40 from the centre, so they meet the wires of ref_odt.sch at (-330, -270) etc.
    gen_sym(os.path.join(SCH, "ref_odt_lvlup.sym"),
            [("i", "in", "l", 0), ("o", "out", "r", 0),
             ("vdd", "inout", "t", -40), ("iovdd", "inout", "t", 40), ("vss", "inout", "b", 0)],
            w=60, h=40, title="lvlup")
    print("wrote ref_odt.sch/.sym and ref_odt_lvlup.sch/.sym")
