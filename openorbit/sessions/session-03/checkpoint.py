"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    r1, r2 = 6778e3, 42164e3
    h = L.hohmann(r1, r2)
    checks.append((f"worked example: LEO to GEO dv1 2.398, dv2 1.457, total 3.854 km/s (got {h['dv1'] / 1e3:.3f}, {h['dv2'] / 1e3:.3f}, {h['total'] / 1e3:.3f})",
                   abs(h["dv1"] / 1e3 - 2.398) < 5e-4 and abs(h["dv2"] / 1e3 - 1.457) < 5e-4 and abs(h["total"] / 1e3 - 3.854) < 5e-4))
    checks.append((f"worked example: transfer takes 5.291 h on an ellipse with a = 24471 km (got {h['time'] / 3600:.3f}, {h['a_t'] / 1e3:.0f})",
                   abs(h["time"] / 3600 - 5.291) < 5e-4 and abs(h["a_t"] / 1e3 - 24471) < 0.5))
    vp_t, va_t = L.vis_viva(r1, h["a_t"]), L.vis_viva(r2, h["a_t"])
    checks.append((f"worked example speeds: circular LEO 7.669, transfer perigee 10.066, transfer apogee 1.618, circular GEO 3.075 km/s (got {L.circular_speed(r1) / 1e3:.3f}, {vp_t / 1e3:.3f}, {va_t / 1e3:.3f}, {L.circular_speed(r2) / 1e3:.3f})",
                   abs(L.circular_speed(r1) / 1e3 - 7.669) < 5e-4 and abs(vp_t / 1e3 - 10.066) < 5e-4 and abs(va_t / 1e3 - 1.618) < 5e-4 and abs(L.circular_speed(r2) / 1e3 - 3.075) < 5e-4))
    sm = L.hohmann(6778e3, 7178e3)
    checks.append((f"small step 6778 km to 7178 km: 109.1 + 107.6 = 216.7 m/s in 2900.5 s (got {sm['dv1']:.1f}, {sm['dv2']:.1f}, {sm['total']:.1f}, {sm['time']:.1f})",
                   abs(sm["dv1"] - 109.1) < 0.05 and abs(sm["dv2"] - 107.6) < 0.05 and abs(sm["total"] - 216.7) < 0.05 and abs(sm["time"] - 2900.5) < 0.05))
    c = L.check_hohmann(r1, r2)
    checks.append((f"integration from burn 1 arrives at 42164 km (within 1 km), opposite side (180 degrees) (got {c['r_end'] / 1e3:.2f} km, {c['angle']:.2f})",
                   abs(c["r_end"] - r2) < 1e3 and abs(c["angle"] - 180) < 0.01))
    checks.append((f"integrated arrival speed equals the vis-viva apogee speed 1618 m/s (got {c['v_end']:.1f})",
                   abs(c["v_end"] - L.vis_viva(r2, h["a_t"])) < 0.5 and abs(c["v_end"] - 1618) < 1))
    checks.append((f"after burn 2 the orbit stays circular to within 1 m over a lap (got {c['circle_err']:.2f} m)", c["circle_err"] < 1.0))
    z = L.hohmann(7e6, 7e6)
    checks.append(("edge: transfer between equal radii costs nothing and takes one half orbit", z["total"] < 1e-9 and abs(z["time"] - 0.5 * L.period(7e6)) < 1e-6))
    d = L.hohmann(r2, r1)
    checks.append(("going down costs the same total, with both burns backwards", d["dv1"] < 0 and d["dv2"] < 0 and abs(d["total"] - h["total"]) < 1e-6))

    # bi-elliptic
    vals = {x: L.cost_ratio(x) for x in (5, 10, 15, 20, 50)}
    checks.append(("ratio 5: bi-elliptic costs 1.249 times Hohmann; ratio 10: 1.029; ratio 15: 0.972",
                   abs(vals[5] - 1.2488) < 5e-4 and abs(vals[10] - 1.0291) < 5e-4 and abs(vals[15] - 0.9719) < 5e-4))
    scan = np.arange(2.0, 30.0, 0.01)
    first = scan[next(i for i, x in enumerate(scan) if L.cost_ratio(x) < 1)]
    checks.append((f"scan: bi-elliptic first wins at a ratio of about 11.94 (scan {first:.2f}, bisection {L.crossover_ratio():.3f})",
                   abs(first - 11.94) < 0.011 and abs(L.crossover_ratio() - 11.94) < 0.005))
    b = L.bielliptic(r1, r2, r2)
    checks.append(("edge: a bi-elliptic transfer with rb = r2 is the Hohmann transfer", abs(b["total"] - h["total"]) < 1e-6))
    b = L.bielliptic(r1, r2, 20 * r2)
    checks.append((f"LEO to GEO is a ratio of 6.2, so bi-elliptic loses: 4.427 km/s and 32.9 days (got {b['total'] / 1e3:.3f}, {b['time'] / 86400:.1f})",
                   abs(b["total"] / 1e3 - 4.427) < 5e-4 and abs(b["time"] / 86400 - 32.9) < 0.05))

    # plane change
    vleo, vgeo = L.circular_speed(r1), L.circular_speed(r2)
    vapo = L.vis_viva(r2, h["a_t"])
    pc = [L.plane_change_dv(v, 28.5) / 1e3 for v in (vleo, vgeo, vapo)]
    checks.append((f"28.5 degrees costs 3.775 (LEO), 1.514 (GEO), 0.797 (transfer apogee) km/s (got {pc[0]:.3f}, {pc[1]:.3f}, {pc[2]:.3f})",
                   abs(pc[0] - 3.775) < 5e-4 and abs(pc[1] - 1.514) < 5e-4 and abs(pc[2] - 0.797) < 5e-4))
    checks.append(("hand calculation: a 60 degree turn costs exactly v, a 0 degree turn costs nothing",
                   abs(L.plane_change_dv(1000.0, 60) - 1000.0) < 1e-9 and L.plane_change_dv(1000.0, 0) == 0))
    comb = L.combined_burn_dv(vapo, vgeo, 28.5) / 1e3
    sep = (abs(vgeo - vapo) + L.plane_change_dv(vgeo, 28.5)) / 1e3
    checks.append((f"combined apogee burn 1.824 km/s beats circularising then turning, 2.970 km/s (got {comb:.3f}, {sep:.3f})",
                   abs(comb - 1.824) < 5e-4 and abs(sep - 2.970) < 5e-4 and comb < sep))
    opt_a = (L.plane_change_dv(vleo, 28.5) + h["total"]) / 1e3
    opt_b = (h["dv1"] + L.combined_burn_dv(vapo, vgeo, 28.5)) / 1e3
    opt_c = (h["total"] + L.plane_change_dv(vgeo, 28.5)) / 1e3
    checks.append((f"design: total delta-v to GEO with 28.5 degrees to remove: 7.629 (turn in LEO), 5.368 (turn at GEO), 4.222 (turn at apogee) km/s (got {opt_a:.3f}, {opt_c:.3f}, {opt_b:.3f})",
                   abs(opt_a - 7.629) < 5e-4 and abs(opt_c - 5.368) < 5e-4 and abs(opt_b - 4.222) < 5e-4 and opt_b < opt_c < opt_a))
    checks.append(("combined burn with no turn is just the speed difference", abs(L.combined_burn_dv(3000.0, 4000.0, 0) - 1000.0) < 1e-9))

    # Oberth
    low, high = L.energy_gain(vleo, 1000.0) / 1e6, L.energy_gain(1000.0, 1000.0) / 1e6
    checks.append((f"Oberth: 1000 m/s adds 8.169 MJ/kg at LEO speed and 1.500 MJ/kg at 1000 m/s (got {low:.3f}, {high:.3f})",
                   abs(low - 8.169) < 5e-4 and abs(high - 1.5) < 5e-4))
    checks.append(("energy gain equals v dv + dv^2/2", abs(L.energy_gain(5000.0, 300.0) - (5000.0 * 300.0 + 0.5 * 300.0**2)) < 1e-6))

    # phasing
    tn, tf = L.phasing_time(6778e3, 7178e3, 30), L.phasing_formula(6778e3, 7178e3, 30)
    checks.append((f"phasing: chaser at 6778 km catches a target 30 degrees ahead at 7178 km in 5615.5 s (numeric {tn:.1f}, formula {tf:.1f})",
                   abs(tn - tf) < 0.5 and abs(tn - 5615.5) < 0.5))

    # finite burn
    acc20 = L.finite_burn(r1, h["dv1"] / 20.0, 20.0)
    acc2 = L.finite_burn(r1, h["dv1"] / 2.0, 2.0)
    acc05 = L.finite_burn(r1, h["dv1"] / 0.5, 0.5)
    checks.append((f"finite burn apogees: 42111 km (20 m/s^2), 38026 km (2 m/s^2), 23023 km (0.5 m/s^2) (got {acc20 / 1e3:.0f}, {acc2 / 1e3:.0f}, {acc05 / 1e3:.0f})",
                   abs(acc20 / 1e3 - 42111) < 3 and abs(acc2 / 1e3 - 38026) < 3 and abs(acc05 / 1e3 - 23023) < 3))
    c2, c05 = L.finite_burn_cost(r1, r2, 2.0), L.finite_burn_cost(r1, r2, 0.5)
    e2, e05 = (c2 - h["dv1"]) / h["dv1"], (c05 - h["dv1"]) / h["dv1"]
    checks.append((f"gravity loss: a 2 m/s^2 burn needs 3.5% more delta-v, a 0.5 m/s^2 burn 35.9% more (got {e2:.1%}, {e05:.1%})",
                   abs(e2 - 0.035) < 0.001 and abs(e05 - 0.359) < 0.001))
    checks.append(("weaker engines lose more", acc05 < acc2 < acc20 < r2 and e05 > e2 > 0))

    # mini-project
    m1, m2 = L.R_EARTH + 500e3, L.R_EARTH + 20200e3
    hm = L.hohmann(m1, m2)
    cm = L.check_hohmann(m1, m2)
    checks.append((f"mini-project: 500 km to 20200 km altitude: dv1 1984.8, dv2 1390.3, total 3375.1 m/s, 2.989 h (got {hm['dv1']:.1f}, {hm['dv2']:.1f}, {hm['total']:.1f}, {hm['time'] / 3600:.3f})",
                   abs(hm["dv1"] - 1984.8) < 0.1 and abs(hm["dv2"] - 1390.3) < 0.1 and abs(hm["total"] - 3375.1) < 0.1 and abs(hm["time"] / 3600 - 2.989) < 5e-4))
    checks.append((f"mini-project: integrated arrival radius 26571 km within 1 km, 180 degrees (got {cm['r_end'] / 1e3:.2f}, {cm['angle']:.2f})",
                   abs(cm["r_end"] - m2) < 1e3 and abs(cm["angle"] - 180) < 0.01))
    checks.append(("mini-project: a bi-elliptic route with rb = 3 r2 costs more than Hohmann at this small ratio",
                   L.bielliptic(m1, m2, 3 * m2)["total"] > hm["total"]))
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
