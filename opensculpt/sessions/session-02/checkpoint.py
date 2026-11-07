"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c0 = (0.0, 0.0)
    # CAD operations on a big circle A (r=2) and a small circle B (r=1) at the same centre-line
    A, B = (0.0, 0.0), (1.5, 0.0)
    pts = np.array([[-1.5, 0.0], [1.4, 0.0], [2.8, 0.0], [5.0, 0.0]])   # in A only, in both, in B only, outside
    a = L.sd_circle(pts, A, 2.0)
    b = L.sd_circle(pts, B, 1.5)
    checks.append(("union is inside where either is inside", list(L.op_union(a, b) < 0) == [True, True, True, False]))
    checks.append(("intersection is inside only where both are inside", list(L.op_intersect(a, b) < 0) == [False, True, False, False]))
    checks.append(("subtraction A minus B keeps the points in A and not in B", list(L.op_subtract(a, b) < 0) == [True, False, False, False]))
    checks.append(("shell: a point on the circle has value -t", abs(float(L.op_shell(L.sd_circle((2, 0), c0, 2.0), 0.3)) + 0.3) < 1e-12))
    checks.append(("shell: a point 0.3 from the surface (either side) is on the shell surface",
                   abs(float(L.op_shell(L.sd_circle((2.3, 0), c0, 2.0), 0.3))) < 1e-12 and abs(float(L.op_shell(L.sd_circle((1.7, 0), c0, 2.0), 0.3))) < 1e-12))

    # smooth minimum
    aa = np.linspace(-3, 3, 601)
    k = 1.0
    far = np.abs(aa - 0.0) >= k
    s = L.smin(aa, 0.0, k)
    checks.append(("smooth min equals min when |a - b| >= k", bool(np.allclose(s[far], np.minimum(aa, 0.0)[far], atol=1e-12))))
    checks.append(("smooth min is never above min", bool(np.all(s <= np.minimum(aa, 0.0) + 1e-12))))
    checks.append(("smooth min is symmetric in a and b", bool(np.allclose(L.smin(aa, 0.3, k), L.smin(0.3, aa, k)))))
    checks.append(("at a = b the surface is pulled out by exactly k/4", abs(float(L.smin(2.0, 2.0, 0.8)) - (2.0 - 0.2)) < 1e-12))
    checks.append(("edge case: k = 0 gives the plain min", bool(np.allclose(L.smin(aa, 0.5, 0.0), np.minimum(aa, 0.5)))))

    # areas
    R, H, t = 3.852, 9.0, 0.5
    an = L.body_area(R, H, t)
    got = L.area_by_cells(lambda q: L.body2d(q, R, H, t), (-R - 0.5, -0.5), (R + 0.5, H + 0.5), 400)
    checks.append((f"mug body area by counting {got:.3f} is within 0.5% of the analytic {an:.3f} cm^2", abs(got - an) / an < 0.005))
    ring = L.area_by_cells(lambda q: np.abs(L.sd_circle(q, c0, 2.0)) - 0.45, (-3, -3), (3, 3), 600)
    checks.append((f"handle ring area {ring:.3f} is within 0.5% of 4 pi Rh r = {4 * np.pi * 2.0 * 0.45:.3f}", abs(ring - 4 * np.pi * 2.0 * 0.45) / (4 * np.pi * 2.0 * 0.45) < 0.005))

    # the mug cross-section
    checks.append(("mug: the cavity is empty, the wall and the handle tube are solid",
                   float(L.mug2d(np.array([0.0, 5.0]), R, H, t)) > 0
                   and float(L.mug2d(np.array([R - t / 2, 4.0]), R, H, t)) < 0
                   and float(L.mug2d(np.array([R + 3.0, 0.55 * H]), R, H, t)) < 0))
    checks.append(("mug: the hole of the handle is empty", float(L.mug2d(np.array([R + 1.0, 0.55 * H]), R, H, t)) > 0))
    a0 = L.area_by_cells(lambda q: L.mug2d(q, R, H, t, 0.0), (-R - 1, -1), (R + 5, H + 1), 500)
    a1 = L.area_by_cells(lambda q: L.mug2d(q, R, H, t, 1.0), (-R - 1, -1), (R + 5, H + 1), 500)
    checks.append((f"a blend radius of 1 cm adds material at the joints ({a0:.2f} to {a1:.2f} cm^2)", a1 > a0))

    # worked example: 300 mL, H = 9, t = 0.5
    root = np.sqrt(300.0 / (np.pi * 8.5))
    Rd = L.radius_for_capacity(300.0, 9.0, 0.5)
    checks.append((f"worked example: R = 0.5 + sqrt(300 / (pi * 8.5)) = {Rd:.3f} cm and the capacity is 300 mL",
                   abs(Rd - (0.5 + root)) < 1e-12 and abs(Rd - 3.852) < 1e-3 and abs(L.capacity(Rd, 9.0, 0.5) - 300.0) < 1e-9))
    mat = L.material_volume(Rd, 9.0, 0.5)
    rev = L.revolve_volume(lambda q: L.body2d(q, Rd, 9.0, 0.5), Rd, 9.0, 400)
    checks.append((f"volume of revolution: counted slice {rev:.1f} matches the formula {mat:.1f} cm^3 within 1%", abs(rev - mat) / mat < 0.01))
    checks.append(("design numbers: H = 10, t = 0.4 needs R = 3.554; H = 9 needs R = 3.732 (t = 0.4) and 4.213 (t = 0.8)",
                   abs(L.radius_for_capacity(300.0, 10.0, 0.4) - 3.554) < 1e-3 and abs(L.radius_for_capacity(300.0, 9.0, 0.4) - 3.732) < 1e-3
                   and abs(L.radius_for_capacity(300.0, 9.0, 0.8) - 4.213) < 1e-3))
    m4 = L.material_volume(L.radius_for_capacity(300.0, 9.0, 0.4), 9.0, 0.4)
    m8 = L.material_volume(L.radius_for_capacity(300.0, 9.0, 0.8), 9.0, 0.8)
    checks.append((f"design: material is {m4:.1f} cm^3 for t = 0.4 and {m8:.1f} cm^3 for t = 0.8 (and {mat:.1f} for 0.5)",
                   abs(m4 - 93.9) < 0.05 and abs(m8 - 201.7) < 0.05 and abs(mat - 119.5) < 0.05))
    checks.append(("app numbers: R = 4.5, t = 0.5, H = 9 holds 427.3 mL; R = 3.85 holds 299.7 mL; smin(0, 0, 2) = -0.5",
                   abs(L.capacity(4.5, 9.0, 0.5) - 427.3) < 0.05 and abs(L.capacity(3.85, 9.0, 0.5) - 299.7) < 0.05
                   and abs(float(L.smin(0.0, 0.0, 2.0)) + 0.5) < 1e-12))
    checks.append(("a thicker wall needs a larger radius for the same capacity",
                   L.radius_for_capacity(300.0, 9.0, 0.8) > L.radius_for_capacity(300.0, 9.0, 0.4)))
    try:
        L.radius_for_capacity(300.0, 9.0, 9.0)
        ok = False
    except ValueError:
        ok = True
    checks.append(("edge case: a wall as thick as the mug is height is rejected", ok))
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
