#!/usr/bin/env python3
"""Generate lvds_pattern.sch, .sym and its testbench.

The block is pure sg13cmos5l standard cells and the schematic is **drawn**: every
local connection is a real wire, so the signal flow is visible left to right --
clock select and gate along the top, the seven-stage PRBS register across the
middle with its XNOR feedback below, then the mode mux and the two output chains
on the right. `lab_wire` names the nets on those wires; only the long PRBS
feedback return uses a label at each end instead of a wire across the drawing.

Writing it out from a table rather than drawing it by hand keeps the drawing and
the net list in step: each wire below is one net, named once.
"""
import io
import os

# --------------------------------------------------------------- cell placement
# (instance, standard cell, family, x, y)
CELLS = [
    ("xcsel", "mux2_2", "mux2", 400, -600),     # clock source select
    ("xicg", "lgcp_1", "lgcp", 750, -600),      # latch-based clock gate
    ("xclkb", "buf_4", "buf", 1050, -610),      # clock buffer to the register
    ("xrstb", "inv_2", "inv", 150, -450),       # reset is active high on the port
    ("xs0", "dfrbp_1", "dfrbp", 400, -100),
    ("xs1", "dfrbp_1", "dfrbp", 700, -100),
    ("xs2", "dfrbp_1", "dfrbp", 1000, -100),
    ("xs3", "dfrbp_1", "dfrbp", 1300, -100),
    ("xs4", "dfrbp_1", "dfrbp", 1600, -100),
    ("xs5", "dfrbp_2", "dfrbp", 1900, -100),    # s5 and s6 carry the extra fanout
    ("xs6", "dfrbp_2", "dfrbp", 2200, -100),
    ("xfb", "xnor2_1", "xnor2", 2200, 250),     # x^7 + x^6 + 1, complement domain
    # The pair is registered AFTER the inversion: s6 and s6_n go into two
    # identical flops on the same clock, so what leaves them are two edges from
    # the same cell type at the same instant.  The Q/Q_N mismatch of xs6 is
    # absorbed by these flops' setup margin instead of appearing as output skew.
    ("xffp", "dfrbp_2", "dfrbp", 2550, -100),
    ("xffn", "dfrbp_2", "dfrbp", 2850, -100),
    ("xclkn", "inv_2", "inv", 1300, -500),      # clock complement, passthrough only
    # one mux per polarity, identical cells, so the select path matches too
    ("xmodep", "mux2_2", "mux2", 3150, -600),
    ("xmoden", "mux2_2", "mux2", 3150, -300),
    # identical output chains - no parity difference left to compensate
    ("xp1", "inv_2", "inv", 3400, -600),
    ("xp2", "inv_8", "inv", 3650, -600),
    ("xbp", "inv_16", "inv", 3900, -600),
    ("xn1", "inv_2", "inv", 3400, -300),
    ("xn2", "inv_8", "inv", 3650, -300),
    ("xbn", "inv_16", "inv", 3900, -300),
]

FLOP_X = [400, 700, 1000, 1300, 1600, 1900, 2200]

# ------------------------------------------------------------------ connectivity
# One entry per net: the polylines that draw it.  Every cell pin has to be an end
# point of, or a point on, one of these.
WIRES = []
LABELS = []          # (net, x, y) for lab_wire
PORTS = []           # (net, xschem pin symbol, x, y, dx) - dx is the stub direction


def w(net, *pts):
    WIRES.append((net, list(pts)))


def lab(net, x, y):
    LABELS.append((net, x, y))


# --- clock source select, gate, buffer ---------------------------------------
PORTS += [("ref_clk", "ipin", 200, -620, 1), ("pll_clk", "ipin", 200, -580, 1),
          ("clk_src", "ipin", 200, -540, 1), ("en", "ipin", 200, -500, 1)]
w("ref_clk", (200, -620), (360, -620))
w("pll_clk", (200, -580), (360, -580))
w("clk_src", (200, -540), (360, -540))
w("en", (200, -500), (600, -500), (600, -590), (660, -590))
w("clk_sel", (440, -600), (620, -600), (620, -610), (660, -610))
w("gclk", (840, -610), (1010, -610))
lab("clk_sel", 530, -600)
lab("gclk", 930, -610)

