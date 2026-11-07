"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    v = L.measured_speed_1d()
    checks.append((f"pulse arrival: measured wave speed within 1 percent of c (got {v:.4f})", abs(v - 1) < 0.01))

    e = L.box_energy_history(steps=200)
    checks.append(("closed box: total energy constant to 1e-9", (e.max() - e.min()) / e.mean() < 1e-9))
    g = L.Yee2D(61, 61, 0.5, boundary="mur")
    for n in range(40):
        g.step([(30, 30, L.gaussian(n, 15.0, 4.0))])
    e1 = g.energy()
    for n in range(200):
        g.step()
    checks.append(("absorbing boundary lets the energy leave (below 5 percent left)", g.energy() < 0.05 * e1))

    checks.append(("Courant limit in 2D is 1/sqrt(2)", abs(L.COURANT_LIMIT_2D - 2 ** -0.5) < 1e-12))
    checks.append(("S = 0.70 (below the limit) stays bounded", L.growth_test(0.70) < 1.0))
    checks.append(("S = 0.75 (above the limit) blows up (above 1e6)", L.growth_test(0.75) > 1e6))

    # worked example: 2.4 GHz wifi, 20 cells per wavelength
    lam = 299792458.0 / 2.4e9
    dx = lam / 20
    dt = L.courant_dt(dx)
    checks.append((f"worked example: wifi grid dx = {dx * 1000:.2f} mm gives dt = {dt * 1e12:.2f} ps (14.73)",
                   abs(dx * 1000 - 6.246) < 0.01 and abs(dt * 1e12 - 14.73) < 0.02))
    checks.append(("worked example: about 28 time steps per wave period", abs(1 / 2.4e9 / dt - 28.3) < 0.1))
    checks.append(("1D limit: dt = dx / c exactly", abs(L.courant_dt(1.0, 1.0, dim=1) - 1.0) < 1e-12))

    nodes, _ = L.standing_wave_nodes()
    sp = np.diff(nodes)
    checks.append((f"standing wave: node spacing is lambda/2 = 10 cells within 3 percent (got {sp.mean():.2f})",
                   len(nodes) >= 10 and abs(sp.mean() - 10) < 0.3))

    p, _, _ = L.falloff_exponent()
    checks.append((f"2D point source: amplitude falls as r^-0.5 (fitted {p:.3f})", abs(p + 0.5) < 0.05))

    # hand calculation: slowness (k dx)^2 (1 - S^2) / 24 at 10 points per wavelength
    hand = 1 - (2 * np.pi / 10) ** 2 * (1 - 0.25) / 24
    checks.append(("hand calculation: phase speed at 10 points per wavelength is 0.988 c",
                   abs(L.phase_speed_theory(10, 0.5) - hand) < 5e-4))
    checks.append(("measured phase speed agrees with theory at 10 points per wavelength (0.3 percent)",
                   abs(L.phase_speed_measured(10) - L.phase_speed_theory(10, 0.5)) < 0.003))
    checks.append(("coarse grid is slower than fine grid (6 vs 20 points per wavelength)",
                   L.phase_speed_theory(6, 0.5) < L.phase_speed_theory(20, 0.5)))
    checks.append(("fewer than 10 points per wavelength: error above 1 percent",
                   1 - L.phase_speed_theory(9, 0.5) > 0.01))

    th, A = L.ring_pattern(delta=np.pi)
    ref = L.array_factor(th, 0.5, np.pi)
    checks.append(("dipole-like pair: FDTD pattern matches theory (rms error below 0.05)",
                   np.sqrt(np.mean((A - ref / ref.max()) ** 2)) < 0.05))
    n = len(A)
    checks.append(("opposite-phase pair: strong along the axis, nearly a null at 90 and 270 degrees",
                   A[0] > 0.9 and A[n // 4] < 0.1 and A[3 * n // 4] < 0.1))
    echo = L.boundary_echo()
    checks.append((f"Mur boundary is imperfect: echo between 0.5 and 5 percent of the pulse (got {100 * echo:.1f})",
                   0.005 < echo < 0.05))
    d = L.beam_phase(60, 0.5)
    checks.append(("hand calculation: aiming at 60 degrees with d = lambda/2 needs delta = -90 degrees",
                   abs(np.degrees(d) + 90) < 1e-9))
    th2, A2 = L.ring_pattern(delta=d)
    up = (th2 > 0) & (th2 < np.pi)
    ang = np.degrees(th2[up][A2[up].argmax()])
    checks.append((f"steered pair: beam points at 60 degrees within 5 (got {ang:.0f})", abs(ang - 60) < 5))
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
