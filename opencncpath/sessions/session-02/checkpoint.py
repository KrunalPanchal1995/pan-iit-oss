"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    p = L.Program()
    p.cut(10, 5, f=300)
    checks.append(("G-code word formatting: the line is exactly 'G1 X10 Y5 F300'", p.lines[-1] == "G1 X10 Y5 F300"))
    checks.append(("number formatting drops trailing zeros and negative zero",
                   L.num(3.0) == "3" and L.num(-0.0) == "0" and L.num(1.23456) == "1.235"))
    mv = L.parse_gcode("G21\nG90\nG1 X10 F200 (cut)\nY5 ; same feed, still G1\nG0 Z5")
    checks.append(("parser is modal: Y5 keeps G1, F200 and X10",
                   len(mv) == 3 and mv[1]["kind"] == "G1" and mv[1]["f"] == 200 and mv[1]["p1"] == (10.0, 5.0, 0.0)))
    checks.append(("parser reads a rapid G0 Z5 as a rapid move", mv[2]["kind"] == "G0" and mv[2]["p1"][2] == 5.0))
    checks.append(("round trip: write 'G1 X12.5 Y-3 F150', parse it, get the same numbers",
                   L.parse_gcode("G1 X12.5 Y-3 F150")[0]["p1"] == (12.5, -3.0, 0.0)))
    # offsets
    inn, out = L.offset_rect(40, 30, 3, True), L.offset_rect(40, 30, 3, False)
    checks.append(("worked example: inside offset of a 40 x 30 rectangle by 3 mm is 34 x 24",
                   (inn[2] - inn[0], inn[3] - inn[1]) == (34, 24)))
    checks.append(("outside offset of a 40 x 30 rectangle by 3 mm is 46 x 36",
                   (out[2] - out[0], out[3] - out[1]) == (46, 36)))
    checks.append(("edge: a 31 mm cutter (r 15.5) cannot offset a 30 mm wide pocket inwards",
                   L.offset_rect(40, 30, 15.5, True) is None and L.offset_rect(40, 30, 15, True) is not None))
    prof = L.parse_gcode(L.profile_gcode(40, 30, 3, -2, 200))
    cutting = [m for m in prof if m["kind"] != "G0" and m["p0"][2] == m["p1"][2]]
    pts = L.sample_xy(cutting)
    dev = max(abs(L.dist_to_rect_outline(q, 40, 30) - 3.0) for q in pts)
    checks.append(("every point of the profile toolpath (lines and arcs) is 3 mm from the part outline", dev < 1e-9))
    prof_len = sum(L.move_length(m) for m in cutting)
    checks.append(("profile length = 2 (40 + 30) + 2 pi 3 = 158.85 mm", abs(prof_len - (140 + 2 * math.pi * 3)) < 1e-6))
    # arcs
    ccw = L.parse_gcode("G0 X10 Y0\nG3 X0 Y10 I-10 J0 F200")[1]
    (c, r, sw) = L.arc_geometry(ccw)
    checks.append(("G3 arc (10,0) to (0,10) with I-10 J0: centre (0,0), radius 10", c == (0.0, 0.0) and abs(r - 10) < 1e-12))
    checks.append(("that arc ends on the circle (radius error 0) and sweeps 90 degrees",
                   L.arc_end_radius_error(ccw) < 1e-12 and abs(sw - math.pi / 2) < 1e-12))
    checks.append(("its length is 10 * pi/2 = 15.708 mm", abs(L.move_length(ccw) - 10 * math.pi / 2) < 1e-9))
    cw = L.parse_gcode("G0 X10 Y0\nG2 X0 Y10 I-10 J0 F200")[1]
    checks.append(("the same endpoints with G2 (clockwise) sweep 270 degrees, length 47.124 mm",
                   abs(L.arc_geometry(cw)[2] - 1.5 * math.pi) < 1e-12 and abs(L.move_length(cw) - 15 * math.pi) < 1e-9))
    full = L.parse_gcode("G0 X10 Y0\nG3 X10 Y0 I-10 J0 F200")[1]
    checks.append(("edge: end = start with I, J is a full circle, length 62.832 mm", abs(L.move_length(full) - 20 * math.pi) < 1e-9))
    bad = L.parse_gcode("G0 X10 Y0\nG3 X0 Y9 I-10 J0 F200")[1]
    checks.append(("an inconsistent arc (end 9 mm from the centre, start 10 mm) is detected: error 1 mm",
                   abs(L.arc_end_radius_error(bad) - 1.0) < 1e-12))
    # pocket plan
    pl = L.plan_pocket(40, 30, 5, 6, 2, 4.5, 300)
    checks.append(("worked example: 4.5 mm stepover on a 24 mm span needs 7 lines, spaced 4 mm",
                   pl["n_lines"] == 7 and abs(pl["stepover_actual"] - 4.0) < 1e-12))
    checks.append(("5 mm deep at 2 mm per pass needs 3 layers of 1.667 mm",
                   pl["layers"] == 3 and abs(pl["dz"] - 5 / 3) < 1e-12))
    checks.append(("hand calculation: one layer = 7 * 34 + 24 = 262 mm, three layers 786 mm",
                   pl["per_layer"] == 262 and pl["cut_len"] == 786))
    checks.append(("worked example: time = 786/300 min + 5.5/100 min = 160.5 s", abs(pl["time_s"] - 160.5) < 1e-9))
    prog = L.pocket_gcode(40, 30, 5, 6, 2, 4.5, 300)
    moves = L.parse_gcode(prog)
    nonrapid = sum(L.move_length(m) / m["f"] * 60 for m in moves if m["kind"] != "G0")
    checks.append(("parsing our own G-code gives the planned time (cutting + plunging) 160.5 s", abs(nonrapid - pl["time_s"]) < 1e-6))
    checks.append(("adding rapids at 3000 mm/min makes the total 162.6 s", abs(L.program_time_s(moves) - 162.64) < 0.05))
    cut = [m for m in moves if m["kind"] == "G1" and m["p0"][2] == m["p1"][2]]
    xy = L.sample_xy(cut)
    checks.append(("all cutting points stay inside the centre rectangle 3..37 x 3..27 (cutter edge reaches 0..40 x 0..30)",
                   xy[:, 0].min() >= 3 - 1e-9 and xy[:, 0].max() <= 37 + 1e-9 and xy[:, 1].min() >= 3 - 1e-9 and xy[:, 1].max() <= 27 + 1e-9))
    checks.append(("the deepest Z in the program is -5 mm", abs(min(m["p1"][2] for m in moves) + 5.0) < 1e-9))
    ys = sorted({round(m["p1"][1], 6) for m in cut})
    checks.append(("the line spacing is 4 mm: Y = 3, 7, 11, 15, 19, 23, 27", ys == [3, 7, 11, 15, 19, 23, 27]))
    # limits and trade-off
    checks.append(("edge: stepover 4 on a 24 mm span gives 7 lines, not 8 (round-off safe)", L.plan_pocket(40, 30, 5, 6, 2, 4, 300)["n_lines"] == 7))
    checks.append(("a smaller stepover costs time: 2 mm gives 13 lines and 282.9 s, 6 mm gives 5 lines and 119.7 s",
                   L.plan_pocket(40, 30, 5, 6, 2, 2, 300)["n_lines"] == 13
                   and abs(L.plan_pocket(40, 30, 5, 6, 2, 2, 300)["time_s"] - 282.9) < 1e-6
                   and abs(L.plan_pocket(40, 30, 5, 6, 2, 6, 300)["time_s"] - 119.7) < 1e-6))
    failed = []
    for args in ((40, 30, 5, 31, 2, 4, 300), (40, 30, 5, 6, 2, 7, 300)):
        try:
            L.plan_pocket(*args)
            failed.append(False)
        except ValueError:
            failed.append(True)
    checks.append(("the planner refuses a cutter wider than the pocket and a stepover above the diameter", all(failed)))
    checks.append(("doubling the feed halves the cutting time", abs(L.plan_pocket(40, 30, 5, 6, 2, 4.5, 600)["cut_len"] / 600 - pl["cut_len"] / 300 / 2) < 1e-12))
    checks.append(("worked example: cutting time 786 / 300 min = 2.62 min = 157.2 s and plunge 5.5 mm / 100 mm/min = 3.3 s",
                   abs(pl["cut_len"] / 300 - 2.62) < 1e-12 and abs(pl["cut_len"] / 300 * 60 - 157.2) < 1e-9
                   and pl["plunge_len"] == 5.5 and abs(pl["plunge_len"] / 100 * 60 - 3.3) < 1e-9))
    checks.append(("snippet: 7 lines, 262 mm per layer, 52.4 s per layer", pl["n_lines"] == 7 and pl["per_layer"] == 262 and abs(262 / 300 * 60 - 52.4) < 1e-9))
    p8 = L.plan_pocket(40, 30, 5, 8, 2, 6, 300)
    checks.append(("design answer: 8 mm cutter, stepover 6 mm: 5 lines 5.5 mm apart, 182 mm per layer, 546 mm, 109.2 s cutting, 112.5 s total",
                   p8["n_lines"] == 5 and abs(p8["stepover_actual"] - 5.5) < 1e-12 and p8["per_layer"] == 182 and p8["cut_len"] == 546
                   and abs(p8["cut_len"] / 300 * 60 - 109.2) < 1e-9 and abs(p8["time_s"] - 112.5) < 1e-9))
    checks.append(("exercise: 3 mm stepover gives 9 lines and 6 mm stepover gives 5 lines",
                   L.plan_pocket(40, 30, 5, 6, 2, 3, 300)["n_lines"] == 9 and L.plan_pocket(40, 30, 5, 6, 2, 6, 300)["n_lines"] == 5))
    a20 = L.parse_gcode("G0 X20 Y0\nG3 X0 Y20 I-20 J0 F200")[1]
    checks.append(("assessment B: arc (20,0) to (0,20), I-20 J0: centre (0,0), end radius error 0, length 31.416 mm",
                   L.arc_geometry(a20)[0] == (0.0, 0.0) and L.arc_end_radius_error(a20) < 1e-12 and abs(L.move_length(a20) - 10 * math.pi) < 1e-9))
    q = L.parse_gcode("G0 X10 Y0\nG3 X0 Y10 I-10 J0 F100")[1]
    checks.append(("roadmap: the quarter circle of radius 10 mm has length 15.708 mm", abs(L.move_length(q) - 15.708) < 1e-3))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
