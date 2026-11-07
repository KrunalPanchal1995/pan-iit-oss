"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    s0 = L.release(120.0)

    # worked example: the triple-jump sizes by hand
    sizes = [g * 0.02 for g in L.TRIPLE_JUMP]
    checks.append((f"worked example: gamma1 = 1 / (2 - 2^(1/3)) = 1.3512 and gamma0 = -1.7024, so h = 0.02 s splits into {sizes[0]:.6f}, {sizes[1]:.6f}, {sizes[2]:.6f} s",
                   abs(L.GAMMA1 - 1.351207) < 1e-5 and abs(L.GAMMA0 + 1.702414) < 1e-5 and abs(sum(sizes) - 0.02) < 1e-15
                   and abs(sizes[0] - 0.027024) < 1e-6 and abs(sizes[1] + 0.034048) < 1e-6))
    one, cubes = L.order_conditions(L.TRIPLE_JUMP)
    naive = L.order_conditions((1 / 3, 1 / 3, 1 / 3))
    checks.append((f"order conditions: the sizes sum to {one:.1f} and their cubes to {cubes:.0e}; three equal thirds fail the cube test (cubes sum to {naive[1]:.3f})",
                   abs(one - 1.0) < 1e-12 and abs(cubes) < 1e-12 and abs(naive[1] - 1 / 9) < 1e-12))

    # symplectic and reversible: step h then -h returns to the start
    gentle = L.START_GENTLE
    rev = {n: L.reversibility_error(f, gentle, 0.05) for n, f in (("rk4", L.rk4_step), ("midpoint", L.midpoint_step), ("composed", L.composed_step))}
    checks.append((f"reversibility: step h then step -h returns to the start for the midpoint rule ({rev['midpoint']:.0e}) and the composition ({rev['composed']:.0e}) but not for RK4 ({rev['rk4']:.0e})",
                   rev["midpoint"] < 1e-12 and rev["composed"] < 1e-12 and rev["rk4"] > 1e-9))
    checks.append(("the composition changes nothing when the three sizes are 0 and 1 and 0 (a single midpoint step)",
                   max(abs(a - b) for a, b in zip(L.composed_step(gentle, 0.03, (0.0, 1.0, 0.0)), L.midpoint_step(gentle, 0.03))) < 1e-14))

    # order of accuracy
    hs = [0.1, 0.05, 0.025, 0.0125]
    ref = L.reference_state(gentle, 0.4)
    e_mid = [L.state_error(L.midpoint_step, gentle, 0.4, h, ref) for h in hs]
    e_com = [L.state_error(L.composed_step, gentle, 0.4, h, ref) for h in hs]
    o_mid, o_com = L.observed_orders(e_mid)[-1], L.observed_orders(e_com)[-1]
    checks.append((f"order: halving h from 0.025 to 0.0125 divides the midpoint error by {2 ** o_mid:.1f} (order {o_mid:.2f}) and the composition error by {2 ** o_com:.1f} (order {o_com:.2f})",
                   1.9 < o_mid < 2.1 and 3.8 < o_com < 4.2))
    checks.append((f"hand check (Section F): from {e_com[1]:.2e} at h = 0.05 an order-4 method predicts {e_com[1] / 256:.2e} at h = 0.0125; measured {e_com[3]:.2e}",
                   abs(e_com[3] / (e_com[1] / 256) - 1) < 0.15))

    # work counting
    L.CALLS[0] = 0
    s = gentle
    for _ in range(50):
        s = L.midpoint_step(s, 0.02)
    w_mid = L.CALLS[0]
    L.CALLS[0] = 0
    s = gentle
    for _ in range(50):
        s = L.composed_step(s, 0.02)
    w_com = L.CALLS[0]
    checks.append((f"work: one composed step costs {w_com / w_mid:.1f} times a midpoint step in rate evaluations (between 3 and 4.5)", 3.0 < w_com / w_mid < 4.5))

    # the roadmap test: 1000 s at h = 0.02, 120 degree release. Chaos makes one run's worst value luck,
    # so each solver is run from 5 nearby starts and the median is used.
    worst = {}
    L.NOT_CONVERGED[0] = 0
    for name, f in (("RK4", L.rk4_step), ("midpoint", L.midpoint_step), ("composition", L.composed_step)):
        worst[name] = float(np.median([np.abs(L.drift_curve(f, s, 1000.0, 0.02)[1]).max() for s in L.nearby_starts(120.0, 5)]))
    checks.append((f"1000 s at h = 0.02 s, 120 degrees (median of 5 nearby starts): worst energy error {worst['composition']:.4f} of E_ref for the composition, at most 0.01",
                   worst["composition"] <= 0.01))
    checks.append((f"for comparison the midpoint rule gives {worst['midpoint']:.4f} (above 0.01) and RK4 gives {worst['RK4']:.3f} (above 0.1)",
                   worst["midpoint"] > 0.01 and worst["RK4"] > 0.1))
    checks.append(("all solves converged in those runs (no silent failures)", L.NOT_CONVERGED[0] == 0))

    # failure case: coarse steps
    mid_bad = L.ladder_results(L.midpoint_step, 120.0, 60.0, [0.035])[0]
    com_bad = L.ladder_results(L.composed_step, 120.0, 60.0, [0.035])[0]
    checks.append((f"failure case: at h = 0.035 s the midpoint rule still runs (typical energy error {mid_bad[1]:.2f}) but the composition fails (error {com_bad[1]}, {com_bad[3]} solves did not converge)",
                   math.isfinite(mid_bad[1]) and mid_bad[1] < 0.3 and not math.isfinite(com_bad[1]) and com_bad[3] > 0))

    # cost and accuracy (typical largest energy error over 60 s; ladders are subsets of the ones in the lesson)
    res_m = L.ladder_results(L.midpoint_step, 120.0, 60.0, [0.015, 0.0075, 0.0025])
    res_c = L.ladder_results(L.composed_step, 120.0, 60.0, [0.02, 0.015, 0.01])
    m2, c2 = L.cheapest_for_tolerance(res_m, 1e-2), L.cheapest_for_tolerance(res_c, 1e-2)
    m3, c3 = L.cheapest_for_tolerance(res_m, 1e-3), L.cheapest_for_tolerance(res_c, 1e-3)
    m4, c4 = L.cheapest_for_tolerance(res_m, 1e-4), L.cheapest_for_tolerance(res_c, 1e-4)
    checks.append((f"mini-project: for an energy error of 1e-2 the midpoint rule is cheaper ({m2[0] if m2 else None} against {c2[0] if c2 else None} rate evaluations); the same at 1e-3 ({m3[0] if m3 else None} against {c3[0] if c3 else None})",
                   m2 is not None and c2 is not None and m3 is not None and c3 is not None and m2[0] < c2[0] and m3[0] < c3[0]))
    checks.append((f"mini-project: for 1e-4 only the composition reaches it on this ladder (h = {c4[1] if c4 else None}, {c4[0] if c4 else None} evaluations; the midpoint rule's best is {res_m[-1][1]:.1e})",
                   m4 is None and c4 is not None and c4[2] < 1e-4 and res_m[-1][1] > 5e-5))
    ref5 = L.reference_state(s0, 5.0)
    e_m, w_m = L.trajectory_error_and_work(L.midpoint_step, s0, 5.0, 0.003125, ref5)
    e_c, w_c = L.trajectory_error_and_work(L.composed_step, s0, 5.0, 0.0125, ref5)
    checks.append((f"mini-project: for the state after 5 s, similar work ({w_m} against {w_c} evaluations) gives an error {e_m:.1e} for the midpoint rule and {e_c:.1e} for the composition (at least 5 times smaller)",
                   w_c < 1.3 * w_m and e_c < e_m / 5))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
