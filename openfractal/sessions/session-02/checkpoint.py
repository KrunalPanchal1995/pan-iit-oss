"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    z, w = 3 + 4j, 1 + 1j
    checks.append(("worked example: |3+4i| = 5 and arg(3+4i) = 53.13 degrees",
                   abs(L.modulus(z) - 5.0) < 1e-12 and abs(L.argument_deg(z) - 53.1301) < 1e-3))
    checks.append(("|z w| = |z| |w| and arg(z w) = arg z + arg w",
                   abs(L.modulus(z * w) - L.modulus(z) * L.modulus(w)) < 1e-12
                   and abs(L.argument_deg(z * w) - (L.argument_deg(z) + L.argument_deg(w))) < 1e-9))
    checks.append(("multiplying by i adds 90 degrees to the argument (45 -> 135)", abs(L.argument_deg(1j * (1 + 1j)) - 135.0) < 1e-9))
    checks.append(("c = 1 escapes at step 3, c = 0.3 at step 12", L.escape_time(1, 100) == 3 and L.escape_time(0.3, 100) == 12))
    checks.append(("c = 0, -1 and -2 never escape (they are in the Mandelbrot set)",
                   all(L.escape_time(c, 200) == 200 for c in (0, -1, -2))))
    checks.append(("c = -2.0001 (just outside the tip) does escape", L.escape_time(-2.0001, 200) < 200))
    checks.append(("a start already beyond 2 escapes at step 0", L.escape_time(0.0, 50, 3 + 0j) == 0))
    checks.append(("edge: max_iter = 0 returns 0 without error", L.escape_time(0.5, 0) == 0))
    checks.append(("Julia set for c = 0 is the unit disc: |z0| < 1 stays, |z0| > 1 escapes",
                   L.escape_time(0, 100, 0.9 + 0j) == 100 and L.escape_time(0, 100, 1.1 + 0j) < 10))
    img = L.mandelbrot_image(complex(-0.5, 0), 3.4, 17, 11, 50)
    checks.append(("the Mandelbrot image is mirror-symmetric about the real axis", np.array_equal(img, img[::-1])))
    q, mods = 2.5 + 0j, []
    for _ in range(5):
        q = q * q + 1.9
        mods.append(abs(q))
    checks.append(("an orbit past radius 2 only grows: from |z| = 2.5 with c = 1.9, each step is larger", all(b > a for a, b in zip([2.5] + mods, mods))))
    e = [L.wrongly_inside(L.SEAHORSE, 0.05, m, 20, 15) for m in (25, 100, 400)]
    checks.append(("more iterations means fewer wrongly-inside pixels", e[0] >= e[1] >= e[2]))
    checks.append(("design: width 0.5 needs 200 iterations on the ladder, width 0.05 needs 800",
                   L.smallest_enough(L.SEAHORSE, 0.5) == 200 and L.smallest_enough(L.SEAHORSE, 0.05) == 800))
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