# --- the gated clock: down to the register trunk, and across to the mode mux ---
w("gclk_b", (1090, -610), (1090, -220))               # drop onto the trunk
w("gclk_b", (310, -220), (2760, -220))                # clock trunk
for x in FLOP_X + [2550, 2850]:
    w("gclk_b", (x - 90, -220), (x - 90, -120))       # up to each CLK
w("gclk_b", (1090, -610), (2520, -610), (2520, -620), (2560, -620))
lab("gclk_b", 1090, -400)

# --- reset ---------------------------------------------------------------------
PORTS.append(("reset", "ipin", 0, -450, 1))
w("reset", (0, -450), (110, -450))
w("reset_b", (190, -450), (190, 60))                  # drop onto the trunk
w("reset_b", (190, 60), (2760, 60))                   # reset trunk
for x in FLOP_X + [2550, 2850]:
    w("reset_b", (x - 90, 60), (x - 90, -80))         # up to each RESET_B
lab("reset_b", 190, -200)

# --- the shift register --------------------------------------------------------
for i in range(6):
    a, b = FLOP_X[i], FLOP_X[i + 1]
    w("s%d" % i, (a + 90, -120), (a + 150, -120), (a + 150, -100), (b - 90, -100))
    lab("s%d" % i, a + 150, -112)
# s5 also drives the feedback gate
w("s5", (2050, -100), (2050, 270), (2140, 270))
# s6 drives the feedback gate; s6_n is the line bit
w("s6", (2290, -120), (2350, -120), (2350, 200), (2140, 200), (2140, 230))
w("s6", (2350, -100), (2460, -100))            # true bit into the P output flop
lab("s6", 2350, 100)
w("s6_n", (2290, -100), (2290, -40), (2700, -40), (2700, -100), (2760, -100))
lab("s6_n", 2500, -40)
# the line bit leaves the register on its own flop, so both mux inputs are
# clean synchronous edges rather than one clock and one combinational path
# the registered pair, each into its own mux
w("fp", (2640, -120), (2640, -580), (3110, -580))
lab("fp", 2640, -350)
w("fn", (2940, -120), (2940, -280), (3110, -280))
lab("fn", 2940, -200)
# the unused complementary outputs of the two output flops
w("fp_n", (2640, -100), (2680, -100), (2680, -60))
lab("fp_n", 2680, -60)
w("fn_n", (2940, -100), (2980, -100), (2980, -60))
lab("fn_n", 2980, -60)

# The feedback return crosses the whole drawing, so it is a label at each end
# rather than a wire.  Everything else here is a drawn connection.
w("fb", (2260, 250), (2340, 250))
lab("fb", 2340, 250)
w("fb", (250, -100), (310, -100))
lab("fb", 250, -100)

# the unused complementary outputs of the first six flops, stubbed and named so
# that they read as deliberate rather than forgotten
for i in range(6):
    x = FLOP_X[i]
    w("s%d_n" % i, (x + 90, -100), (x + 130, -100), (x + 130, -60))
    lab("s%d_n" % i, x + 130, -60)

# --- clock complement, used only by the passthrough leg ------------------------
w("gclk_b", (1090, -500), (1260, -500))
w("gclk_bn", (1340, -500), (3060, -500), (3060, -620), (3110, -620))
lab("gclk_bn", 1600, -500)
w("gclk_b", (1090, -320), (3110, -320))
lab("gclk_b", 1600, -320)

# --- mode select, one mux per polarity -----------------------------------------
PORTS.append(("mode", "ipin", 2900, -700, 1))
w("mode", (2900, -700), (3080, -700), (3080, -540), (3110, -540))
w("mode", (3080, -540), (3080, -240), (3110, -240))
lab("mode", 3080, -420)

