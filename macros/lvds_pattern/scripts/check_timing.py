#!/usr/bin/env python3
"""Time the PRBS data path against its own clock, then check the sequence.

Sampling at a fixed phase - half a bit after the clock edge - only works while
the clock-to-output delay is small compared to the bit period, and here it is not.
This script measures that delay instead of assuming it: for every clock edge it
finds the data transition that edge caused, and the spread of those delays is
what closes the data valid window. It then samples in the middle of the measured
window rather than at a fixed phase, and only then checks

    b[k] = b[k-7] xor b[k-6]

the same self-reference serdes/check_link.py uses on the analog side.
"""
import io
import os
import sys

VDD = 1.2
TH = VDD / 2.0
TAP_A, TAP_B = 7, 6          # x^7 + x^6 + 1


def read_columns(path):
    with io.open(path, encoding="utf-8") as fh:
        header = fh.readline().split()
        rows = [[float(v) for v in line.split()]
                for line in fh if len(line.split()) == len(header)]
    return header, rows


def col(header, name):
    for i, h in enumerate(header):
        if h.lower() == name.lower():
            return i
    raise SystemExit("column %s not in %s" % (name, header))


def crossings(t, v, rising=None):
    """times where v crosses TH, linearly interpolated; rising=None gives both"""
    out = []
    for i in range(1, len(v)):
        a, b = v[i - 1], v[i]
        up = a < TH <= b
        dn = a > TH >= b
        if (rising is True and up) or (rising is False and dn) or \
           (rising is None and (up or dn)):
            out.append((t[i - 1] + (TH - a) * (t[i] - t[i - 1]) / (b - a), up))
    return out


def sample(t, v, when):
    lo, hi = 0, len(t) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if t[mid] < when:
            lo = mid + 1
        else:
            hi = mid
    return v[lo]


def main(path, t_from, t_to):
    header, rows = read_columns(path)
    t = [r[0] for r in rows]
    dp = [r[col(header, "v(d_p)")] for r in rows]
    dn = [r[col(header, "v(d_n)")] for r in rows]
    clk = [r[col(header, "v(x1.gclk_b)")] for r in rows]

    edges = [c for c, _ in crossings(t, clk, True) if t_from <= c <= t_to]
    if len(edges) < 3 * TAP_A:
        raise SystemExit("only %d clock edges in the window" % len(edges))
    period = (edges[-1] - edges[0]) / (len(edges) - 1)

    # clock to output: for each edge, the data transition it caused, i.e. the
    # first D_p crossing after it and before the next edge
    dp_edges = [c for c, _ in crossings(t, dp)]
    tco = []
    for e in edges:
        nxt = [c for c in dp_edges if e < c < e + period]
        if nxt:
            tco.append(nxt[0] - e)
    if not tco:
        raise SystemExit("D_p never transitions - is the clock reaching the block?")
    tco_min, tco_max = min(tco), max(tco)

    # the data is valid from the last transition until the next edge causes one
    valid_from, valid_to = tco_max, period + tco_min
    centre = 0.5 * (valid_from + valid_to)

    bits, comp_err = [], 0
    for e in edges:
        at = e + centre
        if at > t[-1]:
            break
        p = 1 if sample(t, dp, at) > TH else 0
        n = 1 if sample(t, dn, at) > TH else 0
        if p == n:
            comp_err += 1
        bits.append(p)

    errors = sum(1 for k in range(TAP_A, len(bits))
                 if bits[k] != (bits[k - TAP_A] ^ bits[k - TAP_B]))
    checked = max(0, len(bits) - TAP_A)

    # D_p rising against the D_n falling it pairs with, and vice versa
    dn_edges = [c for c, _ in crossings(t, dn)]
    worst = 0.0
    for c, _ in crossings(t, dp):
        if not (t_from <= c <= t_to):
            continue
        worst = max(worst, min(abs(d - c) for d in dn_edges))

    ns = 1e9
    print("bit rate             %.3f Gb/s" % (1e-9 / period))
    print("clock to output      %.1f ... %.1f ps  (spread %.1f ps)"
          % (tco_min * 1e12, tco_max * 1e12, (tco_max - tco_min) * 1e12))
    print("data valid window    %.3f ... %.3f ns after the edge, %.1f%% of a UI"
          % (valid_from * ns, valid_to * ns, 100 * (valid_to - valid_from) / period))
    print("sampled at           %.3f ns after the edge" % (centre * ns))
    print("bits sampled         %d" % len(bits))
    print("PRBS-7 mismatches    %d of %d checked" % (errors, checked))
    print("non-complementary    %d samples" % comp_err)
    print("worst D_p/D_n skew   %.1f ps" % (worst * 1e12))
    if errors or comp_err:
        return 1
    print("PASS: sequence obeys x^7 + x^6 + 1 and the pair stays complementary")
    return 0


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.join(here, "..", "testbenches", "xschem",
                           "plot_simulations", "data",
                           "lvds_pattern_tb_prbs.txt")
    data = sys.argv[1] if len(sys.argv) > 1 else default
    lo = float(sys.argv[2]) if len(sys.argv) > 2 else 10e-9
    hi = float(sys.argv[3]) if len(sys.argv) > 3 else 155e-9
    sys.exit(main(data, lo, hi))
