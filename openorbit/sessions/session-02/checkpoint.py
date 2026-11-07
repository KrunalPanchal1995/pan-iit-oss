"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r = L.R_EARTH + 400e3
    checks.append(("400 km circular orbit: 7.67 km/s and 92.4 min",
                   abs(L.circular_speed(r) / 1e3 - 7.67) < 0.005 and abs(L.period(r) / 60 - 92.4) < 0.05))
    checks.append((f"geostationary radius 42164 km gives a period of 86164 s (got {L.period(42164e3):.1f})", abs(L.period(42164e3) - 86164) < 1.0))
    checks.append(("the geostationary altitude is 35786 km above the equator (42164 - 6378)", abs((42164 - 6378) - 35786) < 1e-9))

    o = L.design_orbit(500, 35786)
    checks.append((f"worked example: a = 24514 km and e = 0.7197 (got {o['a'] / 1e3:.0f}, {o['e']:.4f})",
                   abs(o["a"] / 1e3 - 24514) < 0.5 and abs(o["e"] - 0.7197) < 5e-5))
    checks.append((f"worked example: period 10.610 h (got {o['T'] / 3600:.3f})", abs(o["T"] / 3600 - 10.610) < 5e-4))
    checks.append((f"worked example: perigee speed 9.988 km/s, apogee speed 1.628 km/s (got {o['vp'] / 1e3:.3f}, {o['va'] / 1e3:.3f})",
                   abs(o["vp"] / 1e3 - 9.988) < 5e-4 and abs(o["va"] / 1e3 - 1.628) < 5e-4))
    checks.append(("angular momentum: rp*vp = ra*va", abs(o["rp"] * o["vp"] / (o["ra"] * o["va"]) - 1) < 1e-12))
    checks.append(("speed ratio equals distance ratio, 6.135", abs(o["vp"] / o["va"] - 6.135) < 5e-4))
    checks.append(("vis-viva with a = r is the circular speed", abs(L.vis_viva(r, r) - L.circular_speed(r)) < 1e-9))
    en_p = L.specific_energy(o["rp"], o["vp"])
    en_a = L.specific_energy(o["ra"], o["va"])
    checks.append(("energy -mu/(2a) = -8.13 MJ/kg at both ends", abs(en_p - en_a) < 1e-3 and abs(en_p + L.MU / (2 * o["a"])) < 1e-3 and abs(en_p / 1e6 + 8.13) < 0.005))
    a12 = L.semi_major_axis_for_period(43200.0)
    ap12 = L.apogee_altitude_for_period(43200.0, 500)
    o12 = L.design_orbit(500, ap12)
    checks.append((f"design: a 12 hour orbit has a = 26610 km, and with perigee 500 km its apogee altitude is 39978 km (got {a12 / 1e3:.0f}, {ap12:.0f})",
                   abs(a12 / 1e3 - 26610) < 0.5 and abs(ap12 - 39978) < 0.5 and abs(o12["T"] - 43200.0) < 1e-6))
    a, e = L.ellipse_from_peri_apo(7e6, 7e6)
    checks.append(("a circle has e = 0", e == 0 and a == 7e6))

    # Kepler's equation
    worst_res, worst_it = 0.0, 0
    for ecc in (0.0, 0.3, 0.7, 0.95):
        for M in np.linspace(0.0, 2 * np.pi, 120):
            E, it, res = L.solve_kepler(M, ecc)
            worst_res = max(worst_res, abs(E - ecc * np.sin(E) - M))
            worst_it = max(worst_it, it)
    checks.append((f"Kepler's equation residual below 1e-12 for e up to 0.95 (worst {worst_res:.1e})", worst_res < 1e-12))
    checks.append((f"Newton needs at most 8 iterations (worst {worst_it})", worst_it <= 8))
    M1 = 2 * np.pi * 3600 / o["T"]
    E1, it1, _ = L.solve_kepler(M1, o["e"])
    checks.append((f"one hour after perigee: E = 1.2821 rad, r = 19491 km in 5 iterations (got {E1:.4f}, {L.radius_from_E(E1, o['a'], o['e']) / 1e3:.0f}, {it1})",
                   abs(E1 - 1.2821) < 5e-4 and abs(L.radius_from_E(E1, o["a"], o["e"]) / 1e3 - 19491) < 2 and it1 == 5))
    checks.append(("edge: e = 0 gives E = M, M = 0 gives E = 0, M = pi gives E = pi",
                   abs(L.solve_kepler(1.234, 0.0)[0] - 1.234) < 1e-12 and abs(L.solve_kepler(0.0, 0.9)[0]) < 1e-12
                   and abs(L.solve_kepler(np.pi, 0.9)[0] - np.pi) < 1e-9))

    # integrators on a 7000 x 21000 km orbit
    rp, ra = 7.0e6, 2.1e7
    r0, v0 = L.perigee_start(rp, ra)
    T = L.period((rp + ra) / 2)
    dt = 60.0
    k = int(round(T / dt))
    pos, en, hh = L.propagate(L.rk4_step, r0, v0, T / k, k)
    checks.append((f"RK4 returns to the start point after one period (within 2 km, got {np.linalg.norm(pos[-1] - r0) / 1e3:.2f})", np.linalg.norm(pos[-1] - r0) < 2e3))
    d = {}
    for name, step in (("rk4", L.rk4_step), ("lf", L.leapfrog_step)):
        p10, e10, h10 = L.propagate(step, r0, v0, dt, 10 * k)
        p40, e40, h40 = L.propagate(step, r0, v0, dt, 40 * k)
        rel10 = abs(e10[-1] - e10[0]) / abs(e10[0])
        rel40 = abs(e40[-1] - e40[0]) / abs(e40[0])
        d[name] = (rel10, rel40, np.max(np.abs(e40 - e40[0])) / abs(e40[0]), abs(h40[-1] - h40[0]) / h40[0])
    checks.append((f"RK4 energy drift grows with laps (10 laps {d['rk4'][0]:.1e}, 40 laps {d['rk4'][1]:.1e})", d["rk4"][1] > 2.5 * d["rk4"][0]))
    checks.append((f"leapfrog energy error stays bounded: worst over 40 laps below 2e-3 (got {d['lf'][2]:.1e})", d["lf"][2] < 2e-3))
    checks.append(("leapfrog conserves angular momentum to 1e-12", d["lf"][3] < 1e-12))
    checks.append((f"RK4 energy change: 1.9e-6 after 10 laps, 7.8e-6 after 40 (got {d['rk4'][0]:.1e}, {d['rk4'][1]:.1e})",
                   abs(d["rk4"][0] - 1.9e-6) < 0.1e-6 and abs(d["rk4"][1] - 7.8e-6) < 0.2e-6))
    checks.append(("with this step, RK4 is more accurate than leapfrog after 40 laps", d["rk4"][1] < d["lf"][1]))
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
