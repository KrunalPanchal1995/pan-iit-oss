"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    zF, xD, xB = 0.10, 0.80, 0.02

    # validation against Session 1 (constant alpha)
    for a in (2.5, 4.0):
        n = L.total_reflux_stages(xD, xB, L.alpha_curve(a))
        checks.append((f"alpha = {a}: stepping at total reflux gives {n} stages = Fenske {L.fenske(xD, xB, a):.2f} rounded up",
                       n == int(np.ceil(L.fenske(xD, xB, a)))))
    big = L.mccabe_thiele(zF, xD, xB, 1e5, eq=L.alpha_curve(2.5))
    checks.append(("limit: a huge reflux ratio gives the total-reflux stage count",
                   big["stages"] == L.total_reflux_stages(xD, xB, L.alpha_curve(2.5))))

    # minimum reflux
    rmin, xp = L.min_reflux(zF, xD)
    ys = float(L.y_eq(zF))
    checks.append((f"worked example: Rmin = (0.80 - {ys:.3f}) / ({ys:.3f} - 0.10) = {rmin:.3f}, a feed pinch",
                   abs(rmin - (xD - ys) / (ys - zF)) < 1e-3 and abs(xp - zF) < 1e-3))
    r86, x86 = L.min_reflux(zF, 0.86)
    checks.append((f"tangent pinch: for xD = 0.86 Rmin = {r86:.2f} is above the feed-pinch formula and touches above the feed",
                   r86 > (0.86 - ys) / (ys - zF) + 0.3 and x86 > 0.5))
    bad_r = False
    try:
        L.mccabe_thiele(zF, xD, xB, 0.95 * rmin)
    except ValueError:
        bad_r = True
    checks.append(("below the minimum reflux the column cannot be built (ValueError)", bad_r))

    # the design
    d = L.design(zF, xD, xB, 1.5)
    mt = L.mccabe_thiele(zF, xD, xB, d["R"])
    checks.append((f"worked example: R = 1.5 Rmin = {d['R']:.3f} needs 13 stages with the feed on stage 12",
                   d["stages"] == 13 and d["feed_stage"] == 12 and abs(d["R"] - 1.587) < 2e-3))
    fl = d["flows"]
    checks.append(("material balance: D = 10.26 kmol/h and ethanol in = ethanol out",
                   abs(fl["D"] - 800 / 78) < 1e-9 and abs(fl["D"] * xD + fl["B"] * xB - 100 * zF) < 1e-9))
    checks.append(("flow balances: V = L + D at the top and V' = L' - B at the bottom",
                   abs(fl["V"] - fl["L"] - fl["D"]) < 1e-9 and abs(fl["Vb"] - (fl["Lb"] - fl["B"])) < 1e-9))
    checks.append((f"hand calculation: reboiler duty = 26.53 kmol/h x 40 kJ/mol / 3.6 = {d['duty_kw']:.1f} kW",
                   abs(d["duty_kw"] - (d["R"] + 1) * (800 / 78) * 40 / 3.6) < 1e-6 and abs(d["duty_kw"] - 294.8) < 0.2))
    checks.append(("every stage is at equilibrium: y = y_eq(x) on each stage",
                   np.allclose(L.y_eq(mt["x"]), mt["y"], atol=2e-4)))
    rect = mt["y"][1:mt["feed_stage"] - 1]
    checks.append(("each rectifying step lands on the rectifying line",
                   np.allclose(rect, d["R"] / (d["R"] + 1) * mt["x"][:mt["feed_stage"] - 2] + xD / (d["R"] + 1))))
    checks.append(("the last stage reaches xB and the one above does not", mt["x"][-1] <= xB < mt["x"][-2]))
    t = L.t_bubble(mt["x"])
    checks.append((f"temperature rises down the column, from {t[0]:.1f} C at the top to {t[-1]:.1f} C at the bottom",
                   bool(np.all(np.diff(t) > 0)) and 78 < t[0] < 79.5 and 95 < t[-1] < 100))

    # trends and limits
    stages = [L.mccabe_thiele(zF, xD, xB, f * rmin)["stages"] for f in (1.1, 1.3, 1.5, 2.0, 3.0)]
    checks.append((f"more reflux never needs more stages: {stages}", all(a >= b for a, b in zip(stages, stages[1:]))))
    nmin = L.total_reflux_stages(xD, xB)
    checks.append((f"no design beats the total-reflux minimum of {nmin} stages", min(stages) >= nmin))
    factors = np.round(np.arange(1.05, 3.01, 0.05), 2)
    costs = [L.design(zF, xD, xB, f)["cost"] for f in factors]
    k = int(np.argmin(costs))
    checks.append((f"mini-project: the cheapest reflux is inside the range (R = {factors[k]:.2f} x Rmin), not at an end",
                   0 < k < len(factors) - 1 and abs(factors[k] - 1.5) < 1e-9))
    checks.append(("purer bottoms need more stages", L.design(zF, xD, 0.005, 1.5)["stages"] > d["stages"]))

    # the azeotrope wall
    checks.append((f"the model azeotrope is at x = {L.X_AZEO:.3f} (measured 0.894)", abs(L.X_AZEO - 0.894) < 0.03))
    bad = 0
    for call in (lambda: L.mccabe_thiele(zF, 0.92, xB, 10.0), lambda: L.min_reflux(zF, 0.95),
                 lambda: L.column_flows(0.10, 0.05, 0.02, 2.0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("a target beyond the azeotrope and invalid inputs raise ValueError", bad == 3))
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
