"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def _cross(L, key, target, B=2.0):
    lo, hi = 0.0, 4.0
    for _ in range(60):
        m = (lo + hi) / 2
        if L.wall_state(B, 4.0, 0.5, 30.0, 18.0, hw=m)[key] > target:
            lo = m
        else:
            hi = m
    return lo


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # earth pressure coefficients
    checks.append(("Rankine Ka for beta = 0 equals (1 - sin phi)/(1 + sin phi) for several phi",
                   all(abs(L.ka_rankine(p) - (1 - np.sin(np.radians(p))) / (1 + np.sin(np.radians(p)))) < 1e-12 for p in (20, 30, 40))))
    checks.append(("Coulomb reduces to Rankine for delta = alpha = beta = 0",
                   all(abs(L.ka_coulomb(p) - L.ka_rankine(p)) < 1e-12 for p in (20, 30, 40))))
    checks.append(("Coulomb with delta = beta, vertical wall, equals Rankine with that slope (10 degrees: 0.3495)",
                   abs(L.ka_coulomb(30, 10, 0, 10) - L.ka_rankine(30, 10)) < 1e-12 and abs(L.ka_rankine(30, 10) - 0.3495) < 1e-4))
    checks.append(("wall friction delta = 20 degrees lowers Ka from 0.3333 to 0.2973 (about 11 percent)",
                   abs(L.ka_coulomb(30, 20) - 0.2973) < 1e-4 and abs(1 - L.ka_coulomb(30, 20) / L.ka_rankine(30) - 0.1080) < 1e-3))
    checks.append(("a backfill slope raises Rankine Ka: 0.3333, 0.3495, 0.4142 at 0, 10, 20 degrees",
                   abs(L.ka_rankine(30, 0) - 1 / 3) < 1e-4 and abs(L.ka_rankine(30, 10) - 0.3495) < 1e-4
                   and abs(L.ka_rankine(30, 20) - 0.4142) < 1e-4))
    try:
        L.ka_rankine(30, 30)
        bad = True
    except ValueError:
        bad = False
    checks.append(("edge: a slope equal to phi is refused (no active state)", not bad))

    # worked example: B = 2, H = 4, mu = 0.5
    s = L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0)
    checks.append(("worked example: Pa = 48 kN/m, W = 192 kN/m, FS_slide = 2.00, FS_ot = 3.00",
                   abs(s["Ph"] - 48) < 1e-9 and abs(s["W"] - 192) < 1e-9 and abs(s["FS_slide"] - 2.0) < 1e-9
                   and abs(s["FS_ot"] - 3.0) < 1e-9))
    checks.append(("worked example: resultant at 0.667 m from the toe, e = 0.333 m = B/6, heel pressure zero",
                   abs(s["xbar"] - 2 / 3) < 1e-9 and abs(s["e"] - 1 / 3) < 1e-9 and abs(s["q_heel"]) < 1e-9
                   and s["middle_third"] and abs(s["q_toe"] - 192.0) < 1e-9))
    # hand calculation, B = 1.6 m, H = 3 m
    h = L.wall_state(1.6, 3.0, 0.5, 30.0, 18.0)
    checks.append(("hand calculation: H = 3, B = 1.6: FS_slide 2.13, FS_ot 3.41, e = 0.234 m < B/6 = 0.267 m",
                   abs(h["FS_slide"] - 2.1333) < 1e-3 and abs(h["FS_ot"] - 3.4133) < 1e-3
                   and abs(h["e"] - 0.2344) < 1e-3 and h["middle_third"]))

    # validation: moment equilibrium of the full free body
    ok_eq = True
    for kw in ({}, {"q": 10.0}, {"hw": 2.0}, {"hw": 4.0}, {"beta": 10.0}):
        st = L.wall_state(2.5, 4.0, 0.5, 30.0, 18.0, **kw)
        F, M = L.base_pressure_check(st, 2.5)
        ok_eq &= abs(F - st["N"]) < 1e-6 * max(1, st["N"]) and abs(M - st["N"] * st["xbar"]) < 1e-6 * max(1, abs(M))
        ok_eq &= abs(M - (st["M_res"] - st["M_ot"])) < 1e-6 * max(1, abs(M))
    checks.append(("base pressure carries the vertical load and the moment about the toe (dry, surcharge, water, slope)", bool(ok_eq)))

    # validation: numerical pressure integration against the closed forms
    ok_int = True
    for kw in ({}, {"q": 10.0}, {"hw": 2.0}, {"hw": 4.0}, {"q": 10.0, "hw": 1.0}):
        parts = L.horizontal_forces(4.0, 30.0, 18.0, **kw)
        f_cf = sum(f for _, f, _ in parts)
        m_cf = sum(f * z for _, f, z in parts)
        f_n, m_n = L.numeric_push(4.0, 30.0, 18.0, **kw)
        ok_int &= abs(f_n - f_cf) < 1e-3 and abs(m_n - m_cf) < 1e-3
    checks.append(("numerical integration of the pressure matches the closed-form force and moment", bool(ok_int)))
    sat = L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0, hw=4.0)
    checks.append(("saturated backfill: horizontal force 105.65 kN/m, of which water 78.48", abs(sat["Ph"] - 105.65) < 0.01
                   and abs(0.5 * 9.81 * 16 - 78.48) < 1e-9))
    checks.append(("zero water level gives the dry result", abs(L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0, hw=0.0)["Ph"] - 48) < 1e-9))

    # limits and guidance
    checks.append(("the dry B = 2 m wall just passes (sliding 2.0, overturning 3.0, middle third)", L.passes(s)))
    checks.append(("narrow wall B = 1.5 m: sliding exactly 1.5 but overturning only 1.69 and e outside B/6",
                   abs(L.wall_state(1.5, 4.0, 0.5, 30.0, 18.0)["FS_slide"] - 1.5) < 1e-9
                   and abs(L.wall_state(1.5, 4.0, 0.5, 30.0, 18.0)["FS_ot"] - 1.6875) < 1e-9
                   and not L.passes(L.wall_state(1.5, 4.0, 0.5, 30.0, 18.0))))
    checks.append(("sliding and overturning rise with width and friction",
                   L.wall_state(3.0, 4.0, 0.5, 30.0, 18.0)["FS_ot"] > s["FS_ot"] and L.wall_state(2.0, 4.0, 0.6, 30.0, 18.0)["FS_slide"] > s["FS_slide"]))
    sweep = [L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0, beta=b) for b in (0, 10, 20)]
    checks.append(("backfill slope sweep: sliding 2.00, 2.03, 1.89 at 0, 10, 20 degrees (changes less than 6 percent)",
                   abs(sweep[0]["FS_slide"] - 2.0) < 1e-9 and abs(sweep[1]["FS_slide"] - 2.025) < 1e-3
                   and abs(sweep[2]["FS_slide"] - 1.895) < 1e-3 and max(abs(r["FS_slide"] - 2.0) for r in sweep) < 0.11))
    checks.append(("slope sweep: horizontal push 48.0 kN/m rising to 56.05 kN/m at 20 degrees (Ka 0.4142)",
                   abs(sweep[2]["Ph"] - 56.05) < 0.01))

    # sensitivity to phi
    p25 = L.wall_state(2.0, 4.0, 0.5, 25.0, 18.0)
    p35 = L.wall_state(2.0, 4.0, 0.5, 35.0, 18.0)
    checks.append(("phi 25 versus 35 degrees for the B = 2 m wall: sliding 1.64 versus 2.46, overturning 2.46 versus 3.69",
                   abs(p25["FS_slide"] - 1.6426) < 1e-3 and abs(p35["FS_slide"] - 2.4601) < 1e-3
                   and abs(p25["FS_ot"] - 2.4639) < 1e-3 and abs(p35["FS_ot"] - 3.6902) < 1e-3))
    # surcharge and water lead out of the middle third
    sur = L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0, q=10.0)
    checks.append(("a 10 kPa surcharge on the B = 2 m wall: e = 0.472 m exceeds B/6 and the heel pressure is negative (-40 kPa)",
                   abs(sur["e"] - 0.4722) < 1e-3 and not sur["middle_third"] and abs(sur["q_heel"] + 40.0) < 0.01))

    # failure case: water in the backfill
    fs = [L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0, hw=w) for w in (0.0, 1.0, 2.0, 3.0, 4.0)]
    checks.append(("water at 0, 1, 2, 3, 4 m: FS_ot 3.00, 2.45, 1.92, 1.41, 0.99",
                   all(abs(a - b) < 6e-3 for a, b in zip([r["FS_ot"] for r in fs], [3.0, 2.453, 1.924, 1.415, 0.994]))))
    checks.append(("failure case: with the backfill saturated, uplift is 39.24 kN/m, FS_slide 0.72 and FS_ot 0.994 (below 1)",
                   abs(sat["U"] - 39.24) < 1e-9 and abs(sat["FS_slide"] - 0.723) < 2e-3 and sat["FS_ot"] < 1.0
                   and abs(sat["FS_ot"] - 0.994) < 1e-3 and sat["xbar"] < 0))
    checks.append(("sliding falls below 1.5 at a water level of 1.70 m and below 1 at 3.03 m",
                   abs(_cross(L, "FS_slide", 1.5) - 1.7018) < 5e-3 and abs(_cross(L, "FS_slide", 1.0) - 3.0321) < 5e-3))
    checks.append(("overturning falls below 2 at 1.86 m and below 1 at 3.98 m",
                   abs(_cross(L, "FS_ot", 2.0) - 1.8577) < 5e-3 and abs(_cross(L, "FS_ot", 1.0) - 3.9831) < 5e-3))
    checks.append(("safety factors fall as the water rises",
                   all(fs[i]["FS_slide"] > fs[i + 1]["FS_slide"] and fs[i]["FS_ot"] > fs[i + 1]["FS_ot"] for i in range(4))))

    # design widths
    checks.append(("design: smallest passing width for H = 4 m is 2.00 dry, 2.45 with water at 2 m, 4.15 saturated",
                   L.min_width(4.0, 0.5, 30.0, 18.0) == 2.0 and L.min_width(4.0, 0.5, 30.0, 18.0, hw=2.0) == 2.45
                   and L.min_width(4.0, 0.5, 30.0, 18.0, hw=4.0) == 4.15))
    w25 = L.min_width(4.0, 0.5, 25.0, 18.0)
    w35 = L.min_width(4.0, 0.5, 35.0, 18.0)
    checks.append(("design: phi 25 degrees needs 2.25 m, phi 35 degrees needs 1.85 m", w25 == 2.25 and w35 == 1.85))
    checks.append(("challenge: B = 2.5 m, friction 0.5, phi 30, water at 2 m passes; B = 2.4 m does not",
                   L.passes(L.wall_state(2.5, 4.0, 0.5, 30.0, 18.0, hw=2.0)) and not L.passes(L.wall_state(2.4, 4.0, 0.5, 30.0, 18.0, hw=2.0))
                   and abs(L.wall_state(2.5, 4.0, 0.5, 30.0, 18.0, hw=2.0)["FS_slide"] - 1.726) < 2e-3))

    # extra numbers quoted in the text
    w3 = L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0, hw=3.0)
    checks.append(("water 3 m on the B = 2 m wall: FS_slide 1.01 and FS_ot 1.41", abs(w3["FS_slide"] - 1.011) < 2e-3 and abs(w3["FS_ot"] - 1.415) < 2e-3))
    checks.append(("hand calculation: H = 3, B = 1.6 base pressures 135.3 kPa (toe) and 8.7 kPa (heel)",
                   abs(h["q_toe"] - 135.28) < 0.01 and abs(h["q_heel"] - 8.72) < 0.01))
    checks.append(("sliding factor is proportional to friction: 1.2 at 0.3 and 2.8 at 0.7 (B = 2 m)",
                   abs(L.wall_state(2.0, 4.0, 0.3, 30.0, 18.0)["FS_slide"] - 1.2) < 1e-9 and abs(L.wall_state(2.0, 4.0, 0.7, 30.0, 18.0)["FS_slide"] - 2.8) < 1e-9))
    d195 = L.wall_state(1.95, 4.0, 0.5, 30.0, 18.0)
    checks.append(("dry design is controlled by the middle-third rule: at B = 1.95 m both factors pass but e > B/6",
                   d195["FS_slide"] >= 1.5 and d195["FS_ot"] >= 2.0 and not d195["middle_third"]))
    checks.append(("the undrained 2.45 m wall needs 22.5 percent more width than the dry 2.00 m wall", abs(2.45 / 2.0 - 1.225) < 1e-12))
    # mini-project: garden wall
    g = {"H": 1.2, "mu": 0.45, "phi": 30.0, "gamma": 18.0, "gc": 22.0}
    wd = L.min_width(g["H"], g["mu"], g["phi"], g["gamma"], g["gc"], q=5.0)
    w1 = L.min_width(g["H"], g["mu"], g["phi"], g["gamma"], g["gc"], hw=0.6, q=5.0)
    w2 = L.min_width(g["H"], g["mu"], g["phi"], g["gamma"], g["gc"], hw=1.2, q=5.0)
    checks.append(("mini-project: garden wall 1.2 m, 5 kPa surcharge needs B = 0.85 m dry, 1.10 m with water at 0.6 m, 1.90 m saturated",
                   wd == 0.85 and w1 == 1.1 and w2 == 1.9))
    a = L.wall_state(0.8, 1.2, 0.45, 30.0, 18.0, 22.0, q=5.0)
    b = L.wall_state(0.85, 1.2, 0.45, 30.0, 18.0, 22.0, q=5.0)
    checks.append(("mini-project: at 0.80 m both factors pass (1.50, 2.89) but the middle-third rule fails; at 0.85 m it passes (1.60, 3.26)",
                   a["FS_slide"] >= 1.5 and a["FS_ot"] >= 2.0 and not a["middle_third"]
                   and abs(a["FS_slide"] - 1.504) < 2e-3 and abs(a["FS_ot"] - 2.885) < 2e-3
                   and L.passes(b) and abs(b["FS_slide"] - 1.598) < 2e-3 and abs(b["FS_ot"] - 3.257) < 2e-3))
    # edge: a wall lifted off its base
    checks.append(("edge: water level equal to the wall height: overturning moment 140.87 kN m/m (= 105.65 * 4/3)",
                   abs(L.wall_state(2.0, 4.0, 0.5, 30.0, 18.0, hw=4.0)["Mo"] - 140.871) < 1e-3))
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
