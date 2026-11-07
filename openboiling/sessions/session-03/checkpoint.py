"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # the piecewise boiling curve
    checks.append(("flux at the CHF superheat equals the CHF", abs(L.boiling_flux(L.DT_CHF) - L.Q_CHF) < 1.0))
    checks.append(("flux at the minimum point equals Q_MIN", abs(L.boiling_flux(L.DT_MIN) - L.Q_MIN) < 1e-6))
    checks.append(("edge: zero superheat gives zero flux, negative superheat gives negative flux",
                   L.boiling_flux(0.0) == 0.0 and L.boiling_flux(-2.0) < 0.0))
    checks.append(("the four regimes are named in order",
                   [L.regime(d) for d in (2.0, 15.0, 60.0, 300.0)] ==
                   ["natural convection", "nucleate boiling", "transition boiling", "film boiling"]))
    checks.append(("a smaller surface factor pushes the CHF to a higher superheat", L.dt_at_chf(0.6) > L.dt_at_chf(1.0) > L.dt_at_chf(1.5)))

    # validation 1: exact solution of the linear (natural convection) case
    run = L.simulate_power(lambda t: 3000.0, t_end=60.0, dt_s=0.005)
    exact = L.exact_natural(3000.0, run["t"])
    err = float(np.max(np.abs(run["dT"] - exact)))
    checks.append((f"validation: the stepper matches the exact exponential (max error {err:.4f} K)", err < 0.01))

    # worked example: steady superheat at 600 kW/m2 and the simulation
    d_hand = (6.0e5 / (1.1e6 / 30.0 ** 3)) ** (1.0 / 3.0)
    run6 = L.simulate_power(L.step_power(6.0e5), t_end=60.0)
    checks.append((f"worked example: 600 kW/m2 gives a steady superheat of 24.5 K by hand ({d_hand:.2f}) and in the simulation ({run6['dT'][-1]:.2f})",
                   abs(d_hand - 24.51) < 0.01 and abs(run6["dT"][-1] - d_hand) < 0.05))
    checks.append(("steady_superheat agrees with the hand calculation", abs(L.steady_superheat(6.0e5) - d_hand) < 1e-6))

    # validation 2: energy conservation
    eb = L.energy_balance(run6)
    checks.append((f"validation: energy in = energy out + stored (residual {abs(eb['residual']) / eb['in']:.1e} of the input)",
                   abs(eb["residual"]) < 1e-3 * eb["in"]))
    runb = L.simulate_power(L.step_power(1.3e6), t_end=60.0)
    ebb = L.energy_balance(runb)
    checks.append(("energy balance also holds through the burnout run", abs(ebb["residual"]) < 1e-3 * ebb["in"]))

    # failure case: burnout
    safe = L.burnout_time(1.0e6)
    burn = L.burnout_time(1.15e6)
    checks.append(("below the CHF there is no burnout", safe is None))
    checks.append((f"failure case: 1150 kW/m2 (above the CHF) burns out after about 20 s ({burn})", burn is not None and 15.0 < burn < 25.0))
    checks.append(("a bigger overload burns out sooner", L.burnout_time(1.5e6) < burn))
    checks.append(("a thicker plate delays burnout, a thinner plate hastens it",
                   L.burnout_time(1.3e6, c_plate=2 * L.C_PLATE) > L.burnout_time(1.3e6) > L.burnout_time(1.3e6, c_plate=0.5 * L.C_PLATE)))
    checks.append(("sensitivity: an active surface runs cooler at the same flux",
                   L.steady_superheat(5e5, 1.5) < L.steady_superheat(5e5, 1.0) < L.steady_superheat(5e5, 0.6)))
    checks.append(("edge: no steady nucleate state above the CHF", L.steady_superheat(1.2e6) is None))

    # hysteresis and temperature control
    h = L.hysteresis_loop()
    up, down = L.hysteresis_flux(h)
    checks.append((f"hysteresis: jump to film boiling at the CHF ({up / 1e3:.0f} kW/m2)", abs(up - L.Q_CHF) < 0.05 * L.Q_CHF))
    checks.append((f"hysteresis: return to nucleate boiling only near the film minimum ({down / 1e3:.0f} kW/m2)",
                   0.0 < down < 2.0 * L.Q_MIN and up / down > 20.0))
    sw, qq = L.temperature_controlled()
    n = len(sw) // 2
    checks.append(("temperature control: flux never exceeds the CHF", float(qq.max()) <= L.Q_CHF * (1 + 1e-9)))
    checks.append(("temperature control: no hysteresis, the way back retraces the way up", np.allclose(qq[:n], qq[n:][::-1])))

    # bubble growth
    t, r = L.growth_numeric(5.0)
    slope = L.loglog_slope(t, r)
    checks.append((f"validation: the growth exponent of the diffusion solver is 0.5 ({slope:.3f})", abs(slope - 0.5) < 0.02))
    ratio = float(r[-1] / L.radius_planar(t[-1], 5.0))
    checks.append((f"validation: numerical R(t) matches the planar formula within 3 percent ({ratio:.3f})", abs(ratio - 1.0) < 0.03))
    tt = np.geomspace(1e-4, 1e-2, 30)
    checks.append(("Plesset-Zwick radius is sqrt(3) times the planar one", np.allclose(L.radius_pz(tt, 5.0) / L.radius_planar(tt, 5.0), np.sqrt(3.0))))
    checks.append(("log-log slope of the analytic scaling is exactly 0.5", abs(L.loglog_slope(tt, L.radius_pz(tt, 5.0), 1e-4) - 0.5) < 1e-9))
    checks.append(("the Jakob number of a 5 K superheat is about 15.0", abs(L.jakob(5.0) - 15.02) < 0.01))
    checks.append(("doubling the superheat doubles the radius at a given time", abs(L.radius_pz(1e-3, 10.0) / L.radius_pz(1e-3, 5.0) - 2.0) < 1e-12))

    # mini-project helper
    checks.append(("mini-project: 15 kW on 0.04 m2 passes, 16 kW fails (fouled surface)",
                   L.design_check(15000.0, 0.04)["ok"] and not L.design_check(16000.0, 0.04)["ok"]))
    # ---- thick plate: 1-D conduction against the lumped model -----------------------------------
    q_ss = 5e5
    steady = {}
    for th in (0.005, 0.02, 0.05):
        rr = L.simulate_plate(lambda t: q_ss, th, t_end=150.0, stop_at_limit=False)
        steady[th] = rr
    errs = {th: abs((r_["T"][0] - r_["T"][-1]) - q_ss * th / L.K_PLATE) / (q_ss * th / L.K_PLATE) for th, r_ in steady.items()}
    checks.append((f"steady temperature difference across the plate is q L / k within 1 percent: 5, 20, 50 mm give {', '.join(f'{100 * v:.4f} %' for v in errs.values())} error (6.25, 25, 62.5 K)",
                   all(v < 0.01 for v in errs.values())))
    sup = steady[0.005]["T"][-1]
    checks.append((f"steady boiling surface superheat equals the lumped steady value {L.steady_superheat(q_ss):.2f} K (got {sup:.2f} K)",
                   abs(sup - L.steady_superheat(q_ss)) / sup < 0.01))
    r5 = L.simulate_plate(lambda t: 2e3, 0.005, t_end=17.25, stop_at_limit=False)
    ex5 = float(L.exact_natural(2e3, 17.25))
    checks.append((f"natural convection (q = 2 kW/m2, no bubbles): the 5 mm plate's mean superheat after one time constant is {r5['T_mean'][-1]:.4f} K against the exact exponential {ex5:.4f} K, within 1 percent",
                   abs(r5["T_mean"][-1] - ex5) / ex5 < 0.01))
    checks.append(("Biot number at the CHF: 0.09 for 1 mm, 0.46 for 5 mm, 1.8 for 20 mm (lumping needs about 0.1 or less)",
                   abs(L.biot_chf(0.001) - 0.092) < 0.001 and abs(L.biot_chf(0.005) - 0.458) < 0.001 and abs(L.biot_chf(0.02) - 1.833) < 0.001))
    cmp_ = {}
    for th in (0.001, 0.005, 0.02):
        cmp_[th] = (L.burnout_time(1.3e6, c_plate=L.RHO_CP * th, t_end=400.0), L.plate_burnout_time(1.3e6, th, t_end=400.0))
    d1 = abs(cmp_[0.001][0] - cmp_[0.001][1]) / cmp_[0.001][0]
    d20 = (cmp_[0.02][0] - cmp_[0.02][1]) / cmp_[0.02][0]
    checks.append((f"burnout time after a step to 1.3 MW/m2: 1 mm plate agrees with the lumped model to {100 * d1:.1f} %, the 20 mm plate burns out {100 * d20:.1f} % earlier ({cmp_[0.02][1]:.1f} s against {cmp_[0.02][0]:.1f} s)",
                   d1 < 0.01 and 0.02 < d20 < 0.07))
    b_a = L.plate_burnout_time(1.3e6, 0.02, dt_s=0.004)
    b_b = L.plate_burnout_time(1.3e6, 0.02, dt_s=0.001)
    b_c = L.plate_burnout_time(1.3e6, 0.02, n=10)
    b_d = L.plate_burnout_time(1.3e6, 0.02, n=40)
    checks.append((f"result does not depend on the time step (0.004 against 0.001 s: {b_a:.2f}, {b_b:.2f} s) or the number of slices (10 against 40: {b_c:.2f}, {b_d:.2f} s)",
                   abs(b_a - b_b) / b_b < 1e-3 and abs(b_c - b_d) / b_d < 1e-3))
    rb = L.simulate_plate(L.step_power(1.3e6, 10.0), 0.02)
    eb = L.plate_energy_balance(rb)
    checks.append((f"energy balance of the 1-D plate: in = out + stored within 0.01 percent (residual {abs(eb['residual']) / eb['in'] * 100:.4f} %)",
                   abs(eb["residual"]) / eb["in"] < 1e-4))
    checks.append(("the heated face is the hottest point and the surface the coolest at burnout",
                   rb["T_back"][-1] >= L.DT_LIMIT and rb["T"][0] > rb["T"][1] > rb["T"][-1]))
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
