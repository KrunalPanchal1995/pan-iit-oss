"""Checkpoint for Session 5. Prints PASS or FAIL."""
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
    W, H, C, BD, D, S = 40.0, 30.0, (20.0, 15.0), 12.0, 6.0, 4.0
    DEPTH, DOC, FEED, PLUNGE = 5.0, 2.0, 300.0, 100.0
    rb, r = BD / 2, D / 2

    # the clearance field
    ok_phi = abs(L.clearance(20, 15 + 6 + 2, W, H, C, rb) - 2.0) < 1e-12 and abs(L.clearance(1, 15, W, H, C, rb) - 1.0) < 1e-12 and abs(L.clearance(20, 29, W, H, C, rb) - 1.0) < 1e-12
    s_ = C[0] + C[1] + rb
    rho_formula = s_ - math.sqrt(s_ * s_ - (C[0] ** 2 + C[1] ** 2 - rb * rb))
    rho = L.max_clearance(W, H, C, BD)
    checks.append((f"clearance field: the distance to the nearest wall or to the boss; the largest clearance of the 40 x 30 mm pocket with a 12 mm boss is {rho:.4f} mm, equal to the closed form for the corner point {rho_formula:.4f} mm, and a ring just above it is empty",
                   ok_phi and abs(rho - rho_formula) < 1e-9 and L.level_nonempty(W, H, C, rb, rho - 1e-6) and not L.level_nonempty(W, H, C, rb, rho + 1e-6)))

    # rings
    ok_ring, worst = True, 0.0
    for ell in (3.0, 4.4, 4.6, 5.477, 6.5, 7.5, 7.9):
        for lp in L.level_loops(W, H, C, BD, ell):
            for x, y in L.densify(lp, 0.05):
                worst = max(worst, abs(L.clearance(x, y, W, H, C, rb) - ell))
    ok_ring = worst < 1e-6
    checks.append((f"a ring is a level set: every point of the rings at 3, 4.4, 4.6, 5.477, 6.5, 7.5 and 7.9 mm has a clearance equal to the ring's value (worst error {worst:.1e} mm, needed: at most 1e-6)", ok_ring))
    loops3 = L.level_loops(W, H, C, BD, 3.0)
    areas = sorted(L.signed_area(L.sample_loop(lp, 0.02)) for lp in loops3)
    closed = all(math.hypot(L.piece_end(lp[k])[0] - L.piece_start(lp[(k + 1) % len(lp)])[0], L.piece_end(lp[k])[1] - L.piece_start(lp[(k + 1) % len(lp)])[1]) < 1e-6 for lp in loops3 for k in range(len(lp)))
    checks.append((f"the first ring (3 mm) is the rectangle 34 x 24 mm (area 816) with the boss circle of radius 9 mm as a hole (area {areas[0]:.2f}, formula {-math.pi * 81:.2f}); its pieces join end to start",
                   len(loops3) == 2 and closed and abs(areas[1] - 816.0) < 1e-6 and abs(areas[0] + math.pi * 81) < 0.05))
    counts = {e: len(L.level_components(W, H, C, BD, e)) for e in (3.0, 4.4, 4.6, 5.477, 7.5, 7.9)}
    checks.append((f"rings split: the number of separate pieces is {counts[3.0]} at 3 mm, {counts[4.4]} at 4.4 mm, then {counts[4.6]} from 4.6 mm on (the neck between boss and wall closes at (15 - 6) / 2 = 4.5 mm), and {counts[7.5]} corner pieces from 7.5 mm to the end",
                   counts[3.0] == 1 and counts[4.4] == 1 and counts[4.6] == 2 and counts[5.477] == 2 and counts[7.5] == 4 and counts[7.9] == 4))
    offs = L.level_offsets(rho, r, S)
    checks.append((f"ring schedule for the roadmap pocket: rings at {', '.join(f'{v:.3f}' for v in offs)} mm (every {S:g} mm from the cutter radius; the cutter reaches {r:g} mm past the last ring, so none is needed at {rho:.3f} mm)",
                   len(offs) == 2 and abs(offs[0] - 3.0) < 1e-12 and abs(offs[1] - 7.0) < 1e-12))

    # the tree
    roots, levels, o3, _ = L.build_tree(W, H, C, BD, D, S, [3.0, 5.477288358, rho])
    shape = [len(roots), [len(c["children"]) for c in roots], [[len(g["children"]) for g in c["children"]] for c in roots]]
    pts_ok = all(g["is_point"] for c in roots[0]["children"] for g in c["children"])
    checks.append((f"the tree for rings 3, 5.477 and {rho:.3f} mm: one root, two crescents (children) and two corner points under each ({shape[1][0]} children, then {shape[2][0]}); the last rings are points",
                   shape[0] == 1 and shape[1] == [2] and shape[2] == [[2, 2]] and pts_ok))
    ok_hole = len(roots[0]["holes"]) == 1 and all(len(c["holes"]) == 0 for c in roots[0]["children"])
    checks.append(("the root keeps the boss circle as a hole; from the second ring on the circle is part of the outer boundary of each crescent", ok_hole))

    # links
    p, q = (5.0, 15.0), (35.0, 15.0)
    route = L.link_route(p, q, C, rb + r, W, H, r)
    ref = 2 * math.sqrt(15.0 ** 2 - 9.0 ** 2) + 9.0 * (math.pi - 2 * math.acos(9.0 / 15.0))
    clear = min(math.hypot(x - C[0], y - C[1]) for x, y in L.densify(route, 0.02))
    direct = L.link_route((5.0, 5.0), (35.0, 5.0), C, rb + r, W, H, r)
    checks.append((f"a link round the boss: from (5, 15) to (35, 15) the straight line is blocked, so the route is tangent, arc, tangent: {L.segs_length(route):.3f} mm (independent value {ref:.3f} mm) and never closer than {clear:.3f} mm to the boss centre (needed: at least 9); a free link stays a straight line ({len(direct)} piece)",
                   len(route) == 3 and abs(L.segs_length(route) - ref) < 1e-6 and clear >= 9 - 1e-6 and len(direct) == 1 and direct[0][0] == "L"))

    # the path
    plan = L.plan_pocket(W, H, C, BD, D, S)
    path = plan["path"]
    gaps = max(math.hypot(L.piece_end(a)[0] - L.piece_start(b)[0], L.piece_end(a)[1] - L.piece_start(b)[1]) for a, b in zip(path[:-1], path[1:]))
    dense = L.densify(path, 0.02)
    low = min(L.clearance(x, y, W, H, C, rb) for x, y in dense)
    checks.append((f"the centre path of one layer ({plan['length']:.1f} mm, {len(path)} pieces) is unbroken (largest gap between pieces {gaps:.1e} mm) and never gets closer than the cutter radius to a wall or the boss: smallest clearance {low:.6f} mm (needed: at least 3)",
                   gaps < 1e-6 and low >= 3.0 - 1e-6))
    only_outer = L.walk_tree(L.build_tree(W, H, C, BD, D, S, [3.0])[0][0], W, H, C, BD, D, (r, r))
    bad_one = L.uncovered_cells(only_outer, W, H, C, BD, r)
    bad_all = L.uncovered_cells(path, W, H, C, BD, r)
    checks.append((f"coverage check: the first ring alone leaves {len(bad_one) * 0.0625:.1f} mm^2 farther than the cutter radius from the path; the planned path leaves {len(bad_all)} grid points (the rounded corner leftovers are not counted)",
                   len(bad_one) > 100 and len(bad_all) == 0 and plan["uncovered"] == 0))

    # G-code
    hm, mv, text = L.simulate_contour(W, H, DEPTH, D, DOC, S, FEED, PLUNGE, C, BD)
    layers = math.ceil(DEPTH / DOC - 1e-9)
    plunges = [m for m in mv if m["kind"] == "G1" and abs(m["b"][2] - m["a"][2]) > 1e-9]
    rapid_xy = [m for m in mv if m["kind"] == "G0" and (m["b"][0], m["b"][1]) != (m["a"][0], m["a"][1])]
    ups, _ = L.count_lifts(mv)
    n_arcs = sum(1 for m in mv if m["kind"] in ("G2", "G3"))
    base = L.read_moves(L.boss_pocket_gcode(W, H, DEPTH, D, DOC, S, FEED, PLUNGE, C, BD))
    base_plunges = sum(1 for m in base if m["kind"] == "G1" and abs(m["b"][2] - m["a"][2]) > 1e-9)
    checks.append((f"G-code read back: {layers} layers, {len(plunges)} plunges and {len(rapid_xy)} rapid moves in x and y (one per layer), {ups - 2} lifts (the end of each layer), {n_arcs} arcs in all; the Session 3 raster program needs {base_plunges} plunges: the cutter does not lift inside a layer",
                   layers == 3 and len(plunges) == 3 and len(rapid_xy) == 3 and ups - 2 == 3 and n_arcs >= 3 * 4 and base_plunges > 30))
    cutting = [m for m in mv if m["kind"] != "G0"]
    t_cut, t_base = L.gcode_time_s(cutting), L.gcode_time_s([m for m in base if m["kind"] != "G0"])
    dz = DEPTH / layers
    plunge_len = sum(1.0 + k * dz for k in range(1, layers + 1))
    t_ref = layers * plan["length"] / FEED * 60 + plunge_len / PLUNGE * 60
    checks.append((f"roadmap test: cutting time (G1, G2 and plunge moves) {t_cut:.1f} s (needed: under 200 s) against {t_base:.1f} s for the Session 3 raster program; an independent sum ({layers} layers x {plan['length']:.1f} mm at {FEED:g} mm/min plus {plunge_len:.1f} mm of plunging at {PLUNGE:g} mm/min) gives {t_ref:.1f} s",
                   t_cut < 200.0 and abs(t_cut - t_ref) < 0.05 and abs(t_base - 315.5) < 0.5))
    sim, exp = hm.removed_volume(), L.boss_expected_volume(W, H, DEPTH, D, BD)
    intr = L.boss_intrusion_area(hm, C, BD)
    checks.append((f"roadmap test: simulated volume {sim:.1f} mm^3 against the analytic {exp:.1f} mm^3 = (area - boss - corner leftovers) x depth ({100 * (sim / exp - 1):+.3f} %, needed: within 0.5 %), with {intr:.3f} mm^2 cut inside the boss (G-code is rounded to 0.001 mm)",
                   abs(sim / exp - 1) < 0.005 and intr < 0.05))

    # other set-ups
    w2, h2, c2, bd2 = 60.0, 40.0, (30.0, 20.0), 14.0
    p_no = L.plan_pocket(w2, h2, c2, bd2, D, S, refine=False)
    p_yes = L.plan_pocket(w2, h2, c2, bd2, D, S)
    bad_no = L.uncovered_cells(p_no["path"], w2, h2, c2, bd2, r)
    hm2, mv2, _ = L.simulate_contour(w2, h2, DEPTH, D, DOC, S, FEED, PLUNGE, c2, bd2)
    e2 = L.boss_expected_volume(w2, h2, DEPTH, D, bd2)
    checks.append((f"where rings split, spacing at most the stepover is not enough: in a 60 x 40 mm pocket with a 14 mm boss the rings every 4 mm leave {len(bad_no) * 0.0625:.1f} mm^2 uncut above the boss ({len(p_no['offsets'])} rings); the check adds a ring and the simulated volume is then within {100 * abs(hm2.removed_volume() / e2 - 1):.3f} % of the target ({len(p_yes['offsets'])} rings)",
                   len(bad_no) > 20 and len(p_yes["offsets"]) == len(p_no["offsets"]) + 1 and len(p_yes["added"]) == 1 and abs(hm2.removed_volume() / e2 - 1) < 0.005))
    c3 = (14.0, 15.0)
    pl3 = L.plan_pocket(W, H, c3, BD, D, S)
    hm3, mv3, _ = L.simulate_contour(W, H, DEPTH, D, DOC, S, FEED, PLUNGE, c3, BD)
    e3 = L.boss_expected_volume(W, H, DEPTH, D, BD)
    ups3, _ = L.count_lifts(mv3)
    checks.append((f"an off-centre boss at (14, 15): rings at {', '.join(f'{v:.2f}' for v in pl3['offsets'])} mm, {ups3 - 2} lifts (layer ends only), simulated volume within {100 * abs(hm3.removed_volume() / e3 - 1):.3f} % of the target",
                   ups3 - 2 == 3 and abs(hm3.removed_volume() / e3 - 1) < 0.005 and L.uncovered_cells(pl3["path"], W, H, c3, BD, r).size == 0))

    # failure cases
    checks.append(("failure cases are refused: a boss so big that the cutter cannot pass between it and the walls (the free space has two parts), a boss touching a wall or outside the pocket, a gap exactly as wide as the cutter, a stepover above the cutter diameter, a cutter that fits nowhere, and zero or negative sizes",
                   _raises(L.plan_pocket, *L.BOSS_TOO_BIG) and _raises(L.plan_pocket, W, H, (5.0, 15.0), BD, D, S) and _raises(L.plan_pocket, W, H, (50.0, 15.0), BD, D, S)
                   and _raises(L.plan_pocket, W, H, C, 18.0, D, S) and _raises(L.plan_pocket, W, H, C, BD, D, 7.0) and _raises(L.plan_pocket, W, H, C, BD, 40.0, S)
                   and _raises(L.plan_pocket, W, H, C, 0.0, D, S) and _raises(L.plan_pocket, W, H, C, BD, 0.0, S) and _raises(L.plan_pocket, W, H, C, BD, D, 0.0)))
    return checks
# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson5", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
