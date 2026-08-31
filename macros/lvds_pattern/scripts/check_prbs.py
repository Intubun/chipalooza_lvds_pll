#!/usr/bin/env python3
"""Re-run the PRBS-7 polynomial over the transient data and count mismatches.

Reads the wrdata export of lvds_pattern_tb_tran, samples D_p on every rising
edge of the internal gated clock, and checks that the sampled stream obeys
b[k] = b[k-7] xor b[k-6] - the same self-reference serdes/check_link.py uses on
the analog side, and the reason the hand-built LFSR has to match serdes_dig.v
bit for bit rather than merely be *a* PRBS-7.

Also checks that D_n is the complement of D_p at every sample, and reports the
worst D_p/D_n edge skew, which is the number the pre-driver cares about.
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
        rows = []
        for line in fh:
            parts = line.split()
            if len(parts) == len(header):
                rows.append([float(p) for p in parts])
    return header, rows


def col(header, name):
    for i, h in enumerate(header):
        if h.lower() == name.lower():
            return i
    raise SystemExit("column %s not in %s" % (name, header))


def crossings(t, v, rising):
    """times where v crosses TH, linearly interpolated"""
    out = []
    for i in range(1, len(v)):
        a, b = v[i - 1], v[i]
        if rising and a < TH <= b:
            out.append(t[i - 1] + (TH - a) * (t[i] - t[i - 1]) / (b - a))
        elif not rising and a > TH >= b:
            out.append(t[i - 1] + (TH - a) * (t[i] - t[i - 1]) / (b - a))
    return out


def sample(t, v, when):
    """value of v at time `when`, nearest sample"""
    lo, hi = 0, len(t) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if t[mid] < when:
            lo = mid + 1
        else:
            hi = mid
    return v[lo]


def main(path, prbs_from, prbs_to):
    header, rows = read_columns(path)
    it = 0
    idp, idn = col(header, "v(d_p)"), col(header, "v(d_n)")
    iclk = col(header, "v(x1.gclk_b)")

    t = [r[it] for r in rows]
    dp = [r[idp] for r in rows]
    dn = [r[idn] for r in rows]
    clk = [r[iclk] for r in rows]

    # sample D_p in the middle of each bit: one clock edge sets it, the next
    # replaces it, so half a period after the edge is the safe point
    edges = [e for e in crossings(t, clk, True) if prbs_from <= e <= prbs_to]
    if len(edges) < 3 * TAP_A:
        raise SystemExit("only %d clock edges in the PRBS window" % len(edges))
    period = (edges[-1] - edges[0]) / (len(edges) - 1)

    bits, comp_err = [], 0
    for e in edges:
        at = e + 0.5 * period
        if at > t[-1]:
            break
        p = 1 if sample(t, dp, at) > TH else 0
        n = 1 if sample(t, dn, at) > TH else 0
        if p == n:
            comp_err += 1
        bits.append(p)

    errors = 0
    for k in range(TAP_A, len(bits)):
        if bits[k] != (bits[k - TAP_A] ^ bits[k - TAP_B]):
            errors += 1
    checked = max(0, len(bits) - TAP_A)

    # worst edge skew: D_p rising against the nearest D_n falling and vice versa
    ups, downs = crossings(t, dp, True), crossings(t, dn, False)
    worst = 0.0
    for u in ups:
        if not (prbs_from <= u <= prbs_to):
            continue
        near = min(downs, key=lambda d: abs(d - u))
        worst = max(worst, abs(near - u))

    print("bit rate            %.3f Gb/s" % (1e-9 / period))
    print("bits sampled        %d" % len(bits))
    print("PRBS-7 mismatches   %d of %d checked" % (errors, checked))
    print("non-complementary   %d samples" % comp_err)
    print("worst D_p/D_n skew  %.1f ps" % (worst * 1e12))
    if errors or comp_err:
        return 1
    print("PASS: stream obeys x^7 + x^6 + 1 and the pair stays complementary")
    return 0


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    default = os.path.join(here, "..", "testbenches", "xschem",
                           "plot_simulations", "data",
                           "lvds_pattern_tb_tran.txt")
    data = sys.argv[1] if len(sys.argv) > 1 else default
    # the PRBS window of the bench: mode goes high at 12 ns, en drops at 150 ns
    lo = float(sys.argv[2]) if len(sys.argv) > 2 else 14e-9
    hi = float(sys.argv[3]) if len(sys.argv) > 3 else 149e-9
    sys.exit(main(data, lo, hi))
