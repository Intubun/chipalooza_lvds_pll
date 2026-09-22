#!/usr/bin/env python3
"""Read the hierarchy of `lvds_tx.sch` out of its SPICE netlist.

The device table is not transcribed by hand: `netlist/schematic/lvds_tx.spice`
is regenerated from the schematic by `run_all.sh` and parsed here, so the
layout cannot silently drift away from the schematic it is built from.

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
NETLIST = os.path.join(HERE, "..", "netlist", "schematic", "lvds_tx.spice")

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
# Mp1 and Mp2 are the two halves of one mirror, so they are built from the
# same cell: matching wants identical geometry, down to the gate contacts.
GENCELL_OVERRIDES = {
    # polycov 85 instead of the 50 the long-channel rule applies: it
    # widens the gate contact bar and takes the cuts per finger from 3 to
    # 5, at no area cost.  The count steps rather than scales -- 60 gives
    # 3, 65..80 give 4, 85..95 give 5, 100 gives 6 -- so 85 is the
    # cheapest way to five.  What it costs is the corridor between the
    # gate pads, which is why the value is here and not in the global
    # rule.  _keepname holds the cell name so the placement above and the
    # cell swap into lvds_tx.gds still work.
    ("iref_x15", "Mp1"): {"botc": 0, "_open": "n", "polycov": 85,
                          "_keepname": "dev_p_w8_l2_ng6_openn_botc0"},
    ("iref_x15", "Mp2"): {"botc": 0, "_open": "n", "polycov": 85,
                          "_keepname": "dev_p_w8_l2_ng6_openn_botc0"},
    # gate contacted from the top only, like the two pmos; the cell is used
    # by Mn2 alone, so the name can stay and the placement above holds
    # viagate 50, not 100: the via landing pad on metal1 is what sets the
    # gap between the gate contacts, and at 100 it is 1.88 um wide, leaving
    # 0.14 um between packets -- under the 0.16 um a metal1 wire needs, so
    # source cannot reach the guard ring.  At 50 the pad is 0.99 um and the
    # gap 1.39 um, and the gate still reaches metal2.  60 rather than 50
    # because the cut count per gate steps 2 -> 3 there; the pad grows to
    # 1.17 um and the gap falls to 1.21 um, still far more than a wire
    # needs.  70 and 80 also give 3 cuts but only take corridor away.
    ("iref_x15", "Mn2"): {"botc": 0, "viagate": 60, "_keepname": True},
    # gate brought up to metal2 (the rest of the block stops on metal1);
    # single user, so the name can stay
    ("iref_x15", "Mn1"): {"viagate": 100, "viadrn": 100, "_keepname": True},
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
        self.opts = dict(GENCELL_OVERRIDES.get((parent, base or name), {}))
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
    return subckts


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