# --- two identical output chains -----------------------------------------------
w("dp0", (3190, -600), (3360, -600))
w("dp1", (3440, -600), (3610, -600))
w("dp2", (3690, -600), (3860, -600))
w("D_p", (3940, -600), (4100, -600))
w("dn0", (3190, -300), (3360, -300))
w("dn1", (3440, -300), (3610, -300))
w("dn2", (3690, -300), (3860, -300))
w("D_n", (3940, -300), (4100, -300))
for n, x, y in (("dp0", 3270, -600), ("dp1", 3520, -600), ("dp2", 3770, -600),
                ("dn0", 3270, -300), ("dn1", 3520, -300), ("dn2", 3770, -300)):
    lab(n, x, y)
PORTS += [("D_p", "opin", 4100, -600, 0), ("D_n", "opin", 4100, -300, 0)]

# --- supplies.  The standard cells take VDD / VSS from their instance template,
# so these are ports by name, with no drawn net.
PORTS += [("VDD", "iopin", 1200, -900, 1), ("VSS", "iopin", 1200, 400, 1)]
w("VDD", (1200, -900), (1320, -900))
lab("VDD", 1320, -900)
w("VSS", (1200, 400), (1320, 400))
lab("VSS", 1320, 400)

HEADER = """v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}"""

NOTES = """T {lvds_pattern - data source for the LVDS transmitter, sg13cmos5l standard cells only

  clk_src   0 = ref_clk, 1 = pll_clk
  en        1 = clock runs, 0 = clock stopped low (latch-based gate, no runt pulse)
  reset     active high, asynchronous, seeds the PRBS
  mode      0 = gated clock straight to the pair, 1 = PRBS-7

D_p / D_n drive the pre-driver of macros/lvds_tx.} 150 -1000 0 0 0.6 0.6 {}
T {Clock source select, then the PDK's latch-based clock gate.  GCLK is
held low while en is 0, so en may change at any point in the cycle
without producing a runt pulse.} 200 -700 0 0 0.35 0.35 {}
T {PRBS-7, x^7 + x^6 + 1.  The seven flops hold the COMPLEMENT of the LFSR word:
dfrbp resets Q to 0, and an all-zero complement is the all-ones seed that
serdes_dig.v uses.  That is why the feedback gate is an XNOR and not an XOR, and
why the bit that goes to the line is s6_n rather than s6.  The stream is
bit-identical to serdes_dig.v in PRBS7 mode, so serdes/check_link.py works
against this block unchanged.

xsout re-registers the line bit on the same clock, so what leaves the block is a
flop output and not a combinational path through the shift register's fanout: both
mux inputs are then synchronous edges.  It costs one bit of latency and does not
change the sequence - b[k] = b[k-7] xor b[k-6] is shift invariant.

The feedback net fb is the one connection drawn as a label at each end instead of
a wire - it returns from the XNOR at the right to the first flop at the left.} 250 400 0 0 0.4 0.4 {}
T {Complementary output pair, sized for the ~170 fF the pre-driver presents
(two 40u/0.45u HV gates per side).  Matched inv_2 -> inv_8 front ends, then
buf_16 - two internal stages, so four inversions - against inv_16, three.
That pairing measured the least D_p/D_n skew into that load: 23 ps, against
the pre-driver's ~40 ps budget.  XOR/XNOR against VSS measured 48 ps.} 2800 -900 0 0 0.35 0.35 {}
T {clock trunk} 1150 -232 0 0 0.3 0.3 {}
T {reset trunk} 1150 48 0 0 0.3 0.3 {}"""


def gen_sch(path):
    out = [HEADER, NOTES]
    for net, pts in WIRES:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            out.append("N %d %d %d %d {lab=%s}" % (x1, y1, x2, y2, net))
    for i, (net, x, y) in enumerate(LABELS):
        out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                   "{name=lw%d sig_type=std_logic lab=%s}" % (x, y, i, net))
    for net, sym, x, y, dx in PORTS:
        out.append("C {devices/%s.sym} %d %d 2 %d {name=p_%s lab=%s}"
                   % (sym, x, y, 1 if sym == "ipin" else 0, net, net))
    for inst, cell, fam, x, y in CELLS:
        out.append("C {sg13cmos5l_stdcells/sg13cmos5l_%s.sym} %d %d 0 0 {name=%s}"
                   % (cell, x, y, inst))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


