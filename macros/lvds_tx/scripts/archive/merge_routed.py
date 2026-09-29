#!/usr/bin/env python3
"""The generator's placement with the hand-routed cells put back in.

    python3 merge_routed.py          -> lvds_tx_merged.gds

lvds_tx_gen.gds has the current placement but only the generator's copy of
the cells in ROUTED: the same devices in the same arrangement, without the
wiring.  This writes a third file that takes those cells -- and every cell
below them -- verbatim from lvds_tx.gds, so the result is the new placement
with the routing that already exists.

Neither input is written.  lvds_tx_merged.gds becoming the working file is a
copy the user makes.

The generator shifts a routed cell's devices so that they start at its
margin, so its copy does not share an origin with the original.  The shift
is measured from the devices themselves and put into every instance of the
cell, which puts the original exactly where the generator placed its copy
without touching the cell.
"""
import os
import sys

import klayout.db as kdb

from build_placement import ROUTED

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "lvds_tx_gen.gds")
USER = os.path.join(HERE, "lvds_tx.gds")
OUT = os.path.join(HERE, "lvds_tx_merged.gds")


def centres(cell):
    """{instance name: centre of its bbox} over a cell's child instances."""
    out = {}
    for inst in cell.each_inst():
        box = inst.bbox()
        out[inst.property(61)] = ((box.left + box.right) // 2,
                                  (box.bottom + box.top) // 2)
    return out


def shift_between(gen_cell, user_cell):
    """The translation that takes the original's devices onto the copy's."""
    gen, user = centres(gen_cell), centres(user_cell)
    if set(gen) != set(user):
        raise SystemExit("%s: instances differ -- generator %s, lvds_tx.gds %s"
                         % (gen_cell.name, sorted(gen), sorted(user)))
    shifts = {(gen[n][0] - user[n][0], gen[n][1] - user[n][1]) for n in gen}
    if len(shifts) != 1:
        raise SystemExit("%s: devices are not arranged alike in both files "
                         "(%s) -- run make_floorplan.py again"
                         % (gen_cell.name, sorted(shifts)))
    return shifts.pop()


def fingerprint(layout, cell):
    """Everything a cell is made of, for proving two copies identical."""
    shapes = {}
    for li in layout.layer_indexes():
        info = layout.get_info(li)
        texts = sorted(str(s.text) for s in cell.shapes(li).each()
                       if s.is_text())
        polys = kdb.Region(cell.shapes(li))
        if not polys.is_empty() or texts:
            shapes[(info.layer, info.datatype)] = (polys, texts)
    insts = sorted((layout.cell(i.cell_index).name, str(i.trans),
                    i.property(61)) for i in cell.each_inst())
    return shapes, insts


def same(la, ca, lb, cb):
    sa, ia = fingerprint(la, ca)
    sb, ib = fingerprint(lb, cb)
    if ia != ib or set(sa) != set(sb):
        return False
    for key in sa:
        if sa[key][1] != sb[key][1] or not (sa[key][0] ^ sb[key][0]).is_empty():
            return False
    return True


def subtree(layout, cell):
    """The cell and every cell below it."""
    return [cell] + [layout.cell(ci) for ci in cell.called_cells()]


def main():
    gen = kdb.Layout()
    gen.read(GEN)
    user = kdb.Layout()
    user.read(USER)

    for name in ROUTED:
        gcell, ucell = gen.cell(name), user.cell(name)
        if gcell is None or ucell is None:
            raise SystemExit("%s fehlt in %s" % (name, GEN if gcell is None
                                                  else USER))
        dx, dy = shift_between(gcell, ucell)

        # every instance of the generator's copy, to be repointed
        parents = []
        for inst in gcell.each_parent_inst():
            ci = inst.child_inst()
            parents.append((inst.parent_cell_index(), ci.cell_inst.trans,
                            ci.prop_id))

        # The copy and whatever only it uses go.  A leaf cell used elsewhere
        # too would stay, and the original's version of it would then come
        # in under a new name -- refuse that rather than rename silently.
        gen.prune_cell(gcell.cell_index(), -1)
        clash = [c.name for c in subtree(user, ucell)[1:]
                 if gen.cell(c.name) is not None]
        if clash:
            raise SystemExit("%s: %s is also used outside it; the original "
                             "and the generator's version would collide"
                             % (name, ", ".join(sorted(set(clash)))))

        new = gen.create_cell(name)
        new.copy_tree(ucell)
        for parent, trans, prop_id in parents:
            moved = trans * kdb.Trans(kdb.Vector(dx, dy))
            gen.cell(parent).insert(kdb.CellInstArray(new.cell_index(),
                                                      moved), prop_id)

        for ucell_below in subtree(user, ucell):
            copy = gen.cell(ucell_below.name)
            if copy is None or not same(user, ucell_below, gen, copy):
                raise SystemExit("%s: copy of %s is not identical"
                                 % (name, ucell_below.name))
        print("%s: aus lvds_tx.gds uebernommen, %d Zellen identisch, "
              "Instanzen um %.3f / %.3f um verschoben"
              % (name, len(subtree(user, ucell)), dx * gen.dbu, dy * gen.dbu))

    gen.write(OUT)
    print("geschrieben: %s" % os.path.basename(OUT))


if __name__ == "__main__":
    sys.exit(main())
