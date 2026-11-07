"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    a, b = L.collide(2, 4, 1, -1, 0.5)
    checks.append((f"worked example: speeds 1.5 and 4.0 m/s (got {a:.3f} and {b:.3f})", abs(a - 1.5) < 1e-9 and abs(b - 4.0) < 1e-9))
    checks.append(("worked example: momentum 7 kg m/s before and after", abs(2 * a + 1 * b - 7) < 1e-9))
    lost = L.energy_lost(2, 4, 1, -1, 0.5)
    checks.append((f"worked example: 6.25 J lost (got {lost:.2f})", abs(lost - 6.25) < 1e-9))
    checks.append(("worked example: lost = KE before - KE after = 16.5 - 10.25 J", abs((L.ke(2, 4) + L.ke(1, -1)) - (L.ke(2, a) + L.ke(1, b)) - lost) < 1e-9))
    checks.append(("e = 0 reproduces the sticking speed", all(abs(x - (2 * 4 + 1 * -1) / 3) < 1e-12 for x in L.collide(2, 4, 1, -1, 0))))
    checks.append(("e = 1 keeps the kinetic energy", abs(L.energy_lost(2, 4, 1, -1, 1.0)) < 1e-12))
    ok = True
    for m1, v1, m2, v2, e in ((2, 4, 1, -1, 0.3), (1, 5, 4, -2, 0.9), (5, 1, 2, 3, 0.0)):
        x, y = L.collide(m1, v1, m2, v2, e)
        ok &= abs((y - x) - e * (v1 - v2)) < 1e-9 and abs(m1 * x + m2 * y - (m1 * v1 + m2 * v2)) < 1e-9
    checks.append(("the speed of separation equals e times the speed of approach, and momentum is kept", ok))
    checks.append(("a 1 m drop and 0.64 m rebound give e = 0.80", abs(L.restitution_from_heights(1.0, 0.64) - 0.8) < 1e-12))
    checks.append((f"a 10 g bullet in a 2 kg block that rises 12 cm has speed 308 m/s (got {L.bullet_speed(0.010, 2.0, 0.12):.0f})", abs(L.bullet_speed(0.010, 2.0, 0.12) - 308.4) < 0.5))
    a2, b2 = L.collide(0.5, 6, 1.5, 0, 0.8)
    checks.append((f"question B: speeds -2.1 and 2.7 m/s, 2.43 J lost (got {a2:.2f}, {b2:.2f}, {L.energy_lost(0.5, 6, 1.5, 0, 0.8):.2f})",
                   abs(a2 + 2.1) < 1e-9 and abs(b2 - 2.7) < 1e-9 and abs(L.energy_lost(0.5, 6, 1.5, 0, 0.8) - 2.43) < 1e-9))
    checks.append(("design: m1 = 4 kg, m2 = 1 kg, v1 = 5 m/s, e = 1 sends body 2 away at 8 m/s with no loss",
                   abs(L.collide(4, 5, 1, 0, 1.0)[1] - 8) < 1e-9 and abs(L.energy_lost(4, 5, 1, 0, 1.0)) < 1e-12))
    for bad, label in ((lambda: L.collide(1, 1, 1, 0, 1.2), "e above 1"), (lambda: L.collide(1, 1, 1, 0, -0.1), "a negative e"),
                       (lambda: L.restitution_from_heights(1.0, 1.5), "a rebound higher than the drop"), (lambda: L.collide(0, 1, 1, 0, 0.5), "mass 0")):
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
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
