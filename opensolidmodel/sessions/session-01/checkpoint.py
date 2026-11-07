"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r = L.rebuild(L.PLATE)
    p = r["params"]
    checks.append((f"worked example: hole spacing 24.0 mm (got {p['s']:.1f})", abs(p["s"] - 24.0) < 1e-9))
    checks.append((f"worked example: hole diameter 9.6 mm (got {p['dia']:.1f})", abs(p["dia"] - 9.6) < 1e-9))
    checks.append((f"worked example: volume 36 084 mm3 (got {r['volume']:.0f})", abs(r["volume"] - 36083.8) < 0.5))
    checks.append((f"worked example: mass 0.283 kg (got {r['mass']:.3f})", abs(r["mass"] - 0.2833) < 0.0005))
    checks.append((f"worked example: 10 faces (6 outer + 4 hole walls) (got {r['faces']})", r["faces"] == 10))
    r6 = L.rebuild(L.PLATE, n=6, w=140.0)
    checks.append((f"customer change n = 6, w = 140: spacing 20 mm and hole diameter 8 mm (got {r6['params']['s']:.1f}, {r6['params']['dia']:.1f})",
                   abs(r6["params"]["s"] - 20.0) < 1e-9 and abs(r6["params"]["dia"] - 8.0) < 1e-9))
    checks.append((f"customer change: mass 0.333 kg (got {r6['mass']:.3f})", abs(r6["mass"] - 0.3327) < 0.0005))
    ok = True
    for w, d, h, n, ratio in ((120, 40, 8, 4, 0.4), (90, 30, 5, 2, 0.3), (200, 50, 10, 9, 0.5)):
        q = L.rebuild(L.PLATE, w=w, d=d, h=h, n=n, ratio=ratio)
        s = w / (n + 1)
        by_hand = w * d * h - n * 3.141592653589793 / 4 * (ratio * s) ** 2 * h
        ok &= abs(q["volume"] - by_hand) < 1e-6 * by_hand
    checks.append(("validation: volume = w d h - n (pi / 4) dia^2 h for three different plates", ok))
    checks.append(("a rebuild never changes the stored recipe", L.PLATE["params"]["w"] == 120.0 and L.PLATE["params"]["n"] == 4))
    ra = L.rebuild(L.PLATE, ratio=0.5)
    checks.append(("changing ratio changes the diameter but not the spacing", ra["params"]["dia"] > p["dia"] and ra["params"]["s"] == p["s"]))
    rw = L.rebuild(L.PLATE, w=150.0)
    checks.append(("changing w changes both the spacing and the diameter", rw["params"]["s"] > p["s"] and rw["params"]["dia"] > p["dia"]))
    checks.append(("bigger holes mean a lighter plate", L.rebuild(L.PLATE, ratio=0.5)["mass"] < r["mass"] < L.rebuild(L.PLATE, ratio=0.3)["mass"]))
    ms = [L.rebuild(L.PLATE, n=k)["mass"] for k in range(1, 8)]
    checks.append(("with the diameter tied to the spacing, one hole is the lightest choice and more holes make the plate heavier", ms[0] == min(ms) and ms == sorted(ms)))
    checks.append(("equation evaluator: 2 * (3 + 4) = 14 and sqrt(w) * 2 = 8 for w = 16",
                   L.evaluate("2 * (3 + 4)", {}) == 14 and abs(L.evaluate("sqrt(w) * 2", {"w": 16.0}) - 8.0) < 1e-12))
    for expr, label in (("__import__('os').system('echo hi')", "a function call that is not on the list"), ("().__class__", "an attribute access"),
                        ("9 ** 9 ** 9", "a huge power"), ("1 / 0", "division by zero"), ("2 +", "a syntax error"), ("unknown_name * 2", "an unknown name")):
        try:
            L.evaluate(expr, {})
            raised = False
        except ValueError:
            raised = True
        checks.append((f"safety: the evaluator refuses {label}", raised))
    for bad, label in ((lambda: L.rebuild(L.PLATE, n=2.5), "a fractional number of holes"), (lambda: L.rebuild(L.PLATE, ratio=1.2), "holes wider than their spacing"),
                       (lambda: L.rebuild(L.PLATE, w=-5.0), "a negative width"), (lambda: L.rebuild(L.PLATE, dia=5.0), "overwriting a value that an equation owns"),
                       (lambda: L.rebuild(L.PLATE, n=-1), "n = -1 (the spacing equation divides by zero)")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
    checks.append(("design: ratio 0.44 gives at most 0.28 kg and ratio 0.43 does not",
                   L.rebuild(L.PLATE, ratio=0.44)["mass"] <= 0.28 < L.rebuild(L.PLATE, ratio=0.43)["mass"]))
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
