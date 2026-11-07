"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    W, H, D = 40.0, 30.0, 6.0
    # --- scallops (ball end)
    for s, want in ((1, 0.0420), (2, 0.1716), (3, 0.4019), (4, 0.7639)):
        checks.append((f"ridge height r=3 mm, stepover {s} mm: formula {want:.4f} mm",
                       abs(L.cusp_height(3, s) - want) < 5e-5))
    checks.append(("worked example: the height-map simulation agrees with the formula to 0.002 mm (stepover 1 to 4 mm)",
                   all(abs(L.simulate_cusp(3, s) - L.cusp_height(3, s)) < 2e-3 for s in (1, 2, 3, 4))))
    checks.append(("inverse formula: ridge 0.05 mm with r = 3 mm needs stepover 1.0909 mm",
                   abs(L.stepover_for_cusp(3, 0.05) - 1.0909) < 1e-4 and abs(L.cusp_height(3, L.stepover_for_cusp(3, 0.05)) - 0.05) < 1e-12))
    checks.append(("stepover 1.0 mm gives 0.0420 mm (<= 0.05) but 1.1 mm gives 0.0508 mm (> 0.05)",
                   L.cusp_height(3, 1.0) <= 0.05 < L.cusp_height(3, 1.1)))
    checks.append(("edge: stepover equal to the cutter diameter gives a finite ridge of r = 3 mm; zero stepover gives 0",
                   abs(L.cusp_height(3, 6) - 3.0) < 1e-12 and L.cusp_height(3, 0) == 0.0 and L.stepover_for_cusp(3, 0) == 0.0))
    # --- MRR and chip load
    checks.append(("MRR = 4 mm * 2 mm * 300 mm/min = 2400 mm^3/min", L.mrr(4, 2, 300) == 2400))
    checks.append(("chip load = 300 / (6000 * 2) = 0.025 mm per tooth", abs(L.chip_load(300, 6000, 2) - 0.025) < 1e-12))
    v = L.line_cut_volume(3, 2, 20)
    cap = math.pi * 9 * 2
    checks.append(("a 20 mm straight cut (6 mm wide, 2 mm deep): simulated volume = (6*20 + pi*9) * 2 = 296.5 mm^3 within 0.5%",
                   abs(v - (6 * 20 * 2 + cap)) / v < 0.005))
    checks.append(("MRR check: removed volume minus the two half-circle ends equals width*depth*length = 240 mm^3 (feed cancels: 6*2*300 * 20/300)",
                   abs((v - cap) - L.mrr(6, 2, 300) * 20 / 300) / 240 < 0.005))
    # --- strategies
    ras, con = L.raster_path(W, H, D, 4), L.contour_path(W, H, D, 4)
    checks.append(("raster with stepover 4: 7 lines, length 262 mm per layer", L.n_lines(24, 4) == 7 and abs(L.path_length(ras) - 262) < 1e-9))
    checks.append(("contour-parallel with stepover 4: rings 34x24, 26x16, 18x8 and a 10 mm centre line, length 279.0 mm",
                   abs(L.path_length(con) - 278.97) < 0.01 and len(con) == 5 * 3 + 2))
    cl_c, out_c = L.pocket_cleared_area(con, W, H, 3)
    ideal = W * H - L.corner_leftover(3)
    checks.append(("contour-parallel clears the pocket except the corners: 1192.3 mm^2 (= 1200 - 4 * 3^2 * (1 - pi/4))",
                   abs(cl_c - ideal) < 0.2 and abs(ideal - 1192.27) < 0.01 and out_c == 0.0))
    cl_r, _ = L.pocket_cleared_area(ras, W, H, 3)
    checks.append(("raster alone leaves extra scallops at the line ends (cleared 1186.5 mm^2 < 1192.3)",
                   cl_r < cl_c - 5.0 and abs(cl_r - 1186.5) < 0.2))
    checks.append(("time/stepover: raster lengths 466, 262, 194 mm for stepover 2, 4, 6 mm",
                   [round(L.path_length(L.raster_path(W, H, D, s))) for s in (2, 4, 6)] == [466, 262, 194]))
    checks.append(("a stepover of 2r leaves corner cusps in contour-parallel: cleared 1180.9 mm^2 at s = 6 mm",
                   abs(L.pocket_cleared_area(L.contour_path(W, H, D, 6), W, H, 3)[0] - 1180.9) < 0.2))
    # --- strips (stepover larger than the diameter)
    wide = L.raster_path(W, H, D, 8)
    hm = L.HeightMap(0, W, 0, H, 0.1)
    hm.cut_polyline(wide, -1.0, 3.0)
    win = (hm.xc >= 6) & (hm.xc <= 34)
    uncut = float((hm.h[:, win] >= -1e-9).sum() * 0.01)
    checks.append(("stepover 8 mm with a 6 mm cutter leaves 3 strips 2 mm wide: 3 * 2 * 28 = 168 mm^2 uncut between x = 6 and 34",
                   L.n_lines(24, 8) == 4 and abs(uncut - 168.0) < 1.0))
    # --- corners
    ok = True
    for r in (1, 2, 3, 4, 5):
        pts = np.vstack([L.raster_path(W, H, 2 * r, r), [(r, r), (W - r, r), (W - r, H - r), (r, H - r), (r, r)]])
        cleared, _ = L.pocket_cleared_area(pts, W, H, r, res=0.05)
        ok &= abs((W * H - cleared) - L.corner_leftover(r)) < 0.1
    checks.append(("inside corners: leftover area 4 r^2 (1 - pi/4) matches the simulation for r = 1..5 mm (0.86, 3.43, 7.73, 13.73, 21.46)", ok))
    checks.append(("corner leftover formula values for r = 1 and 3 mm", abs(L.corner_leftover(1) - 0.8584) < 1e-4 and abs(L.corner_leftover(3) - 7.7257) < 1e-4))
    checks.append(("planner: corner radius 2 mm with a 6 mm cutter is reported; 3 mm is fine",
                   "smaller" in L.check_inside_corner(2, 6) and L.check_inside_corner(3, 6) == "ok"))
    # --- failures
    inside = np.array([(3, 3), (37, 3), (37, 27), (3, 27), (3, 3)], dtype=float)
    outward = np.array([(-3, -3), (43, -3), (43, 33), (-3, 33), (-3, -3)], dtype=float)
    on_line = np.array([(0, 0), (40, 0), (40, 30), (0, 30), (0, 0)], dtype=float)
    gi = L.pocket_cleared_area(inside, W, H, 3, res=0.05, margin=10)
    go = L.pocket_cleared_area(outward, W, H, 3, res=0.05, margin=10)
    gl = L.pocket_cleared_area(on_line, W, H, 3, res=0.05, margin=10)
    checks.append(("correct inside offset gouges nothing (0 mm^2 outside the pocket)", gi[1] == 0.0))
    checks.append(("wrong direction (outward offset): cuts 976.3 mm^2 outside the pocket and nothing inside",
                   abs(go[1] - L.wrong_offset_gouge_area(W, H, 3)) < 1.0 and abs(L.wrong_offset_gouge_area(W, H, 3) - 976.27) < 0.01 and go[0] == 0.0))
    checks.append(("zero offset (centre on the outline) gouges 448.3 mm^2 outside the pocket", abs(gl[1] - 448.26) < 1.0))
    checks.append(("slot 5 mm wide, 6 mm cutter: the planner reports it cannot cut",
                   L.plan_slot(30, 5, 6)[0] is None and "cannot cut" in L.plan_slot(30, 5, 6)[1]))
    checks.append(("edge: a 6 mm cutter in a 6 mm slot is accepted, centre line from x = 3 to 27 mm",
                   L.plan_slot(30, 6, 6)[1] == "ok" and L.plan_slot(30, 6, 6)[0] == [(3.0, 3.0), (27.0, 3.0)]))
    # --- mini-project
    prog = L.boss_pocket_gcode(W, H, 5, D, 2, 4, 300, 100, (20, 15), 12)
    mv = L.read_moves(prog)
    checks.append(("boss program is plain G-code: G21, G90, uses G0, G1 and G3 only",
                   prog.startswith("G21\nG90") and {m["kind"] for m in mv} == {"G0", "G1", "G3"}))
    sim = L.HeightMap(0, W, 0, H, 0.1)
    L.simulate_moves(sim, mv, D / 2)
    expected = L.boss_expected_volume(W, H, 5, D, 12)
    checks.append(("worked example: expected removed volume (1200 - 113.10 - 7.73) * 5 = 5395.9 mm^3", abs(expected - 5395.9) < 0.1))
    checks.append(("simulation of the parsed G-code removes 5396 mm^3, within 0.1% of the expected volume",
                   abs(sim.removed_volume() - expected) / expected < 0.001))
    cx, cy = np.argmin(abs(sim.xc - 20)), np.argmin(abs(sim.yc - 15))
    checks.append(("the boss is untouched (height 0) and the floor is at -5 mm", sim.h[cy, cx] == 0.0 and abs(sim.h.min() + 5.0) < 1e-9))
    checks.append(("the uncut area is the boss plus four corners (about 120.8 mm^2)",
                   abs(float((sim.h > -1e-9).sum() * 0.01) - 120.76) < 0.5))
    t = L.gcode_time_s(mv)
    checks.append(("estimated time: 327 s (5.5 min) with rapids at 3000 mm/min", abs(t - 327.3) < 0.5))
    checks.append(("the program has 1213 mm of cutting, arc and plunge moves", abs(L.moves_length(mv) - 1213.4) < 0.5))
    checks.append(("corner leftover for r = 2, 4, 5 mm: 3.43, 13.73, 21.46 mm^2; doubling r quadruples it",
                   abs(L.corner_leftover(2) - 3.43) < 0.01 and abs(L.corner_leftover(4) - 13.73) < 0.01 and abs(L.corner_leftover(5) - 21.46) < 0.01
                   and abs(L.corner_leftover(4) / L.corner_leftover(2) - 4.0) < 1e-12))
    checks.append(("chip load 480 / (8000 * 2) = 0.03 mm and MRR 3 * 1.5 * 400 = 1800 mm^3/min",
                   abs(L.chip_load(480, 8000, 2) - 0.03) < 1e-12 and abs(L.mrr(3, 1.5, 400) - 1800) < 1e-9))
    checks.append(("worked example arithmetic: sqrt(8) = 2.828, sqrt(0.2975) = 0.5454, ridge at 1.1 mm = 0.0508 mm",
                   abs(math.sqrt(8) - 2.828) < 5e-4 and abs(math.sqrt(0.2975) - 0.5454) < 5e-5 and abs(L.cusp_height(3, 1.1) - 0.0508) < 5e-5))
    s_d = L.stepover_for_cusp(4, 0.02)
    checks.append(("design answer: ball r = 4 mm, ridge 0.02 mm: s = 0.7990 mm, use 0.79 mm: 39 lines, 1590 mm, 159.0 s at 600 mm/min",
                   abs(s_d - 0.7990) < 1e-4 and L.n_lines(30, 0.79) == 39 and (39 * 40 + 30) == 1590 and abs(1590 / 600 * 60 - 159.0) < 1e-9
                   and L.cusp_height(4, 0.79) <= 0.02))
    cut_only = sum(L.moves_length([m]) / m["f"] * 60 for m in mv if m["kind"] != "G0")
    checks.append(("the shipped boss program needs 315.5 s of cutting (G1, G3 and plunge) out of 327 s", abs(cut_only - 315.5) < 0.1))
    checks.append(("roadmap: a 2 mm cutter would leave only 0.86 mm^2 in the corners", abs(L.corner_leftover(1) - 0.86) < 0.01))
    checks.append(("roadmap: the boss area is pi * 6^2 = 113.10 mm^2", abs(math.pi * 36 - 113.10) < 0.01))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