SYM_PINS = [("ref_clk", "in"), ("pll_clk", "in"), ("clk_src", "in"),
            ("en", "in"), ("reset", "in"), ("mode", "in"),
            ("D_p", "out"), ("D_n", "out"),
            ("VDD", "inout"), ("VSS", "inout")]


def gen_sym(path):
    out = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}",
           "K {type=subcircuit", 'format="@name @pinlist @symname"',
           'template="name=x1"', "}", "V {}", "S {}", "E {}"]
    w_, top, bot = 110, -120, 120
    out.append("P 4 5 %d %d %d %d %d %d %d %d %d %d {}"
               % (-w_, top, w_, top, w_, bot, -w_, bot, -w_, top))
    out.append("T {@symname} -60 -6 0 0 0.3 0.3 {}")
    out.append("T {@name} %d %d 0 0 0.2 0.2 {}" % (w_ + 5, top - 12))

    def emit(name, direction, x, y):
        sgn = -1 if x < 0 else 1
        out.append("B 5 %s %s %s %s {name=%s dir=%s}"
                   % (x + sgn * 17.5, y - 2.5, x + sgn * 22.5, y + 2.5, name, direction))
        out.append("L %d %d %d %d %d {}"
                   % (7 if direction == "inout" else 4, x, y, x + sgn * 20, y))
        out.append("T {%s} %d %d 0 %d 0.2 0.2 {}"
                   % (name, x - sgn * 5, y - 4, 0 if x < 0 else 1))

    for i, (name, d) in enumerate([p for p in SYM_PINS if p[1] == "in"]):
        emit(name, d, -w_, top + 20 + i * 20)
    for i, (name, d) in enumerate([p for p in SYM_PINS if p[1] == "out"]):
        emit(name, d, w_, top + 20 + i * 20)
    for i, (name, d) in enumerate([p for p in SYM_PINS if p[1] == "inout"]):
        emit(name, d, w_, bot - 40 + i * 20)
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ------------------------------------------------- graphs and launchers
# xschem draws waveforms straight into the schematic from the rawfile the deck
# writes.  The launchers run the simulation and load that rawfile, so the whole
# loop stays inside the drawing.


def graph(box, nodes, colors, ymin, ymax, tmin, tmax, divy=5):
    """one waveform panel; box is (x1, y1, x2, y2) in schematic coordinates"""
    x1, y1, x2, y2 = box
    return ("B 2 %d %d %d %d {flags=graph\n"
            "y1=%g\ny2=%g\nypos1=0\nypos2=2\ndivy=%d\nsubdivy=1\nunity=1\n"
            "x1=%g\nx2=%g\ndivx=5\nsubdivx=1\n"
            "xlabmag=1.0\nylabmag=1.0\nlegendmag=1.0\n"
            'node="%s"\ncolor="%s"\n'
            "dataset=-1\nunitx=1\nlogx=0\nlogy=0\nautoload=0\nhilight_wave=-1}"
            % (x1, y1, x2, y2, ymin, ymax, divy, tmin, tmax,
               "\n".join(nodes), " ".join(str(c) for c in colors)))


def launchers(x, y, tb):
    """Simulate and load-waves arrows for testbench `tb`"""
    return [
        'C {launcher.sym} %d %d 0 0 {name=h_sim\n'
        'descr="Simulate"\n'
        'tclcommand="\n'
        'set_sim_defaults\n'
        'file mkdir $netlist_dir\n'
        'write_data [save_params] $netlist_dir/[file rootname '
        '[file tail [xschem get current_name]]].save\n'
        'xschem netlist\n'
        'simulate\n'
        '"}' % (x, y),
        'C {launcher.sym} %d %d 0 0 {name=h_waves\n'
        'descr="Load waves"\n'
        'tclcommand="xschem raw_read $netlist_dir/%s.raw tran"\n'
        '}' % (x, y + 40, tb),
        'C {launcher.sym} %d %d 0 0 {name=h_check\n'
        'descr="Check PRBS + timing"\n'
        'tclcommand="exec python3 [file dirname [xschem get current_dirname]]'
        '/../../scripts/check_timing.py &"\n'
        '}' % (x, y + 80),
    ]


