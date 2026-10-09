#!/usr/bin/env python3
"""Write the schematic and symbol of lvds_bt - the switchable back-termination of the LVDS pair.

    schematic/xschem/lvds_bt.sch, .sym

    OUTP --- R1 rppd 10/3.3 (93 ohm) --- A --- MSW sg13_hv_nmos 300/0.45, 30 fingers --- B --- R2 (93 ohm) --- OUTN
    EN --- xls (ref_odt_lvlup, macros/ref_odt) --- ENH = gate of MSW, 0 / 3.3 V
     '---- DEN dantenna 0.78/0.78 (antenna diode on the long EN line)

EN = 1: MSW on (gate at 3.3 V, source and drain near the 1.2 V common mode,
~11 ohm), R1 + MSW + R2 ~ 200 ohm across the pair.  The LVDS driver is a
current source; with 200 ohm behind the pads its output looks like 200 ohm
differential instead of an open, and a wave coming back from the receiver is
absorbed to two thirds instead of being thrown back whole.  The pair then sees
100 || 200 = 67 ohm: the driver current has to be 1.5 times as high for the
same |Vod| - ibias1 3 uA instead of 2 uA.
EN = 0: MSW off, the pair sees R1 / R2 and MSW's junctions - a few 10 fF each.

The level shifter is ref_odt's (sg13cmos5l_LevelUp, transistor for transistor);
the layout carries the same cell.  No clamp diodes on A and B: R1 / R2 sit in
front of them, and the driver's own transistors are on the pads without any.

    python3 scripts/gen_schematic.py
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
SCH = os.path.join(HERE, "..", "schematic", "xschem")
PR = "sg13cmos5l_pr/"
HEADER = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}", "V {}", "S {}", "F {}", "E {}"]
RPPD_VALUE = ('value=\\"expr_eng(  ( 70.0e-6 / @w + 260.0 * ( (@b + 1)* @l + ( 1.081*( @w + 6.0e-9 ) '
              '+ 0.18e-6 )*@b ) / ( @w + 6.0e-9 ) ) / @m  )\\"')


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
        flip = 1 if kind == "ipin" else 0
        self.out.append("C {devices/%s.sym} %d %d %d %d {name=p_%s lab=%s}" % (kind, x, y, 2 if left else 0, flip, net, net))

    def text(self, x, y, s, size=0.35):
        self.out.append("T {%s} %d %d 0 0 %s %s {}" % (s, x, y, size, size))

    def write(self, path):
        io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(self.out) + "\n")


def rppd(name):
    return ["name=" + name, "w=10u", "l=3.3u", "model=rppd", "body=VSS", "spiceprefix=X",
            "b=0", "m=1", "mm_ok=1", RPPD_VALUE]


def gen_bt(path):
    s = Sheet()
    s.text(-520, -980, """lvds_bt - switchable back-termination of the LVDS pair, ~200 ohm differential

  EN = 1   R1 + MSW + R2 ~ 200 ohm from OUTP to OUTN (MSW's gate at 3.3 V through xls)
  EN = 0   off: the pair sees R1 / R2 and MSW's junctions, no current

The driver is a current source: without this, a wave coming back from the receiver
is thrown back whole.  With it, two thirds are absorbed.  The pair then sees
100 || 200 = 67 ohm - ibias1 3 uA instead of 2 uA keeps |Vod|.""", 0.4)
    # OUTP -> R1 -> A
    s.port("iopin", -200, -620, "OUTP")
    s.wire((-200, -620), (0, -620), (0, -550), net="OUTP")
    s.inst(PR + "rppd.sym", 0, -520, rppd("R1"))
    s.text(30, -550, "93 ohm, 10 um wide")
    s.wire((0, -490), (0, -300), net="A")
    s.wlab(0, -400, "A")
    # the switch, drain A on top, source B below
    s.inst(PR + "sg13_hv_nmos.sym", -20, -270, ["name=MSW", "l=0.45u", "w=300u", "ng=30", "m=1", "mm_ok=1",
                                                 "model=sg13_hv_nmos", "spiceprefix=X"])
    s.wire((0, -270), (40, -270)); s.lab(40, -270, "VSS", right=True)
    s.text(40, -330, "300/0.45 HV, 30 fingers:\n~11 ohm with S/D at 1.2 V")
    s.wire((0, -240), (0, -170), net="B")
    s.wlab(0, -200, "B")
    # B -> R2 -> OUTN
    s.inst(PR + "rppd.sym", 0, -140, rppd("R2"))
    s.wire((0, -110), (0, -60), (-200, -60), net="OUTN")
    s.port("iopin", -200, -60, "OUTN")
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
    for i, net in enumerate(("VDD", "VDDH", "VSS")):
        y = 40 + 40 * i
        s.port("iopin", -520, y, net)
        s.wire((-520, y), (-480, y), net=net)
        s.lab(-480, y, net, right=True)
    s.write(path)


def gen_sym(path, pins, w=100, h=80, title="@symname"):
    out = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}",
           "K {type=subcircuit", 'format="@name @pinlist @symname"', 'template="name=x1"', "}",
           "V {}", "S {}", "E {}",
           "P 4 5 %d %d %d %d %d %d %d %d %d %d {}" % (-w, -h, w, -h, w, h, -w, h, -w, -h),
           "T {%s} -45 -6 0 0 0.3 0.3 {}" % title, "T {@name} %d %d 0 0 0.2 0.2 {}" % (w + 5, -h - 12)]
    for name, d, side, pos in pins:
        x, y = (-w if side == "l" else w), pos
        sx = -1 if side == "l" else 1
        out.append("B 5 %s %s %s %s {name=%s dir=%s}" % (x + sx * 17.5, y - 2.5, x + sx * 22.5, y + 2.5, name, d))
        out.append("L %d %d %d %d %d {}" % (4 if d != "inout" else 7, x, y, x + sx * 20, y))
        out.append("T {%s} %d %d 0 %d 0.2 0.2 {}" % (name, x - sx * 5, y - 4, 0 if side == "l" else 1))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    os.makedirs(SCH, exist_ok=True)
    gen_bt(os.path.join(SCH, "lvds_bt.sch"))
    gen_sym(os.path.join(SCH, "lvds_bt.sym"),
            [("EN", "in", "l", -40), ("OUTP", "inout", "l", 0), ("OUTN", "inout", "l", 40),
             ("VDD", "inout", "r", -40), ("VDDH", "inout", "r", 0), ("VSS", "inout", "r", 40)])
    print("wrote lvds_bt.sch/.sym")
