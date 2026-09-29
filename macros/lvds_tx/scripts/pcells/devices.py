#!/usr/bin/env python3
"""Read the hierarchy of `lvds_tx.sch` out of its SPICE netlist.

The device table is not transcribed by hand: `netlist/schematic/lvds_tx.spice`
is regenerated from the schematic by `update_pcells.sh` and parsed here, so
the device cells cannot silently drift away from the schematic.

Two conversions happen on the way in:

* the schematic writes `w` as the *total* width and `ng` as the finger count,
  while magic's gencell wants the width *per finger* -- so `w/ng` is stored;
* `m=<n>` on a MOSFET becomes `n` separate instances.  gencell's own `m`
  stacks rows without strapping their gates, so the blocks have to be
  instantiated individually anyway (the same reason the driver's `M6` is four
  instances rather than one `m=4` device).
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NETLIST = os.path.join(HERE, "..", "..", "netlist", "schematic",
                       "lvds_tx.spice")

MOS_MODELS = {"sg13_hv_nmos", "sg13_hv_pmos", "sg13_lv_nmos", "sg13_lv_pmos"}

# Per-device gencell options, keyed by (subcircuit, instance name).  A device
# is otherwise described entirely by its geometry, so an override has to make
# the cell name unique too: two devices of the same w/l/ng but different
# gencell options are different cells.
#
# botc 0 drops the lower of the two poly contact rows the generator puts on
# every gate.  The generator then pulls the guard ring 0.19 um closer to the
# FET, which breaks pSD.i1/pSD.d1 (0.43 um pFET-to-tap), so `patch_cells.py`
# pushes that side of the ring back out.  The cell ends up the size it was:
# this buys a gate that is only contacted from the top, not area.
#
# Keys starting with "_" are not gencell parameters -- the generator has no
# option for them -- but instructions to `patch_cells.py`, applied after the
# cell is built.  They still belong here because they change the cell, and
# so have to change its name:
#
#   _open <side>   cut the guard ring open on that side ("n" or "s"), so the
#                  gate can leave the cell without crossing a tap ring.
#   _keepname      apply the other keys without letting them into the cell
#                  name.  True means the bare geometric name; a string
#                  pins that exact name, which is what a cell already
#                  carrying a suffix needs -- otherwise adding an option
#                  would strip the suffix too and the hierarchy above
#                  would point at a name that no longer exists.  The
#                  suffix exists to keep two different geometries apart, so
#                  it is unnecessary when a geometry has a single user -- and
#                  leaving the name alone is what lets one device change
#                  without invalidating the placement above it.
#                  `unique_devices` refuses it if the name is not unique.
#
# The iref_x15 pre-mirror used to be the one user of these options; it is
# its own macro now (macros/iref_x15, routed by hand), and its README keeps
# the options its leaf cells were built with.
#
# MRef is the one long-channel device (l = 2 um) that keeps a gate rail:
# at l >= 2 um the flow gives every device one contact per finger
# (gen_devices.py: INDIVIDUAL_GATES), which a single-finger diode has no use
# for; its gate is reached on its metal2 rail like every other short-channel
# device's.  Its geometry is unique, so the bare name stays.
#
# The comparator's tail Mt stands right under its input pair Mid|Mio, finger
# on finger (same l, same count: two halves of six under the pair's two
# sixes), so that each of Mt's drains runs straight up in metal1 into the
# pair source above it -- net2 without metal2 or metal3.  For that nothing
# may lie between the two rows: Mt is contacted at the bottom only and its
# ring is open at the top, the pair contacted at the top only with its ring
# open at the bottom.  Placed 1.56 um into each other, the two open rings
# meet and form one (docs/layout.md, *Placing by hand*).
GENCELL_OVERRIDES = {
    ("predriver", "Mref"): {"conn_gates": 1, "polycov": 100, "viagate": 100,
                            "_keepname": True},
    ("predriver_comp", "Mt"): {"topc": 0, "_open": "n"},
    ("predriver_comp", "Mid"): {"botc": 0, "_open": "s"},
    ("predriver_comp", "Mio"): {"botc": 0, "_open": "s"},
    # The comparator load (Mld|Mlo in one cell) is contacted at the bottom
    # only, where its diode and net1 are: with no gate rail on top, its
    # sources run straight up into the guard ring (Va) in metal1.
    ("predriver_comp", "Mldo"): {"topc": 0},
}
# Options for every device of a subcircuit; GENCELL_OVERRIDES still wins.
#
# predriver_stage is built like a row of standard cells: no guard ring per
# device, the PMOS row in one common NWell with an ntap strip along its Va
# edge, the NMOS row with a ptap strip along its Vss edge -- both drawn in
# the stage cell itself, not here.  Sixteen small devices had sixteen rings,
# and each ring was a metal1 wall between the columns.  With `guard 0` a
# cell has no B terminal: its bulk is the well or the substrate, tied by
# the strips.
SUBCKT_OVERRIDES = {
    "predriver_stage": {"guard": 0},
}
# ... and per model within a subcircuit.  In the stage every gate is
# contacted on the inner side only, the one facing the other row: PMOS
# (bottom row) on top, NMOS (top row) at the bottom.  The outer side then
# has no gate rail, and the source stripes run straight into the Va/Vss
# strip in metal1.
MODEL_OVERRIDES = {
    ("predriver_stage", "sg13_hv_pmos"): {"botc": 0},
    ("predriver_stage", "sg13_hv_nmos"): {"topc": 0},
}
# Transistors drawn as ONE multi-finger cell, in one guard ring, although
# the schematic has them apart.  Only for devices that share gate, source
# and bulk and have the same finger: their fingers then differ in nothing
# but which drain stripe they sit on, and one cell has one gate rail running
# through all of them in metal1 -- no guard ring between two gates on the
# same net (the point: gates on metal1, not on a metal2 bridge over a ring).
#
# `drains` says which member each drain stripe belongs to, left to right,
# one letter per member in the order given: the cell's even stripes (the
# generator's "D") are the shared source, its odd stripes the drains, each
# drain stripe between two fingers.  LVS extracts every finger and adds up
# those on the same nets, so it still finds the schematic's devices.
#
#   Mld|Mlo  the comparator's mirror load: gate net1, source Va.  ABBA puts
#            the two halves of the mirror on a common centroid.
MERGED = {
    ("predriver_comp", "Mldo"): {"members": ("Mld", "Mlo"), "drains": "ABBA"},
}
RES_MODELS = {"rhigh", "rsil", "rppd"}
CAP_MODELS = {"cap_cmomf"}

# SPICE suffixes -> microns.  A bare number is metres, as everywhere in SPICE.
_SUFFIX = {"": 1e6, "m": 1e3, "u": 1.0, "n": 1e-3, "p": 1e-6, "f": 1e-9,
           "k": 1e9, "meg": 1e12}


def _um(text):
    """'97.2u' -> 97.2 (microns)."""
    m = re.fullmatch(r"([-+0-9.eE]+)\s*([a-zA-Z]*)", text.strip())
    if not m:
        raise ValueError("cannot parse value %r" % text)
    value, suffix = float(m.group(1)), m.group(2).lower()
    # 'u' in '1u' is microns; a trailing 'F'/'ohm' style unit is noise
    for unit in ("ohm", "f", "s"):
        if suffix.endswith(unit) and suffix != unit:
            suffix = suffix[: -len(unit)]
    if suffix not in _SUFFIX:
        suffix = ""
    return value * _SUFFIX[suffix]


def _tag(value):
    """5.913 -> '5p913', 2.0 -> '2' -- a float that is legal in a cell name."""
    text = ("%g" % value)
    return text.replace(".", "p").replace("-", "m")


class Device:
    """One primitive: a MOSFET, a resistor or a capacitor."""

    def __init__(self, name, model, nets, params, parent=None, base=None):
        self.name = name
        self.model = model
        self.nets = nets
        self.params = params
        self.parent = parent
        # `base` is the instance name before an m>1 expansion, which is what
        # an override is written against.
        self.opts = dict(SUBCKT_OVERRIDES.get(parent, {}))
        self.opts.update(MODEL_OVERRIDES.get((parent, model), {}))
        self.opts.update(GENCELL_OVERRIDES.get((parent, base or name), {}))
        if model in MOS_MODELS:
            self.kind = "mos"
            self.ng = int(params.get("ng", 1))
            self.w = _um(params["w"]) / self.ng      # per finger
            self.l = _um(params["l"])
        elif model in RES_MODELS:
            self.kind = "res"
            self.ng = 1
            self.w = _um(params["w"])
            self.l = _um(params["l"])
        elif model in CAP_MODELS:
            self.kind = "cap"
            self.ng = 1
            self.w = _um(params["w"])
            self.l = _um(params["l"])
        else:
            raise ValueError("unknown primitive model %r" % model)

    @property
    def cellname(self):
        keep = self.opts.get("_keepname")
        if isinstance(keep, str):
            return keep
        if keep:
            suffix = ""
        else:
            suffix = "".join("_%s%s" % (k.lstrip("_"), v)
                             for k, v in sorted(self.opts.items()))
        if self.kind == "mos":
            short = "n" if "nmos" in self.model else "p"
            return "dev_%s_w%s_l%s_ng%d%s" % (short, _tag(self.w), _tag(self.l),
                                              self.ng, suffix)
        return "dev_%s_w%s_l%s%s" % (self.model, _tag(self.w), _tag(self.l),
                                     suffix)

    def __repr__(self):
        return "<Device %s %s>" % (self.name, self.cellname)


class Instance:
    """One instance of another subcircuit."""

    def __init__(self, name, cell, nets):
        self.name = name
        self.cell = cell
        self.nets = nets

    def __repr__(self):
        return "<Instance %s of %s>" % (self.name, self.cell)


class Subckt:
    def __init__(self, name, ports):
        self.name = name
        self.ports = ports
        self.devices = []
        self.instances = []

    @property
    def children(self):
        """Child cell names, devices and subcircuits alike, in netlist order."""
        return ([d.cellname for d in self.devices]
                + [i.cell for i in self.instances])

    def __repr__(self):
        return "<Subckt %s: %d devices, %d instances>" % (
            self.name, len(self.devices), len(self.instances))


def _split_params(tokens):
    """Split a trailing run of key=value tokens off an instance line."""
    params = {}
    while tokens and "=" in tokens[-1]:
        key, _, value = tokens.pop().partition("=")
        params[key.lower()] = value
    return params


def parse(path=NETLIST):
    """Read the netlist into {subckt name: Subckt}."""
    with open(path) as fh:
        raw = fh.read()
    # fold SPICE continuation lines before anything else looks at them
    raw = re.sub(r"\n\+\s*", " ", raw)

    subckts = {}
    current = None
    for line in raw.splitlines():
        line = line.split("$")[0].strip()
        if not line or line.startswith("*"):
            continue
        low = line.lower()
        if low.startswith(".subckt"):
            tokens = line.split()
            current = Subckt(tokens[1], tokens[2:])
            subckts[current.name] = current
            continue
        if low.startswith(".ends"):
            current = None
            continue
        if current is None or not low.startswith("x"):
            continue

        tokens = line.split()
        name = tokens[0][1:]                 # strip the SPICE 'X'
        params = _split_params(tokens)
        model = tokens[-1]
        nets = tokens[1:-1]

        if model in MOS_MODELS | RES_MODELS | CAP_MODELS:
            mult = int(float(params.get("m", 1)))
            if model in MOS_MODELS and mult > 1:
                # gencell does not strap gates between rows of an m>1 device,
                # so the blocks become separate instances here.
                for i in range(mult):
                    current.devices.append(
                        Device("%s_%d" % (name, i), model, nets, params,
                               current.name, name))
            else:
                current.devices.append(
                    Device(name, model, nets, params, current.name))
        else:
            current.instances.append(Instance(name, model, nets))
    for (sub, name), spec in MERGED.items():
        if sub in subckts:
            _merge(subckts[sub], name, spec)
    return subckts


def _merge(sub, name, spec):
    """Replace the members of a MERGED group by one Device of all their
    fingers, where the first member stood."""
    members = [next((d for d in sub.devices if d.name == m), None)
               for m in spec["members"]]
    if None in members:
        raise SystemExit("%s: MERGED %s names a device that is not there"
                         % (sub.name, name))
    first = members[0]
    for d in members[1:]:
        same = (d.model == first.model and abs(d.w - first.w) < 1e-6
                and abs(d.l - first.l) < 1e-6 and d.nets[1:] == first.nets[1:])
        if not same:
            raise SystemExit("%s: %s and %s cannot share one cell -- model, "
                             "finger, gate, source and bulk must all be equal"
                             % (sub.name, first.name, d.name))
    letters = "ABCDEFGH"[:len(members)]
    for letter, d in zip(letters, members):
        if spec["drains"].count(letter) * 2 != d.ng:
            raise SystemExit("%s: %s has %d fingers, `drains` gives it %d"
                             % (sub.name, d.name, d.ng,
                                spec["drains"].count(letter) * 2))
    ng = sum(d.ng for d in members)
    params = dict(first.params, ng=str(ng), w="%gu" % (first.w * ng))
    merged = Device(name, first.model, ["|".join(d.nets[0] for d in members)]
                    + first.nets[1:], params, sub.name)
    merged.members = [(d.name, d.nets[0]) for d in members]
    merged.drains = [members[letters.index(c)].name for c in spec["drains"]]
    at = sub.devices.index(first)
    sub.devices = [d for d in sub.devices if d not in members]
    sub.devices.insert(at, merged)


def build_order(subckts, top):
    """Subcircuit names bottom-up, so a cell is always built after its children."""
    order, seen = [], set()

    def visit(name):
        if name in seen or name not in subckts:
            return
        seen.add(name)
        for inst in subckts[name].instances:
            visit(inst.cell)
        order.append(name)

    visit(top)
    return order


def unique_devices(subckts):
    """One representative Device per distinct leaf cell, by cell name."""
    cells = {}
    for sub in subckts.values():
        for dev in sub.devices:
            seen = cells.get(dev.cellname)
            if seen is None:
                cells[dev.cellname] = dev
            elif seen.opts != dev.opts:
                raise SystemExit(
                    "%s would be two different cells: %s wants %s, %s wants %s"
                    % (dev.cellname, seen.name, seen.opts or "the defaults",
                       dev.name, dev.opts or "the defaults"))
    return dict(sorted(cells.items()))


if __name__ == "__main__":
    subs = parse()
    for name in build_order(subs, "lvds_tx"):
        sub = subs[name]
        print("%-16s %2d devices  %2d instances  ports: %s"
              % (name, len(sub.devices), len(sub.instances),
                 " ".join(sub.ports)))
    print("\n%d distinct leaf cells:" % len(unique_devices(subs)))
    for cellname, dev in unique_devices(subs).items():
        print("  %-28s %s w=%g l=%g ng=%d"
              % (cellname, dev.model, dev.w, dev.l, dev.ng))
