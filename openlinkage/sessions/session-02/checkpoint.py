"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # worked example: crank at 90 degrees for (a, b, c, d) = (4, 1, 4, 5)
    j = L.four_bar_joints(np.pi / 2, 4.0, 1.0, 4.0, 5.0)
    mu = L.transmission_angle(j)
    checks.append(("worked example: crank 90 degrees puts B at (1.882, 4.529) with transmission angle 53.13 degrees",
                   np.allclose(j[2], [1.8824, 4.5294], atol=1e-3) and abs(mu - 53.130) < 0.01))
    cosmu = (4.0 ** 2 + 5.0 ** 2 - 17.0) / (2 * 4.0 * 5.0)
    checks.append(("hand calculation: cos(mu) = (16 + 25 - 17) / 40 = 0.6 (diagonal squared is 17)",
                   abs(cosmu - 0.6) < 1e-12 and abs(np.degrees(np.arccos(cosmu)) - mu) < 1e-9))
    names = [L.grashof_class(*bars)[1] for _, bars in L.EXAMPLES]
    checks.append(("the five examples classify as crank-rocker, double-crank, double-rocker, triple-rocker, change-point",
                   names == ["crank-rocker", "double-crank", "double-rocker", "triple-rocker", "change-point"]))
    rng = np.random.default_rng(7)
    mism, tested = 0, 0
    while tested < 300:
        bars = rng.uniform(1.0, 6.0, 4)
        srt = np.sort(bars)
        margin = srt[1] + srt[2] - srt[0] - srt[3]
        if abs(margin) < 0.05:
            continue
        tested += 1
        predicted = margin > 0 and int(np.argmin(bars)) in (0, 1)
        if L.crank_turns_fully(*bars) != predicted:
            mism += 1
    checks.append(("Grashof's rule agrees with a brute-force full-turn test on 300 random linkages", mism == 0))
    worst, ok_newton = 0.0, True
    for t in np.linspace(0.1, 2 * np.pi - 0.1, 25):
        _, pa, pb, o4 = L.four_bar_joints(t, 4.0, 1.0, 4.0, 5.0)
        t3, t4 = np.arctan2(*(pb - pa)[::-1]), np.arctan2(*(pb - o4)[::-1])
        worst = max(worst, np.abs(L.loop_residual(t, t3, t4, 4.0, 1.0, 4.0, 5.0)).max())
        n3, n4 = L.solve_loop_newton(t, (t3 + 0.05, t4 - 0.05), 4.0, 1.0, 4.0, 5.0)
        ok_newton &= abs(n3 - t3) < 1e-10 and abs(n4 - t4) < 1e-10
    checks.append(("loop-closure error of the circle-circle solution is below 1e-12", worst < 1e-12))
    checks.append(("Newton's method on the loop equations lands on the same angles", ok_newton))
    lo, hi = L.transmission_range(4.0, 1.0, 4.0, 5.0)
    checks.append(("(4, 1, 4, 5) has transmission angles from 36.87 to 66.42 degrees (below the 40 degree guideline)",
                   abs(lo - 36.870) < 0.01 and abs(hi - 66.422) < 0.01))
    b5 = L.design_crank(4.0, 4.0, 5.0, 40.0)
    b35 = L.design_crank(4.0, 4.0, 3.5, 40.0)
    checks.append(("design: crank 1.3459 gives a 40 degree swing with d = 5; crank 1.0860 with d = 3.5",
                   abs(b5 - 1.3459) < 1e-4 and abs(b35 - 1.0860) < 1e-4
                   and abs(L.rocker_swing(4.0, b35, 4.0, 3.5) - 40.0) < 1e-9))
    lo5, _ = L.transmission_range(4.0, b5, 4.0, 5.0)
    lo35, hi35 = L.transmission_range(4.0, b35, 4.0, 3.5)
    checks.append(("design: d = 5 gives a smallest transmission angle of 31.91 degrees (fails 40); d = 3.5 gives 45.12 to 85.12 (passes)",
                   abs(lo5 - 31.91) < 0.01 and abs(lo35 - 45.12) < 0.01 and abs(hi35 - 85.12) < 0.01))
    swing_sampled = np.ptp([np.degrees(np.arctan2(*(L.four_bar_joints(t, 4.0, b35, 4.0, 3.5)[2]
                                                     - np.array([4.0, 0.0]))[::-1]))
                            for t in np.linspace(0, 2 * np.pi, 7201)])
    checks.append(("the designed swing also appears when the linkage is actually moved (sampled swing 40.00 degrees)",
                   abs(swing_sampled - 40.0) < 1e-3))
    try:
        L.design_crank(4.0, 4.0, 5.0, 170.0)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: an impossible swing (170 degrees) raises ValueError", raised))
    checks.append(("edge: equal sums s + l = p + q count as the change-point case, not as non-Grashof",
                   L.grashof_class(2, 1, 2, 1) == (True, "change-point")))
    checks.append(("F answers: (4, 3, 1, 3.5) is Grashof but its crank cannot turn; (2, 5, 4, 6) is a double-crank; d = 5 has mu up to 71.91",
                   L.grashof_class(4, 3, 1, 3.5)[0] and not L.crank_turns_fully(4, 3, 1, 3.5)
                   and L.grashof_class(2, 5, 4, 6) == (True, "double-crank") and abs(transmax(L, b5) - 71.91) < 0.01))
    ok_ends = True
    for bars in ((4.0, 1.0, 4.0, 5.0), (4.0, b5, 4.0, 5.0), (4.0, b35, 4.0, 3.5)):
        ts = np.linspace(0, 360, 361)
        mus = np.array([L.transmission_angle(L.four_bar_joints(np.radians(t), *bars)) for t in ts])
        ok_ends &= int(ts[mus.argmin()]) in (0, 360) and int(ts[mus.argmax()]) == 180
    checks.append(("the smallest transmission angle is at crank angle 0 and the largest at 180 degrees for these linkages", ok_ends))
    j90 = L.transmission_angle(L.four_bar_joints(0.0, 4.0, 1.0, 4.0, 5.0))
    checks.append(("(4, 1, 4, 5) at crank angle 0 has transmission angle 36.87 degrees", abs(j90 - 36.870) < 0.01))
    sw = L.rocker_swing(4.0, 1.1, 4.0, 3.5)
    checks.append(("app challenge: b = 1.1, d = 3.5 swings within 1 degree of 40 with mu between 44 and 86 degrees",
                   abs(sw - 40.0) < 1 and L.transmission_range(4.0, 1.1, 4.0, 3.5)[0] > 44))
    return checks


def transmax(L, b):
    return L.transmission_range(4.0, b, 4.0, 5.0)[1]


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
