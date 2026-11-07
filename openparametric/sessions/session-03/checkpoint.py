"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    import math
    import random
    checks = []
    v = L.flange()
    checks.append((f"worked example: bolt stress area 84.3 mm2 (got {v['area_b']:.1f})", abs(v["area_b"] - 84.27) < 0.05))
    checks.append((f"worked example: one bolt carries 27.0 kN (got {v['f_bolt']:.1f})", abs(v["f_bolt"] - 26.97) < 0.05))
    checks.append((f"worked example: 4 bolts (got {v['n']})", v["n"] == 4))
    checks.append((f"worked example: bolt circle 162.3 mm and outside diameter 198.3 mm (got {v['pcd']:.1f} and {v['fod']:.1f})", abs(v["pcd"] - 162.3) < 0.01 and abs(v["fod"] - 198.3) < 0.01))
    checks.append((f"worked example: thickness 15 mm (got {v['t']})", v["t"] == 15))
    checks.append((f"worked example: mass 2.356 kg (got {v['mass']:.3f})", abs(v["mass"] - 2.356) < 0.001))
    inputs = L.FLANGE_INPUTS
    seq = L.order(L.FLANGE_RULES, inputs)
    deps = {n: L.dependencies(e) for n, e in L.FLANGE_RULES}
    pos = {n: i for i, n in enumerate(seq)}
    checks.append(("the order is valid: every rule comes after all the rules it uses, and every rule appears once",
                   len(seq) == len(L.FLANGE_RULES) == len(set(seq)) and all(pos[d] < pos[n] for n in seq for d in deps[n] if d in pos)))
    ok = True
    rng = random.Random(7)
    for _ in range(25):
        rules = list(L.FLANGE_RULES)
        rng.shuffle(rules)
        w, _ = L.run_rules(rules, inputs)
        ok &= abs(w["mass"] - v["mass"]) < 1e-9 and w["n"] == v["n"]
    checks.append(("validation: 25 random shufflings of the rule list give exactly the same flange", ok))
    try:
        L.run_rules([("a", "b + 1"), ("b", "c * 2"), ("c", "a - 3")], {})
        msg = ""
    except ValueError as e:
        msg = str(e)
    checks.append((f"a loop of three rules is reported with its path (got '{msg}')", "circular rules" in msg and "a -> b -> c -> a" in msg))
    try:
        L.run_rules([("a", "a + 1")], {})
        msg = ""
    except ValueError as e:
        msg = str(e)
    checks.append(("a rule that uses itself is reported as circular", "circular rules" in msg))
    for rules, ins, label in (([("a", "x + 1")], {}, "an unknown name"), ([("a", "1"), ("a", "2")], {}, "two rules with the same name"),
                              ([("x", "1")], {"x": 5}, "a rule with the name of an input"), ([("a", "__import__('os')")], {}, "an unsafe expression"),
                              ([("a", "9 ** 9 ** 9")], {}, "a huge power"), ([("a", "1 / 0")], {}, "a division by zero"), ([("a", "2 +")], {}, "a syntax error")):
        try:
            L.run_rules(rules, ins)
            raised = False
        except ValueError:
            raised = True
        checks.append((f"safety: the engine refuses {label}", raised))
    ok_n, ok_cap, ok_sp, ok_geo = True, True, True, True
    for load in (10, 60, 150, 300):
        for M in (8, 12, 16, 24):
            for od in (60.0, 114.3, 300.0):
                f = L.flange(load=float(load), M=M, od=od)
                ok_n &= f["n"] >= 4 and f["n"] % 2 == 0
                ok_cap &= f["n"] * f["f_bolt"] >= load
                ok_sp &= math.pi * f["pcd"] / f["n"] >= 2.5 * M - 1e-9
                ok_geo &= L.check_flange(f) == []
    checks.append(("for 48 flanges, the number of bolts is even and at least 4", ok_n))
    checks.append(("for 48 flanges, the bolts together carry at least the load", ok_cap))
    checks.append(("for 48 flanges, neighbouring bolts are at least 2.5 M apart along the bolt circle", ok_sp))
    checks.append(("for 48 flanges, every hole lies inside the ring and no two holes touch", ok_geo))
    checks.append(("a heavier load gives a heavier flange", L.flange(load=300.0)["mass"] > L.flange(load=150.0)["mass"] > L.flange(load=30.0)["mass"]))
    checks.append(("a load above what one ring of the minimum bolts carries makes the number of bolts jump", L.flange(load=300.0)["n"] > L.flange(load=60.0)["n"]))
    svg = L.flange_svg(v)
    cs, sc = L.circles_from_svg(svg)
    checks.append((f"the drawing has 2 + n circles: the rim, the bore and one per bolt (got {len(cs)})", len(cs) == 2 + v["n"]))
    holes = [c for c in cs if c[0] == "hole"]
    centre = next(c for c in cs if c[0] == "flange")
    rad = [math.hypot(h[1] - centre[1], h[2] - centre[2]) / sc for h in holes]
    checks.append(("every drawn hole centre is on the bolt circle", all(abs(r - v["pcd"] / 2) < 0.01 for r in rad)))
    ok = True
    for kw in ({}, {"load": 180.0}, {"load": 300.0, "M": 8}, {"M": 20, "od": 200.0}):
        f = L.flange(**kw)
        ok &= abs(L.area_from_drawing(L.flange_svg(f)) - L.area_formula(f)) < 0.005 * L.area_formula(f)
    checks.append(("validation: the area counted from the drawing agrees with the formula in the mass rule to within 0.5 percent for four flanges", ok))
    for bad, label in ((lambda: L.flange(M=13), "a bolt size that does not exist"), (lambda: L.flange(load=0.0), "a load of zero"),
                       (lambda: L.flange(colour="red"), "an unknown input"), (lambda: L.flange(od=-5.0), "a negative pipe diameter")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
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
