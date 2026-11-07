"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R, H, t = 3.852, 9.0, 0.5

    # primitives
    checks.append(("cylinder: the middle of a cylinder of radius 2 has value -2",
                   abs(float(L.sd_cylinder(0.0, 0.0, 5.0, 2.0, 0.0, 10.0)) + 2.0) < 1e-12))
    checks.append(("cylinder: the point (3, 0, 11) is sqrt(2) from the rim",
                   abs(float(L.sd_cylinder(3.0, 0.0, 11.0, 2.0, 0.0, 10.0)) - np.sqrt(2.0)) < 1e-12))
    checks.append(("torus: the middle of the tube has value -r",
                   abs(float(L.sd_torus(2.5, 0.0, 0.0, 0.5, 0.0, 2.0, 0.45)) + 0.45) < 1e-12))
    checks.append(("mug: cavity empty, wall solid, handle solid, handle hole empty",
                   float(L.mug3d(0.0, 0.0, 5.0, R, H, t, 0.5)) > 0 and float(L.mug3d(R - t / 2, 0.0, 4.0, R, H, t, 0.5)) < 0
                   and float(L.mug3d(R + 3.0, 0.0, 0.55 * H, R, H, t, 0.5)) < 0 and float(L.mug3d(R + 1.0, 0.0, 0.55 * H, R, H, t, 0.5)) > 0))

    # exact volumes and the worked example
    vb = L.body_volume(R, H, t)
    checks.append((f"exact body volume pi R^2 H - pi (R-t)^2 (H-t) = {vb:.2f} cm^3 and torus 2 pi^2 Rh r^2 = {L.torus_volume(2.0, 0.45):.2f} cm^3",
                   abs(vb - 119.49) < 0.01 and abs(L.torus_volume(2.0, 0.45) - 7.99) < 0.01))
    mass = L.mug_mass(R, H, t)
    checks.append((f"worked example: body mass {2.4 * vb:.1f} g, whole mug (voxels) {mass:.0f} g",
                   abs(2.4 * vb - 286.8) < 0.1 and abs(mass - 301.0) < 3.0))

    # convergence of the voxel volume
    Ns = np.array([16, 24, 32, 48, 64, 96, 128])
    errs = np.array([L.body_volume_rms_error(int(n), R, H, t) for n in Ns])
    slope = L.convergence_slope(Ns, errs)
    checks.append((f"voxel volume error falls about like 1/N: slope {slope:.2f} (between -1.3 and -0.8)", -1.3 < slope < -0.8))
    checks.append((f"at N = 128 the rms volume error is {100 * errs[-1]:.2f}% (below 1.5%, near 0.9%)", abs(errs[-1] - 0.0092) < 0.0015))
    lo, hi = L.mug_box(R, H)
    allout = L.voxel_volume(lambda x, y, z: np.ones_like(x), lo, hi, 0.5)
    checks.append(("edge case: a field that is positive everywhere has volume 0", allout == 0.0))
    box = L.voxel_volume(lambda x, y, z: -np.ones_like(x), (0, 0, 0), (2, 3, 4), 0.5)
    checks.append(("edge case: a field that is negative everywhere gives the box volume 24", abs(box - 24.0) < 1e-9))

    # marching squares
    e = {n: abs(L.circle_contour_length(1.0, n) - 2 * np.pi) for n in (32, 64, 128)}
    checks.append((f"marching squares: circle length at n = 128 is within 1e-4 relative of 2 pi (error {e[128]:.1e})", e[128] / (2 * np.pi) < 1e-4))
    checks.append(("marching squares: the error falls about 4 times per doubling of n", e[64] < e[32] / 3 and e[128] < e[64] / 3))
    checks.append(("marching squares: a circle of radius 2.5 has length 2 pi (2.5)",
                   abs(L.circle_contour_length(2.5, 128) - 2 * np.pi * 2.5) / (2 * np.pi * 2.5) < 1e-4))
    x = np.linspace(-1, 1, 10)
    checks.append(("edge case: no sign change means no contour", L.contour_length(np.ones((10, 10)), x, x) == 0.0))

    # gradient and the Eikonal property
    p = np.array([[2.0, 1.0, 0.5], [-1.0, 3.0, 2.0], [0.3, -0.4, 0.2]])
    gn = np.linalg.norm(L.gradient(lambda q: L.sphere_f(q), p), axis=-1)
    checks.append(("exact sphere field: |grad| = 1 to 1e-6", bool(np.allclose(gn, 1.0, atol=1e-6))))
    n0 = L.gradient(lambda q: L.sphere_f(q), np.array([1.0, 0.0, 0.0]))
    checks.append(("the gradient at (1, 0, 0) of the unit sphere is the outward normal (1, 0, 0)", bool(np.allclose(n0, [1.0, 0.0, 0.0], atol=1e-6))))
    g_union = L.surface_gradient_norm(lambda q: L.two_spheres(q, 0.0))
    g_smooth = L.surface_gradient_norm(lambda q: L.two_spheres(q, 1.0))
    checks.append((f"min of two spheres keeps |grad| = 1 ({g_union:.3f}); the smooth union has |grad| = {g_smooth:.3f} (about 0.78)", abs(g_union - 1.0) < 1e-3 and abs(g_smooth - 0.775) < 0.01))
    checks.append(("max of two half-spaces at (1, 1) says 1 but the true distance to the corner is sqrt(2)", float(np.max([1.0, 1.0])) < np.sqrt(2.0)))

    # sensitivity: dV/dt = cavity surface area
    A = L.cavity_surface_area(R, H, t)
    dt = 1e-4
    fd = (L.body_volume(R, H, t + dt) - L.body_volume(R, H, t - dt)) / (2 * dt)
    checks.append((f"exact: d(volume)/d(wall) = cavity surface area ({fd:.1f} against {A:.1f} cm^2)", abs(fd - A) / A < 1e-6 and abs(A - 214.3) < 0.1))
    h = L.voxel_size(200, R)
    vp = L.voxel_volume(lambda x, y, z: L.body3d(x, y, z, R, H, t + 0.1), lo, hi, h)
    vm = L.voxel_volume(lambda x, y, z: L.body3d(x, y, z, R, H, t - 0.1), lo, hi, h)
    dvdt = (vp - vm) / 0.2
    checks.append((f"voxels: (V(t+0.1) - V(t-0.1)) / 0.2 = {dvdt:.1f} cm^2 is within 5% of the area", abs(dvdt - A) / A < 0.05))

    dV = L.body_volume(R, H, 0.6) - L.body_volume(R, H, 0.5)
    checks.append((f"first-order estimate {A * 0.1:.1f} cm^3 against the exact change {dV:.2f} cm^3 for t from 0.5 to 0.6",
                   abs(A * 0.1 - 21.4) < 0.05 and abs(dV - 20.96) < 0.01))

    # failure cases
    p03 = L.wall_hit_probability(0.3, 0.5)
    checks.append((f"a wall of 0.3 cm sampled every 0.5 cm is seen only {100 * p03:.0f}% of the time (expected 60%)", abs(p03 - 0.6) < 0.04))
    checks.append(("a wall as thick as the voxel is always seen", L.wall_hit_probability(0.5, 0.5) == 1.0))
    caps = {k: L.cavity_capacity(R, H, t, k) for k in (0, 2, 8, 16)}
    checks.append((f"capacity with no blend is 300 mL to 1% ({caps[0]:.1f}); with k = 2 it is {caps[2]:.1f}, with k = 8 {caps[8]:.1f}, with k = 16 the cavity is full",
                   abs(caps[0] - 300.0) / 300.0 < 0.01 and abs(caps[2] - 294.4) < 1.0 and abs(caps[8] - 166.3) < 1.5 and caps[16] < 1.0))

    # render
    img = L.render_cutaway(R, H, t, 0.5, size=(110, 120))
    frac = float(np.mean(~np.isnan(img)))
    checks.append((f"ray march: {100 * frac:.0f}% of the pixels hit the mug (between 10% and 60%)", 0.1 < frac < 0.6))

    # design: the 0.5 cm wall meets a 320 g limit and 0.55 cm does not (300 mL each)
    R55 = 0.55 + np.sqrt(300.0 / (np.pi * (H - 0.55)))
    m55 = L.mug_mass(R55, H, 0.55)
    checks.append((f"design: the radius for t = 0.55 cm is {R55:.3f} cm", abs(R55 - 3.912) < 5e-4))
    checks.append((f"design: t = 0.5 cm gives {mass:.0f} g (< 320 g) but t = 0.55 cm gives {m55:.0f} g (> 320 g)", mass < 320.0 < m55 and abs(m55 - 336.0) < 4.0))
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
