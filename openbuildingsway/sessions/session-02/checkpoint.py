"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    m = 2.0e5
    k0 = L.stiffness_for_period(m, 1.0)
    checks.append((f"worked example: m = 200000 kg and T = 1 s need k = 7.896e6 N/m (got {k0:.4g}); w = 6.283 rad/s",
                   abs(k0 - 7.896e6) < 5e3 and abs(L.omega(k0, m) - 2 * np.pi) < 1e-9))
    checks.append(("period(k0, m) returns 1 s", abs(L.period(k0, m) - 1.0) < 1e-12))
    checks.append(("rule of thumb: 10 storeys is 1.0 s, 5 storeys 0.5 s",
                   abs(L.rule_of_thumb_period(10) - 1.0) < 1e-12 and abs(L.rule_of_thumb_period(5) - 0.5) < 1e-12))

    # amplification by hand
    d1 = L.amplification(1.0, 0.05)
    checks.append(("D(1) = 1 / (2 zeta) = 10 for zeta = 0.05", abs(d1 - 10.0) < 1e-9))
    checks.append(("D(0) = 1 (a very slow push moves the building statically)", abs(L.amplification(0.0) - 1.0) < 1e-12))
    checks.append(("hand calculation: D(0.5) = 1 / sqrt(0.75^2 + 0.05^2) = 1.3304",
                   abs(L.amplification(0.5) - 1 / np.sqrt(0.75 ** 2 + 0.05 ** 2)) < 1e-12 and abs(L.amplification(0.5) - 1.3304) < 5e-4))
    checks.append(("D(2) = 0.3326: a fast shake barely moves the building", abs(L.amplification(2.0) - 0.3326) < 5e-4))
    pk, rp = L.peak_amplification(0.05)
    grid = np.linspace(0, 3, 300001)
    checks.append((f"exact peak 10.0125 at r = 0.9975 matches a fine grid search (got {pk:.4f}, {rp:.4f})",
                   abs(pk - 10.0125) < 5e-4 and abs(rp - 0.9975) < 5e-4 and abs(L.amplification(grid, 0.05).max() - pk) < 1e-5))
    checks.append(("peak is close to 1/(2 zeta) for small damping: within 0.2 percent at zeta = 0.05",
                   abs(pk - 10.0) / 10.0 < 2e-3))
    checks.append(("more damping, lower peak: zeta 0.02 gives 25.0, zeta 0.2 gives 2.5",
                   abs(L.amplification(1.0, 0.02) - 25.0) < 1e-9 and abs(L.amplification(1.0, 0.2) - 2.5) < 1e-9))

    # numerical solution agrees with the formula
    ok = True
    for rr in (0.5, 1.0, 1.5):
        w = 2 * np.pi / rr
        kk = m * w ** 2
        num = L.sway_amplitude_numeric(1.0, kk, m, 1.0) * w ** 2
        ok &= abs(num - L.amplification(rr)) / L.amplification(rr) < 5e-3
    checks.append(("RK4 steady amplitude matches D(r) within 0.5 percent at r = 0.5, 1.0, 1.5", ok))
    checks.append(("sway_amplitude uses a0 / w^2 * D: 2 m/s^2 on k0 gives 0.5066 m",
                   abs(L.sway_amplitude(2.0, k0, m, 1.0) - 2.0 / (2 * np.pi) ** 2 * 10.0) < 1e-9
                   and abs(L.sway_amplitude(2.0, k0, m, 1.0) - 0.5066) < 5e-4))

    # design problem
    rs = L.r_for_amplification(2.0, 0.05, "stiff")
    rf = L.r_for_amplification(2.0, 0.05, "flexible")
    checks.append((f"D = 2 at r = 0.7107 (stiff side) and r = 1.2186 (flexible side) (got {rs:.4f}, {rf:.4f})",
                   abs(rs - 0.7107) < 5e-4 and abs(rf - 1.2186) < 5e-4
                   and abs(L.amplification(rs) - 2) < 1e-9 and abs(L.amplification(rf) - 2) < 1e-9))
    ks = L.design_stiffness(m, 1.0, 2.0)
    kf = L.design_stiffness(m, 1.0, 2.0, side="flexible")
    checks.append((f"design: stiffer building needs k = 1.563e7 N/m, 1.98 times k0 (got {ks:.4g}, x{ks / k0:.3f})",
                   abs(ks - 1.563e7) < 2e4 and abs(ks / k0 - 1.980) < 2e-3 and abs(L.period(ks, m) - 0.7107) < 5e-4))
    checks.append((f"design: flexible building needs k = 5.317e6 N/m, 0.673 times k0 (got {kf:.4g}, x{kf / k0:.3f})",
                   abs(kf - 5.317e6) < 2e4 and abs(kf / k0 - 0.673) < 2e-3 and abs(L.period(kf, m) - 1.2186) < 5e-4))
    checks.append(("design stiffness really gives D = 2 when fed back through the period",
                   abs(L.amplification(L.period(ks, m) / 1.0) - 2) < 1e-9))
    # edge cases
    try:
        L.r_for_amplification(20.0, 0.05)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: asking for D above the resonance peak is refused", raised))
    checks.append(("edge: the peak formula needs zeta below 0.7071; at zeta = 0.7 the maximum is D = 1.000 near r = 0.14 (no real resonance)",
                   abs(L.peak_amplification(0.7)[0] - 1 / (2 * 0.7 * np.sqrt(1 - 0.49))) < 1e-9
                   and abs(L.peak_amplification(0.7)[0] - 1.0) < 5e-3 and abs(L.peak_amplification(0.7)[1] - 0.1414) < 5e-3))
    checks.append(("D falls below 1 for r above 1.41 (D = 1.000 at r = 1.4107 for zeta = 0.05)", abs(L.amplification(1.4107) - 1.0) < 2e-3 and L.amplification(1.5) < 1))
    # assessment answers quoted in Section F
    checks.append(("B: m = 100000 kg, k = 4e6 N/m, ground 1 s: w = 6.325 rad/s, T = 0.9935 s, D = 9.98, sway 0.499 m for a0 = 2 m/s^2",
                   abs(L.omega(4e6, 1e5) - 6.325) < 5e-4 and abs(L.period(4e6, 1e5) - 0.9935) < 5e-5
                   and abs(float(L.amplification(L.period(4e6, 1e5))) - 9.98) < 5e-3 and abs(L.sway_amplitude(2.0, 4e6, 1e5, 1.0) - 0.499) < 5e-4))
    checks.append(("C: at r = 1 the factor is 1/(2 zeta): 25, 10, 5, 2.5 for zeta = 0.02, 0.05, 0.1, 0.2; D(1.5) = 0.794",
                   all(abs(L.amplification(1.0, z) - 1 / (2 * z)) < 1e-9 for z in (0.02, 0.05, 0.1, 0.2)) and abs(L.amplification(1.5) - 0.794) < 5e-4))
    kst = L.design_stiffness(2e5, 1.5, 2.0)
    kfl = L.design_stiffness(2e5, 1.5, 2.0, side="flexible")
    checks.append((f"D: ground period 1.5 s, m = 200000 kg, D = 2: stiff k = 6.948e6 N/m (T = 1.066 s, sway 0.115 m), flexible k = 2.363e6 N/m (T = 1.828 s, sway 0.339 m)",
                   abs(kst - 6.948e6) < 2e3 and abs(L.period(kst, 2e5) - 1.066) < 5e-4 and abs(L.sway_amplitude(2.0, kst, 2e5, 1.5) - 0.115) < 5e-4
                   and abs(kfl - 2.363e6) < 2e3 and abs(L.period(kfl, 2e5) - 1.828) < 5e-4 and abs(L.sway_amplitude(2.0, kfl, 2e5, 1.5) - 0.339) < 5e-4))
    checks.append(("a ground period of 1.5 s with T = 1.5 s needs k = 3.509e6 N/m for m = 200000 kg", abs(L.stiffness_for_period(2e5, 1.5) - 3.509e6) < 2e3))
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
