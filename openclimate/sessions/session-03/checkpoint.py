"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c = L.heat_capacity(70.0)
    checks.append((f"worked example: 70 m ocean layer has C = {c:.2f} W yr/(m2 K) (hand value 9.07)", abs(c - 9.07) < 0.01))
    lam = L.lambda_for_ecs(3.0)
    checks.append(("worked example: F2x = 5.35 ln 2 = 3.708 W/m2 and lambda = 1.236 W/(m2 K) for ECS 3 K",
                   abs(L.F2X - 3.708) < 1e-3 and abs(lam - 1.236) < 1e-3))
    checks.append(("worked example: time constant tau = C / lambda = 7.34 yr", abs(c / lam - 7.34) < 0.01))
    checks.append(("worked example: exact warming 10 yr after doubling is 2.23 K", abs(float(L.step_response(L.F2X, lam, 10.0)) - 2.232) < 0.002))
    run = L.run_linear_model(lambda _: L.F2X, lam, 60.0, dt=0.1)
    err = np.max(np.abs(run["T"] - L.step_response(L.F2X, lam, run["t"])))
    checks.append((f"simulation matches the exact step response (max error {err:.4f} K < 0.02 K)", err < 0.02))
    fine = L.run_linear_model(lambda _: L.F2X, lam, 20.0, dt=0.01)
    err_fine = np.max(np.abs(fine["T"] - L.step_response(L.F2X, lam, fine["t"])))
    checks.append(("convergence: ten times smaller step gives about ten times smaller error (first order)",
                   5.0 < np.max(np.abs(L.run_linear_model(lambda _: L.F2X, lam, 20.0, dt=0.1)["T"] - L.step_response(L.F2X, lam, np.arange(201) * 0.1))) / err_fine < 15.0))
    checks.append(("equilibrium: after 60 yr the warming equals F / lambda = ECS within 0.01 K", abs(run["T"][-1] - 3.0) < 0.01))
    checks.append(("energy conservation: heat stored C T equals the integrated imbalance", abs(run["stored"] - run["absorbed"]) < 1e-9))
    zero = L.run_linear_model(lambda _: 0.0, lam, 20.0)
    checks.append(("no forcing, no warming", np.max(np.abs(zero["T"])) == 0.0))
    eps0 = 2.0 * (1.0 - (L.S_EARTH * 0.7 / 4 / L.SIGMA) / 288.0 ** 4)
    _, ts = L.run_layer_model(260.0, eps0, 40.0)
    checks.append(("nonlinear one-layer model relaxes to the Session 2 equilibrium (288 K)", abs(ts[-1] - 288.0) < 1e-3))
    checks.append((f"Planck response 4 OLR / Ts = {L.planck_lambda(eps0):.2f} W/(m2 K) (about 3.3)", abs(L.planck_lambda(eps0) - 3.31) < 0.02))
    checks.append(("CO2 forcing: zero at 280 ppm, 3.71 W/m2 at 560 ppm, 7.42 at 1120 (log law)",
                   abs(float(L.co2_forcing(280.0))) < 1e-12 and abs(float(L.co2_forcing(560.0)) - 3.708) < 1e-3
                   and abs(float(L.co2_forcing(1120.0)) - 2 * float(L.co2_forcing(560.0))) < 1e-12))
    path = L.co2_path(1.0, 560.0)
    checks.append(("1 %/yr ramp doubles CO2 in 69.7 yr and then holds at the ceiling",
                   abs(path(69.66) - 560.0) < 0.1 and path(150.0) == 560.0))
    r = L.run_linear_model(lambda x: float(L.co2_forcing(path(x))), lam, 200.0)
    at_double = float(np.interp(np.log(2) / np.log(1.01), r["t"], r["T"]))
    checks.append((f"transient warming at doubling ({at_double:.2f} K) is below the ECS (3 K): warming in the pipeline",
                   2.0 < at_double < 3.0 and abs(r["T"][-1] - 3.0) < 0.01))
    checks.append(("the energy imbalance is positive while warming and near zero at the end",
                   r["N"][500] > 0.1 and abs(r["N"][-1]) < 1e-3))
    deep = L.run_linear_model(lambda _: L.F2X, lam, 10.0, depth_m=200.0)["T"][-1]
    checks.append(("a deeper ocean layer warms more slowly", deep < run["T"][100]))
    ceilings = [L.max_co2_for_limit(2.0, L.lambda_for_ecs(e)) for e in (2.5, 3.0, 4.0)]
    checks.append((f"mini-project: CO2 ceilings for 2 K are {ceilings[0]:.0f}, {ceilings[1]:.0f}, {ceilings[2]:.0f} ppm for ECS 2.5, 3, 4 K",
                   abs(ceilings[0] - 488) < 1 and abs(ceilings[1] - 444) < 1 and abs(ceilings[2] - 396) < 1))
    checks.append(("round trip: the ceiling gives exactly 2 K of equilibrium warming",
                   abs(float(L.co2_forcing(ceilings[1])) / L.lambda_for_ecs(3.0) - 2.0) < 1e-9))
    bad = 0
    for call in (lambda: L.co2_forcing(0.0), lambda: L.run_linear_model(lambda _: 1.0, -1.0, 10.0), lambda: L.heat_capacity(0.0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
