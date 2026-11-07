"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def _raises(f, *a, **k):
    try:
        f(*a, **k)
    except ValueError:
        return True
    return False


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    hexa = L.regular_polygon(6, 20.0)

    # the polygon
    sides = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(hexa, hexa[1:] + hexa[:1])]
    ok_hex = len(hexa) == 6 and max(abs(v - 20.0) for v in sides) < 1e-12 and abs(L.polygon_area(hexa) - 1.5 * math.sqrt(3) * 400) < 1e-9
    ok_hex &= all(abs(t - 2 * math.pi / 3) < 1e-12 for t in L.interior_angles(hexa))
    L.check_convex(hexa)
    checks.append((f"the regular hexagon of side 20 mm has six equal sides, interior angles of 120 degrees and area {L.polygon_area(hexa):.2f} mm^2 (= 3 sqrt(3) / 2 x 400)", ok_hex))
    L_shape, cw = L.L_SHAPE, list(reversed(hexa))
    checks.append(("failure: an L-shaped (not convex) polygon, a clockwise polygon and a polygon with two corners are refused",
                   _raises(L.check_convex, L_shape) and _raises(L.check_convex, cw) and _raises(L.offset_polygon, L_shape, 1.0) and _raises(L.check_convex, hexa[:2])))

    # the roadmap test
    off = L.offset_polygon(hexa, 3.0)
    lines = L.edge_lines(hexa)
    worst, ok_adj, ok_far = 0.0, True, True
    for v in off:
        dist = [L.dist_to_edge_line(v, ln) for ln in lines]
        order = sorted(range(6), key=lambda i: dist[i])
        a, b = order[0], order[1]
        worst = max(worst, abs(dist[a] - 3.0), abs(dist[b] - 3.0))
        ok_adj &= (b - a) % 6 in (1, 5)                       # the two nearest edges are neighbours
        ok_far &= all(dist[i] > 3.0 + 1e-6 for i in order[2:])
    checks.append((f"roadmap test: every one of the {len(off)} corners of the offset hexagon (side 20 mm, offset 3 mm) lies 3 mm from its two neighbouring edges (worst error {worst:.1e} mm, needed: at most 1e-6) and farther from the other four",
                   len(off) == 6 and worst <= 1e-6 and ok_adj and ok_far))
    new_side = math.hypot(off[1][0] - off[0][0], off[1][1] - off[0][1])
    th = 2 * math.pi / 3
    checks.append((f"edge by edge: the corners move {L.corner_shift(th, 3.0):.4f} mm along the bisector (3 / sin 60), and the sides shrink to {new_side:.4f} mm = 20 - 3 x 2 cot 60 (formula {L.offset_edge_length(20.0, th, th, 3.0):.4f})",
                   abs(L.corner_shift(th, 3.0) - 3 / math.sin(math.pi / 3)) < 1e-12 and abs(new_side - 16.5359) < 1e-4 and abs(new_side - L.offset_edge_length(20.0, th, th, 3.0)) < 1e-9
                   and abs(math.hypot(*off[0]) - (20.0 - 3.4641)) < 1e-4))
    naive = L.offset_edges(hexa, 3.0)
    same = max(min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in off) for p in naive)
    checks.append((f"the edge-by-edge recipe and the clipping method give the same hexagon (largest difference {same:.1e} mm), and the area {L.polygon_area(off):.3f} mm^2 equals A - P d + d^2 sum cot(theta/2) = {L.offset_area_formula(hexa, 3.0):.3f}",
                   same < 1e-9 and abs(L.polygon_area(off) - L.offset_area_formula(hexa, 3.0)) < 1e-9))

    # collapse
    rho = L.collapse_distance(hexa)
    ap = L.apothem(6, 20.0)
    inside, outside, at = L.offset_polygon(hexa, rho - 1e-6), L.offset_polygon(hexa, rho + 1e-6), L.offset_polygon(hexa, ap)
    checks.append((f"collapse: the hexagon offset vanishes at {rho:.6f} mm = the apothem {ap:.6f} mm; just inside it still has {len(inside)} corners, just outside it is None, and at exactly the apothem it is the single point at the centre",
                   abs(rho - ap) < 1e-9 and len(inside) == 6 and outside is None and len(at) == 1 and math.hypot(*at[0]) < 1e-9))
    ok_all = all(abs(L.collapse_distance(L.regular_polygon(n, 20.0)) - L.apothem(n, 20.0)) < 1e-8 for n in range(3, 9))
    checks.append(("for every regular polygon with 3 to 8 sides (side 20 mm) the collapse distance equals a / (2 tan(pi / n))", ok_all))
    rect = [(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0)]
    ro = L.offset_polygon(rect, 3.0)
    seg = L.offset_polygon(rect, 15.0)
    checks.append((f"a rectangle is a special case: the 40 x 30 mm pocket offset by 3 mm has corners (3, 3) and (37, 27) as in Session 2, and it collapses at {L.collapse_distance(rect):.6f} mm = 15 (half the short side) into a segment of length {abs(seg[1][0] - seg[0][0]):.1f} mm",
                   len(ro) == 4 and np.abs(np.array(sorted(ro)) - np.array([(3, 3), (3, 27), (37, 3), (37, 27)])).max() < 1e-9
                   and abs(L.collapse_distance(rect) - 15.0) < 1e-9 and len(seg) == 2 and abs(abs(seg[1][0] - seg[0][0]) - 10.0) < 1e-9))

    # an edge that vanishes
    T = L.TRAPEZOID
    ev, tr = L.edge_vanish_distance(T), L.collapse_distance(T)
    nv, gd = L.offset_edges(T, 6.0), L.offset_polygon(T, 6.0)
    se = L.signed_edge_lengths(nv, T)
    checks.append((f"failure: in the trapezoid (40 / 4 / 20 mm) the top edge vanishes at d = {ev:.4f} mm but the polygon only collapses at {tr:.4f} mm; at d = 6 mm the edge-by-edge recipe has a reversed edge ({min(se):.2f} mm) and the wrong area {L.polygon_area(nv):.3f}, while clipping gives a triangle of area {L.polygon_area(gd):.3f}",
                   abs(ev - 4.4907) < 1e-3 and abs(tr - 8.9072) < 1e-3 and ev < tr and min(se) < 0 and len(gd) == 3 and abs(L.polygon_area(gd) - 47.347) < 0.01
                   and abs(L.polygon_area(nv) - L.polygon_area(gd)) > 0.3))
    checks.append(("failure: a negative offset is refused, and the cutter that does not fit (diameter 36 mm in the hexagon of side 20 mm, whose inscribed circle has diameter 34.64 mm) and a stepover larger than the cutter are refused",
                   _raises(L.offset_polygon, hexa, -1.0) and _raises(L.ring_offsets, hexa, 36.0, 4.0) and _raises(L.ring_offsets, hexa, 6.0, 7.0) and len(L.ring_offsets(hexa, 34.0, 4.0)) >= 1))

    # the pocket
    D, s, depth, doc, feed, plunge = 6.0, 4.0, 5.0, 2.0, 300.0, 100.0
    offs = L.ring_offsets(hexa, D, s)
    steps = np.diff(offs)
    checks.append((f"rings: {len(offs)} rings from the cutter radius {offs[0]:.1f} mm to the collapse {offs[-1]:.3f} mm, evenly spaced by {steps[0]:.3f} mm (at most the stepover {s:g} mm)",
                   len(offs) == 5 and abs(offs[0] - 3.0) < 1e-12 and abs(offs[-1] - rho) < 1e-9 and steps.max() <= s + 1e-12 and steps.max() - steps.min() < 1e-9))
    path = L.pocket_path(hexa, D, s)
    low = min(L.dist_to_edge_line(0.5 * (p + q), ln) for p, q in zip(path[:-1], path[1:]) for ln in lines)
    low = min(low, min(L.dist_to_edge_line(p, ln) for p in path for ln in lines))
    checks.append((f"the centre path of one layer ({L.path_length(path):.1f} mm) never gets closer than the cutter radius to a wall: smallest clearance {low:.6f} mm (needed: at least 3)", low >= 3.0 - 1e-9))
    hm, mv, text = L.simulate_pocket(hexa, depth, D, doc, s, feed, plunge)
    layers = math.ceil(depth / doc - 1e-9)
    plunges = [m for m in mv if m["kind"] == "G1" and abs(m["b"][2] - m["a"][2]) > 1e-9]
    rapid_xy = [m for m in mv if m["kind"] == "G0" and (m["b"][0], m["b"][1]) != (m["a"][0], m["a"][1])]
    checks.append((f"G-code read back: {layers} layers, {len(plunges)} plunges and {len(rapid_xy)} rapid moves in x and y (one per layer): the cutter does not lift inside a layer",
                   layers == 3 and len(plunges) == 3 and len(rapid_xy) == 3))
    sim, exp = hm.removed_volume(), L.expected_volume(hexa, depth, D)
    out = L.cut_outside_area(hm, hexa)
    checks.append((f"simulation: {sim:.1f} mm^3 removed against the analytic {exp:.1f} mm^3 = (area - corner leftovers) x depth ({100 * (sim / exp - 1):+.2f} %, needed: within 0.5 %), and {out:.3f} mm^2 cut outside the walls (G-code is rounded to 0.001 mm)",
                   abs(sim / exp - 1) < 0.005 and out < 0.05))
    r = D / 2
    lo_h = 6 * r * r * (1 / math.tan(math.pi / 3) - (math.pi - 2 * math.pi / 3) / 2)
    checks.append((f"corner leftover of a polygon: {L.corner_leftover_polygon(hexa, r):.3f} mm^2 for the hexagon (6 corners of 120 degrees) and, for a square, 4 r^2 (1 - pi/4) = {L.corner_leftover_polygon([(0, 0), (9, 0), (9, 9), (0, 9)], r):.3f} mm^2 as in Session 3",
                   abs(L.corner_leftover_polygon(hexa, r) - lo_h) < 1e-12 and abs(L.corner_leftover_polygon([(0, 0), (9, 0), (9, 9), (0, 9)], r) - L.corner_leftover(r)) < 1e-9))
    t_cut = L.gcode_time_s([m for m in mv if m["kind"] == "G1"])
    dz = depth / layers
    plunge_len = sum(1.0 + k * dz for k in range(1, layers + 1))
    t_ref = layers * L.path_length(path) / feed * 60 + plunge_len / plunge * 60
    checks.append((f"cutting time {t_cut:.1f} s (G1 moves) agrees with an independent sum: {layers} layers x {L.path_length(path):.1f} mm at {feed:g} mm/min plus {plunge_len:.1f} mm of plunging at {plunge:g} mm/min = {t_ref:.1f} s; the whole program with rapids takes {L.gcode_time_s(mv):.1f} s",
                   abs(t_cut - t_ref) < 0.01 and abs(t_cut - 166.5) < 0.5))
    return checks
# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
