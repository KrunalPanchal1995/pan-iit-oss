"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("like charges repel", L.force_direction(1, 2) == "repel" and L.force_direction(-1, -3) == "repel"))
    checks.append(("opposite charges attract", L.force_direction(1, -1) == "attract"))
    checks.append(("a zero charge feels nothing (edge case)", L.force_direction(0, 5) == "none"))

    mid_like = L.field_at((0.0, 0.0), L.LIKE)
    checks.append(("two equal positive charges: the field cancels in the middle", np.allclose(mid_like, 0)))
    mid_dip = L.field_at((0.0, 0.0), L.DIPOLE)
    checks.append(("dipole: the field in the middle points from + towards - and is 2", np.allclose(mid_dip, [2.0, 0.0])))
    checks.append(("a point exactly on a charge does not crash", np.all(np.isfinite(L.field_at((-1.0, 0.0), L.DIPOLE)))))
    Ex, Ey = L.field_grid(L.DIPOLE, np.linspace(-3, 3, 7), np.linspace(-3, 3, 7))
    checks.append(("field grid is finite everywhere", bool(np.all(np.isfinite(Ex)) and np.all(np.isfinite(Ey)))))
    far = L.field_at((50.0, 0.0), L.LIKE)
    checks.append(("far from two like charges the field is about that of one charge of size 2 (2/r^2)",
                   abs(far[0] - 2 / 50 ** 2) / (2 / 50 ** 2) < 0.01))

    # worked example: FM radio at 100 MHz
    lam = L.wavelength(100e6)
    checks.append((f"worked example: an FM station at 100 MHz has wavelength about 3.0 m (got {lam:.3f})", abs(lam - 2.998) < 0.001))
    checks.append(("frequency and wavelength are inverse of each other", abs(L.frequency(L.wavelength(5e8)) - 5e8) < 1))
    checks.append(("hand calculation: 2.4 GHz wifi wavelength is 0.125 m", abs(L.wavelength(2.4e9) - 0.125) < 0.001))
    checks.append(("green light 600 THz is about 500 nm", abs(L.wavelength(600e12) - 500e-9) < 2e-9))
    checks.append(("sound is much slower: 440 Hz in air gives 0.78 m", abs(L.wavelength(440, 343.0) - 0.78) < 0.001))

    x = np.linspace(-2, 12, 1401)
    checks.append(("the bump's peak moves at v: x = 10 at t = 5 when v = 2", abs(L.peak_position(x, 5.0, 2.0) - 10.0) < 0.02))
    checks.append(("at t = 0 the bump is at x = 0", abs(L.peak_position(x, 0.0, 2.0)) < 0.02))
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