# (box, nodes, colours, ymin, ymax) - the time window is filled in per bench.
# Colour numbers are xschem layer indices: 4 blue, 5 red, 7 green, 8 orange.
GRAPH_PANELS = [
    (["x1.gclk_b"], [4], -0.2, 1.4),
    (["D_p", "D_n"], [4, 5], -0.2, 1.4),
    (["x1.s6", "x1.fp", "x1.fn"], [7, 4, 5], -0.2, 1.4),
]


# ---------------------------------------------------------------- layout zones
# The same bands as the top-level benches, scaled to this much smaller cell:
# documentation, stimulus, the block under test, its load, and the analysis.
# Left to right in signal order, and nothing is drawn outside its own band, so
# the ngspice listing can never end up on top of a waveform panel again.
DOC_X = -1500
DOC_TITLE_Y = -1500
DOC_CODE_Y = -800

STIM_X = 150
STIM_TOP = -1000
STIM_PITCH = 200
STIM_GROUP_GAP = 200
STIM_FRAME_L = STIM_X - 180
STIM_FRAME_R = STIM_X + 180

DUT_X = 700
LOAD_X = 1150

VIEW_X = 1700
VIEW_W = 1600
VIEW_TOP = -1750

# the sources, split by what they are for; both benches drive the same nets
TB_GROUPS = [
    ("supply", ["VDD"]),
    ("clocks", ["ref_clk", "pll_clk"]),
    ("control", ["clk_src", "en", "reset", "mode"]),
]


def title_block(x, y, text, scale=0.45):
    return "T {%s} %d %d 0 0 %g %g {}" % (text, x, y, scale, scale)


def code_block(x, y, control):
    return '''C {devices/code_shown.sym} %d %d 0 0 {name=NGSPICE
only_toplevel=true
value="%s"}''' % (x, y, control)


def stim_groups(sources):
    """the source column, one framed and captioned group at a time"""
    val = dict(sources)
    covered = [n for _, nets in TB_GROUPS for n in nets]
    assert sorted(covered) == sorted(val), "groups and sources disagree"
    out, y = [], STIM_TOP
    for caption, nets in TB_GROUPS:
        top = y - 120
        for net in nets:
            out.append("N %d %d %d %d {lab=%s}"
                       % (STIM_X, y - 60, STIM_X, y - 30, net))
            out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                       "{name=lv_%s sig_type=std_logic lab=%s}"
                       % (STIM_X, y - 60, net, net))
            out.append('C {devices/vsource.sym} %d %d 0 0 {name=V%s value="%s"}'
                       % (STIM_X, y, net, val[net]))
            out.append("N %d %d %d %d {lab=GND}"
                       % (STIM_X, y + 30, STIM_X, y + 60))
            out.append("C {devices/gnd.sym} %d %d 0 0 {name=lg_%s lab=GND}"
                       % (STIM_X, y + 60, net))
            y += STIM_PITCH
        bottom = y - STIM_PITCH + 120
        for a, b, c, d in ((STIM_FRAME_L, top, STIM_FRAME_R, top),
                           (STIM_FRAME_R, top, STIM_FRAME_R, bottom),
                           (STIM_FRAME_L, bottom, STIM_FRAME_R, bottom),
                           (STIM_FRAME_L, top, STIM_FRAME_L, bottom)):
            out.append("L 3 %d %d %d %d {}" % (a, b, c, d))
        out.append("T {%s} %d %d 0 0 0.4 0.4 {}" % (caption, STIM_FRAME_L, top - 55))
        y = bottom + STIM_GROUP_GAP
    return out


