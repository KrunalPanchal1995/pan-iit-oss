"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    out = L.solve_plant(100.0, 0.6)
    checks.append((f"worked example: F = 100, r = 0.6 gives S = 250, R = 150, P = 100 (got {out['S']:.1f}, {out['R']:.1f}, {out['P']:.1f})",
                   abs(out["S"] - 250.0) < 1e-9 and abs(out["R"] - 150.0) < 1e-9 and abs(out["P"] - 100.0) < 1e-9))
    checks.append(("hand calculation: S = F / (1 - r) = 100 / 0.4 = 250", abs(100.0 / 0.4 - out["S"]) < 1e-9 and abs(L.amplification(0.6) - 2.5) < 1e-12))
    checks.append(("overall balance: product equals fresh feed at steady state", abs(out["P"] - 100.0) < 1e-9))
    A, b = L.plant_equations(100.0, 0.6)
    checks.append(("3 unknowns and 3 equations (square system)", A.shape == (3, 3) and b.shape == (3,)))
    checks.append(("the solution satisfies every box rule (residual below 1e-9)", float(np.max(np.abs(A @ np.array([out["S"], out["P"], out["R"]]) - b))) < 1e-9))
    R, rounds, hist = L.go_round(100.0, 0.6)
    checks.append((f"guess and go round: first guesses 60, 96, 117.6 (got {hist[0]:.1f}, {hist[1]:.1f}, {hist[2]:.1f})",
                   abs(hist[0] - 60.0) < 1e-9 and abs(hist[1] - 96.0) < 1e-9 and abs(hist[2] - 117.6) < 1e-9))
    checks.append((f"going round reaches R = 150 in 37 rounds at tolerance 1e-6 (got {rounds})", rounds == 37 and abs(R - 150.0) < 1e-4))
    checks.append(("going round and solving together agree (r = 0.5, 0.8)",
                   all(abs(L.go_round(100.0, r, tol=1e-10)[0] - L.solve_plant(100.0, r)["R"]) < 1e-6 for r in (0.5, 0.8))))
    s9 = L.solve_plant(100.0, 0.9)
    checks.append((f"r = 0.9: separator flow 1000 mol/s, ten times the feed (got {s9['S']:.0f})", abs(s9["S"] - 1000.0) < 1e-6 and abs(L.amplification(0.9) - 10.0) < 1e-9))
    checks.append((f"r = 0.9 needs 175 rounds at tolerance 1e-6 (got {L.go_round(100.0, 0.9)[1]})", L.go_round(100.0, 0.9)[1] == 175))
    r0 = L.solve_plant(100.0, 0.0)
    checks.append(("edge: r = 0 means no recycle, S = P = 100 and R = 0", abs(r0["S"] - 100.0) < 1e-12 and r0["R"] == 0.0 and abs(r0["P"] - 100.0) < 1e-12))
    try:
        L.solve_plant(100.0, 1.0)
        bad = False
    except ValueError:
        bad = True
    checks.append(("edge: r = 1 is refused with a clear message (nothing could leave)", bad))
    checks.append(("flows scale with the feed: F = 250 gives S = 625 at r = 0.6", abs(L.solve_plant(250.0, 0.6)["S"] - 625.0) < 1e-9))
    checks.append(("figure values: S/F is 2, 5 and 20 at r = 0.5, 0.8, 0.95; R is 100, 400, 900 at r = 0.5, 0.8, 0.9",
                   [round(L.amplification(r), 6) for r in (0.5, 0.8, 0.95)] == [2.0, 5.0, 20.0]
                   and [round(L.solve_plant(100.0, r)["R"], 6) for r in (0.5, 0.8, 0.9)] == [100.0, 400.0, 900.0]))
    q = L.solve_plant(100.0, 0.75)
    checks.append(("exercise: F = 100 and r = 0.75 give S = 400, R = 300, P = 100", abs(q["S"] - 400) < 1e-9 and abs(q["R"] - 300) < 1e-9 and abs(q["P"] - 100) < 1e-9))
    checks.append(("design: a separator limited to 400 mol/s allows r = 1 - 100/400 = 0.75 at F = 100 and r = 0.625 at F = 150",
                   abs(L.solve_plant(150.0, 0.625)["S"] - 400.0) < 1e-9 and abs(1 - 100 / 400 - 0.75) < 1e-12))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
