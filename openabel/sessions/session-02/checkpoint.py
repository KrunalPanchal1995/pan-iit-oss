"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    g = lambda r: L.gauss_eps(r, 1.0)
    exact = float(L.gauss_abel_exact(1.0, 1.0))
    checks.append((f"worked example: Gaussian a = 1 mm at y = 1 mm gives sqrt(pi)/e = 0.652 (exact {exact:.4f})",
                   abs(exact - np.sqrt(np.pi) / np.e) < 1e-12 and abs(exact - 0.6520) < 1e-3))
    num = float(L.abel_forward(g, 1.0)[0])
    checks.append((f"worked example: numerical integration reproduces it (got {num:.4f})", abs(num - exact) < 1e-4))
    y = np.linspace(0, 3.5, 15)
    err = np.max(np.abs(L.abel_forward(g, y) - L.gauss_abel_exact(y, 1.0)))
    checks.append((f"integration matches the exact Gaussian pair on 15 offsets (largest error {err:.1e})", err < 1e-4))
    checks.append(("a line of sight outside the region sees nothing: I(y >= R) = 0", float(L.abel_forward(g, L.R_MM)[0]) == 0.0))
    # hand calculation of the 3-ring matrix (R = 3 mm, dr = 1 mm)
    W = L.ring_matrix(3, 3.0)
    hand = np.array([[2.0, 2.0, 2.0], [0.0, 2 * np.sqrt(3.0), 2 * (np.sqrt(8.0) - np.sqrt(3.0))], [0.0, 0.0, 2 * np.sqrt(5.0)]])
    checks.append(("hand calculation: the 3-ring matrix has rows (2, 2, 2), (0, 3.464, 2.192), (0, 0, 4.472)", np.allclose(W, hand, atol=1e-9)))
    checks.append(("W is zero below the diagonal (a line of sight at y never meets rings inside y)", np.allclose(np.tril(L.ring_matrix(12), -1), 0.0)))
    # uniform emission: the ring model must reproduce the chord exactly
    yy, I = L.ring_forward(lambda r: np.ones_like(r), 20)
    checks.append(("uniform emission through rings gives the chord 2 sqrt(R^2 - y^2) exactly",
                   np.allclose(I, 2 * np.sqrt(L.R_MM ** 2 - yy ** 2), atol=1e-9)))
    e10, e20, e40 = (L.ring_error(1.0, n) for n in (10, 20, 40))
    checks.append((f"more rings, smaller error: {100 * e10:.1f}% > {100 * e20:.1f}% > {100 * e40:.1f}%", e10 > e20 > e40))
    n1, n05 = L.smallest_rings(1.0), L.smallest_rings(0.5)
    checks.append((f"design: a = 1 mm needs {n1} rings for an error below 1% of peak (33 rings, 66 pixels across)",
                   n1 == 33 and L.ring_error(1.0, 32) >= 0.01 > L.ring_error(1.0, 33)))
    checks.append((f"design: a narrower flame (a = 0.5 mm) needs more rings ({n05} > {n1})", n05 > n1))
    ring = L.abel_forward(lambda r: L.ring_eps(r, 1.5, 0.4), np.array([0.0, 1.5, 2.5]), n=1000)
    checks.append(("a ring-shaped flame is bright at its limb: I(1.5) > I(0) > I(2.5)", ring[1] > ring[0] > ring[2]))
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