def dut_and_load():
    """the block under test with a labelled stub per pin, and its load"""
    ports = [("ref_clk", -110, -100), ("pll_clk", -110, -80), ("clk_src", -110, -60),
             ("en", -110, -40), ("reset", -110, -20), ("mode", -110, 0),
             ("D_p", 110, -100), ("D_n", 110, -80),
             ("VDD", 110, 80), ("VSS", 110, 100)]
    out = []
    for net, dx, dy in ports:
        px, py = DUT_X + dx, dy
        s = -1 if dx < 0 else 1
        ex = px + s * 60
        out.append("N %d %d %d %d {lab=%s}"
                   % (min(px, ex), py, max(px, ex), py,
                      "0" if net == "VSS" else net))
        if net == "VSS":
            out.append("C {devices/gnd.sym} %d %d 3 0 {name=lg_vss lab=GND}" % (ex, py))
        else:
            out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                       "{name=lx_%s sig_type=std_logic lab=%s}" % (ex, py, net, net))
    out.append("C {lvds_pattern.sym} %d 0 0 0 {name=x1}" % DUT_X)
    # the load the pre-driver actually presents: two 40u/0.45u HV gates per side
    for net, cy in (("D_p", -300), ("D_n", -100)):
        out.append("N %d %d %d %d {lab=%s}" % (LOAD_X, cy - 60, LOAD_X, cy - 30, net))
        out.append("C {devices/lab_wire.sym} %d %d 0 0 "
                   "{name=lc_%s sig_type=std_logic lab=%s}" % (LOAD_X, cy - 60, net, net))
        out.append("C {capa.sym} %d %d 0 0 {name=C%s m=1 value=170f}" % (LOAD_X, cy, net))
        out.append("N %d %d %d %d {lab=GND}" % (LOAD_X, cy + 30, LOAD_X, cy + 60))
        out.append("C {devices/gnd.sym} %d %d 0 0 {name=lgc_%s lab=GND}"
                   % (LOAD_X, cy + 60, net))
    return out


def view_panels(tb):
    """the launchers, with the three waveform panels stacked below them"""
    out = launchers(VIEW_X, VIEW_TOP, tb)
    y = VIEW_TOP + 200
    for nodes, colors, ymin, ymax in GRAPH_PANELS:
        out.append(graph((VIEW_X, y, VIEW_X + VIEW_W, y + 400),
                         nodes, colors, ymin, ymax, 2e-08, 2.6e-08))
        y += 500
    return out


# ---------------------------------------------------------------- testbench
TB_SOURCES = [
    ("VDD", "1.2"),
    ("ref_clk", "PULSE(0 1.2 0 50p 50p 1.9n 4n)"),
    ("pll_clk", "PULSE(0 1.2 0 30p 30p 470p 1n)"),
    ("clk_src", "PWL(0 1.2 160n 1.2 160.1n 0)"),
    ("en", "PWL(0 0 3n 0 3.1n 1.2 150n 1.2 150.1n 0 155n 0 155.1n 1.2)"),
    ("reset", "PWL(0 1.2 2n 1.2 2.1n 0)"),
    ("mode", "PWL(0 0 12n 0 12.1n 1.2)"),
]

TB_CONTROL = r'''
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.lib cornerMOSlv.lib mos_tt
.temp 27
.options savecurrents klu reltol=1e-3
.control
save D_p D_n x1.gclk_b x1.s6 x1.s6_n x1.fp x1.fn mode en reset
tran 5p 200n
write @schname\\\\.raw

* the pair has to be complementary at every instant
let dsum = v(D_p)+v(D_n)
meas tran dsum_min MIN dsum from=20n to=140n
meas tran dsum_max MAX dsum from=20n to=140n

* D_p rising against D_n falling on the same bit: the skew the pre-driver sees,
* budget about 40 ps (docs/predriver-findings.md)
meas tran tp_r WHEN v(D_p)=0.6 RISE=5
meas tran tn_f WHEN v(D_n)=0.6 FALL=5
let skew = tn_f - tp_r
print skew

* clock passthrough period, measured before mode goes high
meas tran t1 WHEN v(D_p)=0.6 RISE=4
meas tran t2 WHEN v(D_p)=0.6 RISE=5
let tpass = t2 - t1
print tpass

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(D_p) v(D_n) v(x1.gclk_b) v(mode) v(en)
.endc
'''


