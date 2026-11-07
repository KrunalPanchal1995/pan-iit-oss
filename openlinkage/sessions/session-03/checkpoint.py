"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    leg = L.LEG
    # worked example: crank angle 0 for ground 4.4, crank 1, coupler 3.5, rocker 2.25, foot at k = 1.6
    pa, pb = L.joints(0.0, **leg)
    foot = L.foot_path(0.0, **leg)[0]
    vel, w3, w4 = L.analytic_velocity(0.0, **leg)
    checks.append(("worked example: at crank angle 0 the pin B is at (3.757, -2.156) and the foot at (5.411, -3.450)",
                   np.allclose(pb[0], [3.7570, -2.1560], atol=1e-3) and np.allclose(foot, [5.4112, -3.4496], atol=1e-3)))
    checks.append(("worked example: the instant centre is A itself, so w4/w2 = 1/(1 - 4.4) = -5/17 and MA = 3.4",
                   abs(w4[0] + 5.0 / 17.0) < 1e-9 and abs(L.torque_ratio_statics(0.0, **leg)[0] - 3.4) < 1e-9
                   and abs(L.rocker_speed_instant_centre(0.0, **leg)[0] + 5.0 / 17.0) < 1e-9))
    u = (pb[0] - pa[0]) / 3.5
    arm_crank = abs(pa[0][0] * u[1] - pa[0][1] * u[0])
    arm_rocker = abs((pb[0][0] - 4.4) * u[1] - pb[0][1] * u[0])
    checks.append(("worked example: coupler direction (0.788, -0.616); torque arms 0.616 about O2 and 2.094 about O4",
                   np.allclose(u, [0.7877, -0.6160], atol=1e-3) and abs(arm_crank - 0.616) < 1e-3 and abs(arm_rocker - 2.0945) < 2e-3))
    theta = np.radians(np.arange(0.0, 360.0, 1.0))
    err, drift = L.loop_closure_error(theta, **leg)
    checks.append(("loop-closure error and bar-length change are below 1e-12 over a full turn", err < 1e-12 and drift < 1e-12))
    vel, w3, w4 = L.analytic_velocity(theta, **leg)
    fd = L.finite_difference_velocity(theta, **leg)
    checks.append(("foot velocity: analytic Jacobian and finite differences agree to 1e-7", np.abs(vel - fd).max() < 1e-7))
    pa, pb = L.joints(theta, **leg)
    ok = np.abs(pb[:, 1] - pa[:, 1]) > 1e-3
    checks.append(("rocker speed ratio: Jacobian and instant centre agree to 1e-9",
                   np.abs(w4[ok] - L.rocker_speed_instant_centre(theta, **leg)[ok]).max() < 1e-9))
    stat = L.torque_ratio_statics(theta, **leg)
    good = np.abs(w4) > 0.2
    checks.append(("power balance: torque ratio from statics equals |w2/w4| (relative difference below 1e-9)",
                   (np.abs(stat - np.abs(1.0 / w4))[good] / np.abs(1.0 / w4)[good]).max() < 1e-9))
    line = np.array([[0.0, 0.0], [1.0, 0.1], [2.0, 0.0]])
    straight = np.array([[0.0, 0.0], [1.0, 1.0], [3.0, 3.0], [4.0, 4.0]])
    checks.append(("hand calculation: three points (0,0), (1,0.1), (2,0) deviate 0.0667 from their best line; an exact line deviates 0",
                   abs(L.window_deviations(line, 2)[0] - 0.1 / 1.5) < 1e-9 and L.window_deviations(straight, 3)[0] < 1e-12))
    rep = L.stance_report(span=180, k=L.K_FOOT, **leg)
    checks.append(("our leg: stance deviation 0.1658 (7.74 percent of the 2.143 stride), lift 1.147, no dig, line tilt 47 degrees",
                   abs(rep["deviation"] - 0.1658) < 1e-3 and abs(rep["stride"] - 2.143) < 5e-3 and abs(rep["lift"] - 1.147) < 5e-3
                   and rep["dig"] == 0.0 and abs(rep["tilt_deg"] - 47.4) < 0.5))
    mu_leg = L.min_transmission_angle(**leg)
    srt = sorted(leg.values())
    checks.append(("our leg is a Grashof crank-rocker (s + l = 5.40 < p + q = 5.75) with smallest transmission angle 68.6 degrees",
                   abs(srt[0] + srt[3] - 5.40) < 1e-9 and abs(srt[1] + srt[2] - 5.75) < 1e-9 and abs(mu_leg - 68.6) < 0.1
                   and L.crank_limits(**leg) is None))
    flip = L.stance_report(span=180, k=L.K_FOOT, **dict(leg, a=4.0))
    checks.append(("a ground bar of 4.0 instead of 4.4 flips the swing to the wrong side: the foot digs 1.164 (58 percent of the stride)",
                   abs(flip["dig"] - 1.164) < 5e-3 and abs(flip["dig"] / flip["stride"] - 0.583) < 5e-3))
    hk = L.stance_report(span=180, k=2.0, **L.HOEKEN)
    checks.append(("Hoeken-type proportions are flatter (0.125 percent of stride) but the foot digs 0.894 below its stance line",
                   abs(hk["deviation"] / hk["stride"] - 0.00125) < 1e-4 and abs(hk["dig"] - 0.894) < 5e-3
                   and abs(hk["stride"] - 4.0) < 1e-3))
    lam = L.LAMBDA
    ls = sorted(lam.values())
    lr = L.stance_report(span=180, k=1.25, **lam)
    checks.append(("lambda proportions 4:1:2:5 are a change-point linkage (s + l = p + q = 6): 0.54 percent stance, tilted 62 degrees, digging 0.336",
                   ls[0] + ls[3] == ls[1] + ls[2] and abs(lr["deviation"] / lr["stride"] - 0.00543) < 2e-4
                   and abs(lr["tilt_deg"] - 62.1) < 0.5 and abs(lr["dig"] - 0.336) < 5e-3))
    sens = L.sensitivity(leg)
    checks.append(("every 1 percent bar error changes the stride by under 2 percent and the deviation by under 5 percent, and no dig appears",
                   all(abs(s["stride"] / rep["stride"] - 1) < 0.02 and abs(s["deviation"] / rep["deviation"] - 1) < 0.05
                       and s["dig"] == 0.0 for s in sens.values())))
    fail = dict(a=4.4, b=1.0, c=3.5, d=1.5)
    fs = sorted(fail.values())
    lim = L.crank_limits(**fail)
    checks.append(("failure: a rocker of 1.5 breaks Grashof (s + l = 5.4 > p + q = 5.0) and the crank sticks at 121.82 degrees",
                   fs[0] + fs[3] > fs[1] + fs[2] and lim is not None and abs(lim[0] - 121.82) < 0.01))
    checks.append(("failure: the transmission angle there has collapsed to 180 degrees",
                   abs(L.transmission_angle_at(np.radians(lim[0]), **fail) - 180.0) < 0.01))
    try:
        L.joints(np.radians((lim[0] + lim[1]) / 2.0 if lim[1] > lim[0] else lim[0] + 1.0), **fail)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: an unreachable crank angle raises ValueError", raised))
    spread = L.stance_speed_spread(**leg)
    checks.append(("the foot speed along the stance varies by 221 percent of its mean (it nearly stops at both ends of the stance)",
                   abs(spread - 2.21) < 0.02))
    stride_m, stance_s = rep["stride"] * 0.05, rep["duty"] * 1.0
    checks.append(("hand calculation: crank 0.05 m at 1 rev/s gives a 0.107 m stride and a 0.214 m/s mean stance speed",
                   abs(stride_m - 0.1072) < 5e-4 and abs(stride_m / stance_s - 0.2143) < 1e-3))
    top = L.tune_leg()
    best = top[0]
    checks.append(("mini-project: the best acceptable leg is a = 4.5, k = 1.4 with deviation 2.94 percent of a 2.182 stride",
                   best[1] == 4.5 and best[2] == 1.4 and abs(best[0] - 2.939) < 0.01 and abs(best[5] - 2.182) < 5e-3))
    checks.append(("mini-project: the tuned leg lifts 37.1 percent of the stride, never digs, and its smallest transmission angle is 71.3 degrees",
                   abs(best[3] - 37.1) < 0.2 and best[4] == 0.0 and abs(best[6] - 71.3) < 0.1))
    checks.append(("mini-project: our leg (deviation 7.74 percent) is acceptable but 2.6 times less straight than the tuned leg",
                   abs(100 * rep["deviation"] / rep["stride"] - 7.74) < 0.02 and abs(7.738 / best[0] - 2.63) < 0.03))
    tune_rep = L.stance_report(4.5, 1.0, 3.5, 2.25, 1.4, 180)
    mount = L.stance_report(4.608, 1.0, 3.546, 2.116, 1.74, 180)
    checks.append(("buildability: the lowest pin is 1.06 under the stance line for our leg and 1.36 for the tuned leg",
                   abs(rep["pin_low"] + 1.064) < 0.01 and abs(tune_rep["pin_low"] + 1.358) < 0.01))
    checks.append(("roadmap: a leg (4.608, 1, 3.546, 2.116, k = 1.74) keeps every pin above the line, no dig, deviation 5.3 percent, lift 49 percent, smallest mu 74 degrees",
                   mount["pin_low"] >= 0.0 and mount["dig"] == 0.0 and abs(100 * mount["deviation"] / mount["stride"] - 5.3) < 0.1
                   and abs(100 * mount["lift"] / mount["stride"] - 49.1) < 0.5 and abs(L.min_transmission_angle(4.608, 1.0, 3.546, 2.116) - 74.4) < 0.2))
    cliff = L.stance_report(4.5, 1.0, 3.5, 2.25, 1.3, 180)
    checks.append(("next to the winner (a = 4.5, k = 1.3) the swing has flipped: lift is -1.7 percent of the stride",
                   abs(cliff["lift"] / cliff["stride"] + 0.017) < 0.002))
    rng = np.random.default_rng(4)
    good_n = 0
    for _ in range(1000):
        e = 1 + rng.uniform(-0.03, 0.03, 5)
        try:
            r2 = L.stance_report(4.5 * e[0], 1.0 * e[1], 3.5 * e[2], 2.25 * e[3], 1.4 * e[4], 180)
        except ValueError:
            continue
        good_n += r2["dig"] <= 0.005 * r2["stride"]
    checks.append(("roadmap baseline: with 3 percent random errors the tuned leg keeps no dig in under 93 percent of 1000 trials",
                   good_n < 930))
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
