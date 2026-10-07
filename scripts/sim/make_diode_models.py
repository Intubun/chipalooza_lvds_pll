#!/usr/bin/env python3
"""Write models/diodes_tt0.lib: the PDK's diode library with tt = 0.

The antenna diodes of sg13cmos5l (dantenna, dpantenna - in antennanp, and in
the pad cells' DCN/DCP diodes and secondary protection) stall an ngspice
transient: as soon as a node they sit on moves, the step size collapses to
~1e-14 s and a 10 ns run does not finish in five minutes.  It takes all three
of the breakdown parameters (bv/ibv/nbv), the 700 ns transit time and the
100 kohm-scale series resistance; drop any one and the same deck runs in 0.1 s.

tt only shapes the stored charge in forward conduction, and these diodes are
reverse biased in operation - the PDK says so itself ("model is designed for
reverse direction of the diodes").  So the benches use this copy, identical but
for tt = 0, in place of `.lib cornerDIO.lib dio_tt`; junction capacitance,
leakage and breakdown are untouched.

    python3 scripts/sim/make_diode_models.py        # in the container
"""
import os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SRC = os.path.join(os.environ["PDK_ROOT"], os.environ["PDK"], "libs.tech/ngspice/models/diodes.lib")
OUT = os.path.join(ROOT, "models", "diodes_tt0.lib")

text = open(SRC).read()
out, n = [], 0
for line in text.split("\n"):
    if line.lstrip().lower().startswith(".model"):
        line, k = re.subn(r"(?i)\btt\s*=\s*[-+0-9.eE]+", "tt=0", line)
        n += k
    out.append(line)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
head = ("* models/diodes_tt0.lib - written by scripts/sim/make_diode_models.py from\n"
        "* $PDK_ROOT/$PDK/libs.tech/ngspice/models/diodes.lib (IHP, Apache 2.0),\n"
        "* identical but for tt = 0 in every .model (%d of them).  Why: see the script.\n"
        "* Use it in place of `.lib cornerDIO.lib dio_tt`, together with\n"
        "* `.include sg13g2_esd.lib`, which that corner also pulls in.\n\n" % n)
open(OUT, "w").write(head + "\n".join(out))
print("geschrieben: %s (%d tt auf 0)" % (os.path.relpath(OUT, ROOT), n))