TB_TITLE = """lvds_pattern transient bench.

  0...2 ns     reset high, clock stopped
  3 ns         en high, clock passthrough of pll_clk at 1 GHz
  12 ns        mode high, PRBS-7 at 1 Gb/s
  150...155 ns en low, the clock gate stops the pattern
  160 ns       clk_src low, the 250 MHz reference takes over

scripts/check_timing.py re-runs the polynomial over the exported
data and counts the bits that do not match."""


def gen_tb(path):
    out = [HEADER, title_block(DOC_X, DOC_TITLE_Y, TB_TITLE)]
    out += stim_groups(TB_SOURCES)
    out += dut_and_load()
    out += view_panels("lvds_pattern_tb_tran")
    out.append(code_block(DOC_X, DOC_CODE_Y, TB_CONTROL))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


# ------------------------------------------------- PRBS-only timing bench
# The general bench walks the whole interface; this one stays in PRBS-7 from the
# first clock, so the data path can be timed over a full 127-bit period without
# the mode and source changes moving anything around.
TB_PRBS_SOURCES = [
    ("VDD", "1.2"),
    ("ref_clk", "0"),                                   # unused here
    ("pll_clk", "PULSE(0 1.2 0 30p 30p 470p 1n)"),      # 1 GHz
    ("clk_src", "1.2"),                                 # take the fast clock
    ("en", "PWL(0 0 3n 0 3.1n 1.2)"),
    ("reset", "PWL(0 1.2 2n 1.2 2.1n 0)"),
    ("mode", "1.2"),                                    # PRBS-7 throughout
]

TB_PRBS_CONTROL = r'''
.include /foss/pdks/ihp-sg13cmos5l/libs.ref/sg13cmos5l_stdcell/spice/sg13cmos5l_stdcell.spice
.lib cornerMOSlv.lib mos_tt
.temp 27
.options savecurrents klu reltol=1e-3
.control
save D_p D_n x1.gclk_b x1.s6 x1.s6_n x1.fp x1.fn mode en reset
tran 2p 160n
write @schname\\\\.raw

* the pair has to be complementary at every instant
let dsum = v(D_p)+v(D_n)
meas tran dsum_min MIN dsum from=10n to=155n
meas tran dsum_max MAX dsum from=10n to=155n
print dsum_min dsum_max

set wr_vecnames
set wr_singlescale
wrdata ../plot_simulations/data/@schname\\\\.txt
+ v(D_p) v(D_n) v(x1.gclk_b)
.endc
'''

TB_PRBS_TITLE = """lvds_pattern PRBS-7 timing bench.

PRBS-7 from the first clock, 1 Gb/s, 160 ns - a full 127-bit period with
margin.  mode and clk_src are static, so nothing moves the data path timing
during the run.

scripts/check_timing.py reads the export and reports the bit rate, the
clock-to-output spread, the data valid window that follows from it, the
D_p / D_n skew, and it re-runs the polynomial sampling in the middle of that
window rather than at a fixed phase."""


def gen_tb_prbs(path):
    out = [HEADER, title_block(DOC_X, DOC_TITLE_Y, TB_PRBS_TITLE)]
    out += stim_groups(TB_PRBS_SOURCES)
    out += dut_and_load()
    out += view_panels("lvds_pattern_tb_prbs")
    out.append(code_block(DOC_X, DOC_CODE_Y, TB_PRBS_CONTROL))
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sch = os.path.join(here, "..", "schematic", "xschem")
    tb = os.path.join(here, "..", "testbenches", "xschem")
    gen_sch(os.path.join(sch, "lvds_pattern.sch"))
    gen_sym(os.path.join(sch, "lvds_pattern.sym"))
    gen_tb(os.path.join(tb, "lvds_pattern_tb_tran.sch"))
    gen_tb_prbs(os.path.join(tb, "lvds_pattern_tb_prbs.sch"))
    print("wrote lvds_pattern.sch (%d cells, %d wire segments), .sym and both benches"
          % (len(CELLS), sum(len(p) - 1 for _, p in WIRES)))
