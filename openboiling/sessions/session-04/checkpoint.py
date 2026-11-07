"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    A = L.ATM

    # 1. water properties and the interpolation
    p1, p5 = L.props(A), L.props(5.0)
    checks.append((f"steam table: the saturation temperature is {p1['T']:.1f} C at 1 atm and {p5['T']:.1f} C at 5 bar",
                   abs(p1["T"] - 99.97) < 0.05 and abs(p5["T"] - 151.84) < 0.05))
    # independent IAPWS values at pressures that are NOT rows of the table
    ref = {6.0: dict(T=158.83, rho_l=908.59, rho_v=3.1688, h_fg=2085600.0, sigma=0.046844),
           12.0: dict(T=187.96, rho_l=878.35, rho_v=6.1256, h_fg=1985300.0, sigma=0.040405)}
    worst = 0.0
    for p, vals in ref.items():
        got = L.props(p)
        for k, v in vals.items():
            worst = max(worst, abs(got[k] - v) / (v if k != "T" else 273.15 + v))
    checks.append((f"validation: interpolated properties at 6 and 12 bar (not table rows) agree with independent IAPWS values within 0.5 percent (worst {100 * worst:.2f} %)",
                   worst < 0.005))
    ok_err = True
    try:
        L.props(0.1)
        ok_err = False
    except ValueError:
        pass
    try:
        L.props(30.0)
        ok_err = False
    except ValueError:
        pass
    checks.append(("edge: pressures outside 0.5 to 20 bar raise ValueError instead of extrapolating", ok_err))
    checks.append(("edge: the first and last table pressures work", L.props(0.5)["T"] < 82.0 and L.props(20.0)["T"] > 211.0))
    ts = [L.props(p)["T"] for p in np.linspace(0.5, 20.0, 30)]
    checks.append(("the saturation temperature rises with pressure", all(b > a for a, b in zip(ts, ts[1:]))))

    # 2. Zuber CHF
    c1, c5 = L.chf_zuber(A), L.chf_zuber(5.0)
    checks.append((f"CHF at 1 atm is {c1 / 1e6:.3f} MW/m2, within 2 percent of the 1.1 that Sessions 2 and 3 assumed", abs(c1 / 1.1e6 - 1.0) < 0.02))
    checks.append((f"roadmap check: CHF at 5 bar over CHF at 1 atm is {c5 / c1:.3f}, at least 1.3", c5 / c1 >= 1.3 and abs(c5 / c1 - 1.856) < 0.005))
    cs = [L.chf_zuber(p) for p in np.linspace(0.5, 20.0, 40)]
    checks.append(("the CHF rises with pressure all the way from 0.5 to 20 bar", all(b > a for a, b in zip(cs, cs[1:]))))
    checks.append((f"CHF at 0.5 bar is {L.chf_zuber(0.5) / 1e6:.3f} MW/m2", abs(L.chf_zuber(0.5) / 1e6 - 0.828) < 0.002))
    f = L.chf_factors(5.0)
    checks.append((f"the three factors at 5 bar ({f['sqrt_rho_v']:.2f} x {f['h_fg']:.2f} x {f['capillary']:.2f}) multiply to the CHF ratio",
                   abs(f["sqrt_rho_v"] * f["h_fg"] * f["capillary"] - c5 / c1) < 1e-9 and f["sqrt_rho_v"] > 2.0 and f["h_fg"] < 1.0 and f["capillary"] < 1.0))
    checks.append(("the CHF does not depend on the surface constant Csf", L.dt_chf(A, 0.008) != L.dt_chf(A, 0.02) and
                   all(abs(L.boiling_flux(L.dt_chf(A, c), A, c) - c1) < 1.0 for c in (0.008, 0.013, 0.02))))

    # 3. Rohsenow
    q10 = L.rohsenow_flux(10.0, A)
    checks.append((f"Rohsenow at 1 atm and 10 K gives {q10 / 1e3:.0f} kW/m2, within 2 percent of the roadmap's 141", abs(q10 / 141e3 - 1.0) < 0.02))
    checks.append((f"the superheat at the CHF is {L.dt_chf(A):.1f} K at 1 atm and {L.dt_chf(5.0):.1f} K at 5 bar",
                   abs(L.dt_chf(A) - 19.94) < 0.05 and abs(L.dt_chf(5.0) - 16.88) < 0.05))
    checks.append(("the nucleate flux goes as the cube of the superheat", abs(L.rohsenow_flux(20.0, A) / L.rohsenow_flux(10.0, A) - 8.0) < 1e-9))
    checks.append(("the nucleate flux goes as 1 / Csf cubed: Csf 0.0065 carries 8 times the flux", abs(L.rohsenow_flux(10.0, A, 0.0065) / q10 - 8.0) < 1e-9))
    checks.append(("rohsenow_superheat inverts rohsenow_flux", abs(L.rohsenow_superheat(L.rohsenow_flux(7.0, 3.0), 3.0) - 7.0) < 1e-9))
    sup = [L.rohsenow_superheat(5e5, p) for p in (0.5, 1.0, 2.0, 5.0, 10.0, 20.0)]
    checks.append((f"boiling gets easier with pressure: 500 kW/m2 needs {sup[0]:.1f} K at 0.5 bar and {sup[-1]:.1f} K at 20 bar",
                   all(b < a for a, b in zip(sup, sup[1:]))))
    checks.append((f"sensitivity to Csf at 500 kW/m2 and 1 atm: {L.rohsenow_superheat(5e5, A, 0.008):.1f} K for 0.008 against {L.rohsenow_superheat(5e5, A, 0.02):.1f} K for 0.02",
                   L.rohsenow_superheat(5e5, A, 0.008) < L.rohsenow_superheat(5e5, A) < L.rohsenow_superheat(5e5, A, 0.02)))

    # 4. minimum flux and film boiling
    checks.append((f"minimum flux at 1 atm is {L.q_min(A) / 1e3:.1f} kW/m2 and at 5 bar {L.q_min(5.0) / 1e3:.1f} kW/m2",
                   abs(L.q_min(A) / 1e3 - 19.0) < 0.1 and abs(L.q_min(5.0) / 1e3 - 76.2) < 0.2))
    ok = all(abs(L.film_flux(L.dt_min(p), p) - L.q_min(p)) < 1e-3 * L.q_min(p) for p in (0.5, 1.0, 2.0, 5.0, 10.0, 20.0))
    checks.append(("by construction, film boiling at dt_min carries exactly q_min (0.5 to 20 bar)", ok))
    checks.append((f"dt_min grows with pressure ({L.dt_min(A):.0f} K at 1 atm, {L.dt_min(5.0):.0f} K at 5 bar, {L.dt_min(20.0):.0f} K at 20 bar)",
                   L.dt_min(A) < L.dt_min(2.0) < L.dt_min(5.0) < L.dt_min(10.0) < L.dt_min(20.0) and abs(L.dt_min(A) - 188.0) < 1.0))
    checks.append(("film boiling flux rises with the superheat", all(L.film_flux(b, A) > L.film_flux(a, A) for a, b in ((200, 300), (300, 600), (600, 1200)))))

    # 5. the whole curve
    ok_cont, ok_order = True, True
    for p in L.STEAM_TABLE:
        P = p[0]
        for csf in (0.008, 0.013, 0.02):
            d1, d2 = L.dt_chf(P, csf), L.dt_min(P)
            ok_order &= d1 < d2
            ok_cont &= abs(L.boiling_flux(d1 * (1 + 1e-9), P, csf) - L.chf_zuber(P)) < 1e-3 * L.chf_zuber(P)
            ok_cont &= abs(L.boiling_flux(d2 * (1 + 1e-9), P, csf) - L.q_min(P)) < 1e-3 * L.q_min(P)
    checks.append(("the curve is continuous at the CHF and at the minimum, for all 12 pressures and Csf 0.008 to 0.02", ok_cont))
    checks.append(("dt_min is above the superheat at the CHF for all 12 pressures and Csf 0.008 to 0.02", ok_order))
    dd = np.linspace(L.dt_chf(A), L.dt_min(A), 200)
    trans = np.array([L.boiling_flux(d, A) for d in dd])
    nuc = np.array([L.boiling_flux(d, A) for d in np.linspace(3.0, L.dt_chf(A), 200)])
    film = np.array([L.boiling_flux(d, A) for d in np.linspace(L.dt_min(A), 1000.0, 200)])
    checks.append(("shape at 1 atm: nucleate boiling rises, transition boiling falls, film boiling rises",
                   np.all(np.diff(nuc) > 0) and np.all(np.diff(trans) < 0) and np.all(np.diff(film) > 0)))
    allq = np.array([L.boiling_flux(d, A) for d in np.linspace(0.1, L.dt_min(A), 6000)])
    checks.append(("up to the minimum point the highest flux is the CHF (to 0.1 percent) and the lowest after it is q_min",
                   abs(allq.max() - c1) < 1e-3 * c1 and abs(allq[np.argmax(allq):].min() - L.q_min(A)) < 1e-2 * L.q_min(A)))
    checks.append(("the four regimes are named in order at 1 atm",
                   [L.regime(d, A) for d in (1.0, 10.0, 50.0, 400.0)] == ["natural convection", "nucleate boiling", "transition boiling", "film boiling"]))
    checks.append(("edge: zero superheat gives zero flux, negative superheat gives negative flux",
                   L.boiling_flux(0.0, A) == 0.0 and L.boiling_flux(-2.0, A) < 0.0))

    # 6. what the designer gets
    r = L.pressure_row(5.0)
    checks.append(("the pressure study row for 5 bar agrees with the individual functions",
                   abs(r["chf"] - c5) < 1e-6 and abs(r["q_min"] - L.q_min(5.0)) < 1e-6 and abs(r["chf_ratio"] - c5 / c1) < 1e-12))
    shipped_gap = 1.0 - L.Q_CHF_SHIPPED / c5
    checks.append((f"the hand-picked 1.1 MW/m2 curve underestimates the CHF at 5 bar by {100 * shipped_gap:.0f} percent", abs(shipped_gap - 0.465) < 0.005))
    b1, b5, b5x, b10 = L.burnout_time(1.3e6, A), L.burnout_time(1.3e6, 5.0), L.burnout_time(2.2e6, 5.0), L.burnout_time(2.2e6, 10.0)
    checks.append((f"failure case: a step to 1.3 MW/m2 burns the plate out at 1 atm after {b1:.1f} s" if b1 else "failure case: 1.3 MW/m2 should burn out at 1 atm",
                   b1 is not None and 15.0 < b1 < 22.0))
    checks.append(("the same 1.3 MW/m2 is safe at 5 bar (below the CHF of 2.06)", b5 is None))
    checks.append(("2.2 MW/m2 burns out at 5 bar but not at 10 bar (CHF 2.62)", b5x is not None and b10 is None))
    checks.append(("below the CHF there is no burnout at 1 atm (1.0 MW/m2)", L.burnout_time(1.0e6, A) is None))
    checks.append(("edge: no steady nucleate state above the CHF", L.steady_superheat(1.2e6, A) is None and L.steady_superheat(1.0e6, A) is not None))
    run = L.simulate_power(3e5, A, t_end=40.0)
    checks.append((f"the simulation settles at the steady superheat (simulated {run['dT'][-1]:.2f} K, steady {L.steady_superheat(3e5, A):.2f} K)",
                   abs(run["dT"][-1] - L.steady_superheat(3e5, A)) < 0.05))

    rows = {p: L.design_row(p) for p in (0.5, A, 2.0, 5.0, 10.0)}
    checks.append(("mini-project: allowed flux (60 percent of the CHF) is 497, 665, 873, 1234 and 1570 kW/m2 at 0.5, 1 atm, 2, 5 and 10 bar",
                   all(abs(rows[p]["flux"] / 1e3 - v) < 1.0 for p, v in zip(rows, (497, 665, 873, 1234, 1570)))))
    checks.append(("mini-project: wall temperatures are 99.5, 116.8, 135.9, 166.1 and 193.1 C",
                   all(abs(rows[p]["wall_c"] - v) < 0.1 for p, v in zip(rows, (99.5, 116.8, 135.9, 166.1, 193.1)))))
    checks.append(("mini-project: the wall superheat at the allowed flux falls with pressure (18.2 K down to 13.2 K)",
                   all(rows[a]["superheat"] > rows[b]["superheat"] for a, b in zip(list(rows), list(rows)[1:]))))
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
