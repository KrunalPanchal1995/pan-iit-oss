"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("partition coefficient K = 19/62 = 0.306 and liquidus of 40 wt% Sn is 234.1 C",
                   abs(L.K - 19.0 / 62.0) < 1e-12 and abs(L.t_liquidus(40.0) - 234.09) < 0.01))
    # constant ratio of solid to liquid composition on every tie line
    ratios = [((L.T_PB - T) / L.M_S) / ((L.T_PB - T) / L.M_L) for T in (200.0, 250.0, 300.0)]
    checks.append(("both lines start at pure Pb, so C_solid / C_liquid = K on every tie line", np.allclose(ratios, L.K)))

    # hand calculation: pro-eutectic alpha and eutectic mixture for 40 wt% Sn
    pe = (62.0 - 40.0) / (62.0 - 19.0)
    checks.append((f"worked example: 40 wt% Sn just above 183 C is {100 * pe:.1f} percent pro-eutectic alpha and {100 * (1 - pe):.1f} percent liquid that becomes eutectic",
                   abs(L.pro_eutectic_fraction(40.0) - pe) < 1e-12 and abs(L.eq_solid_fraction(183.0 + 1e-7, 40.0) - pe) < 1e-6
                   and round(100 * pe, 1) == 51.2))
    checks.append(("eutectic composition 62 wt% Sn melts at one temperature (no band): f_s jumps 0 to 1 at 183 C",
                   L.eq_solid_fraction(183.1, 62.0) == 0.0 and L.eq_solid_fraction(183.0, 62.0) == 1.0))
    checks.append(("an alloy below 19 wt% Sn is fully solid after its solidus, with no eutectic",
                   L.eq_solid_fraction(L.t_solidus(10.0) - 0.01, 10.0) == 1.0 and L.t_solidus(10.0) > L.T_E))

    # --- the cooling simulation, constant heat loss q
    x, q = 40.0, 0.5
    tl = L.t_liquidus(x)
    T0, T_end = tl + 40.0, 120.0
    fs_eq = lambda T: L.eq_solid_fraction(T, x)
    t, T, f = L.simulate_cooling(fs_eq, L.constant_q(q), T0, T_end)
    t_liq = L.time_to_reach(t, T, tl - 1e-9)
    hand = L.C_HEAT * 40.0 / q
    checks.append((f"liquid cools at q/c: reaching the liquidus takes c*40/q = {hand:.1f} s (got {t_liq:.2f})", abs(t_liq - hand) < 0.05))
    arrest_hand = L.L_HEAT * (1.0 - pe) / q
    arrest = L.arrest_duration(t, T, L.T_E)
    checks.append((f"worked example: eutectic arrest lasts L*(1 - {pe:.3f})/q = {arrest_hand:.1f} s (simulated {arrest:.1f} s)",
                   abs(arrest - arrest_hand) < 0.2 and round(arrest_hand, 1) == 48.8))
    # energy conservation: heat removed = sensible + latent
    heat_removed = q * t[-1]
    heat_hand = L.C_HEAT * (T0 - T[-1]) + L.L_HEAT * 1.0
    checks.append((f"energy: heat removed q*t = {heat_removed:.2f} J/g equals c*dT + L = {heat_hand:.2f} J/g",
                   abs(heat_removed - heat_hand) < 2 * q * (t[1] - t[0])))
    checks.append(("total latent heat released is L (frozen fraction ends at 1)", abs(L.L_HEAT * f[-1] - L.L_HEAT) < 1e-6))
    # frozen fraction from the energy balance reproduces the lever rule
    pick = [i for i in range(len(T)) if 190.0 < T[i] < tl - 0.5][::37]
    err = max(abs(f[i] - L.eq_solid_fraction(T[i], x)) for i in pick)
    checks.append((f"simulated frozen fraction equals the lever rule between liquidus and 183 C (max error {err:.1e})", len(pick) > 5 and err < 1e-6))
    # slope change at the liquidus: rate = q / (c + L |d fs / dT|)
    Tm = 225.0
    dfs = (L.eq_solid_fraction(Tm + 0.01, x) - L.eq_solid_fraction(Tm - 0.01, x)) / 0.02
    rate_hand = q / (L.C_HEAT - L.L_HEAT * dfs)
    rate_sim = 2.0 / (L.time_to_reach(t, T, Tm - 1.0) - L.time_to_reach(t, T, Tm + 1.0))
    checks.append((f"slope change: rate at 225 C is {rate_hand:.2f} K/s (hand) and {rate_sim:.2f} K/s (simulated), slower than q/c = {q / L.C_HEAT:.1f}",
                   abs(rate_sim - rate_hand) / rate_hand < 0.02 and rate_hand < q / L.C_HEAT))

    # Newtonian cooling of the liquid against the exact exponential
    h = 0.002
    t2, T2, _ = L.simulate_cooling(fs_eq, L.newtonian_q(h), T0, 120.0)
    t_chk = 5.0
    T_exact = 25.0 + (T0 - 25.0) * math.exp(-h * t_chk / L.C_HEAT)
    T_num = float(np.interp(t_chk, t2, T2))
    checks.append((f"Newtonian cooling of the liquid matches the exponential (exact {T_exact:.2f} C, simulated {T_num:.2f} C)", abs(T_exact - T_num) < 0.1))

    # --- Scheil
    k = L.K
    fl = 0.1
    closed = 10.0 * fl ** (k - 1.0)
    rk4 = L.scheil_by_integration(10.0, 0.9)
    checks.append((f"Scheil: C_L = C0 f_L^(k-1) = {closed:.2f} wt% Sn at f_L = 0.1 equals the numerical mass-balance integration ({rk4:.2f})",
                   abs(closed - rk4) < 1e-4 and abs(closed - 49.38) < 0.01))
    mb = L.scheil_mass_balance(10.0, 0.9)
    checks.append((f"Scheil conserves Sn: solid plus liquid carry {mb:.6f} of the total", abs(mb - 1.0) < 1e-6))
    checks.append(("Scheil start: the first solid has composition k*C0 = 3.06 wt% Sn for C0 = 10",
                   abs(float(L.scheil_solid_composition(1.0, 10.0)) - 3.0645) < 1e-3 and abs(float(L.scheil_liquid_composition(1.0, 10.0)) - 10.0) < 1e-12))
    fe = L.scheil_eutectic_fraction(10.0)
    checks.append((f"coring and failure of equilibrium: Scheil makes {100 * fe:.1f} percent eutectic in a 10 wt% Sn alloy where the lever rule says 0",
                   abs(fe - 0.0720) < 5e-4 and L.eq_solid_fraction(L.T_E + 0.01, 10.0) == 1.0))
    checks.append(("segregation ratio: rim / core Sn = C_E / C0 = 6.2 for C0 = 10",
                   abs(19.0 / float(L.scheil_solid_composition(1.0, 10.0)) - 6.2) < 1e-9))
    # Scheil cooling curve has an extra arrest at 183 C that the equilibrium curve lacks
    ts, Ts, _ = L.simulate_cooling(lambda T_: L.scheil_solid_fraction(T_, 10.0), L.constant_q(q), L.t_liquidus(10.0) + 40.0, 120.0)
    te, Te, _ = L.simulate_cooling(lambda T_: L.eq_solid_fraction(T_, 10.0), L.constant_q(q), L.t_liquidus(10.0) + 40.0, 120.0)
    a_s, a_e = L.arrest_duration(ts, Ts, L.T_E), L.arrest_duration(te, Te, L.T_E)
    checks.append((f"Scheil cooling curve shows a 183 C arrest of {a_s:.1f} s (= L*{fe:.3f}/q); equilibrium shows {a_e:.1f} s",
                   abs(a_s - L.L_HEAT * fe / q) < 0.2 and a_e < 0.05))
    # Clyne-Kurz limits
    checks.append(("back-diffusion limits: a' = 0 gives Scheil, a' = 0.5 gives the lever rule (40 wt% Sn: 48.8 percent eutectic)",
                   abs(L.clyne_kurz_eutectic_fraction(10.0, 0.0) - fe) < 1e-9
                   and abs(L.clyne_kurz_eutectic_fraction(40.0, 0.5) - L.eutectic_mixture_fraction(40.0)) < 1e-9
                   and abs(L.alpha_prime(1e-6)) < 1e-5 and abs(L.alpha_prime(1e4) - 0.5) < 1e-3))
    # cooling-rate sensitivity (the failure case)
    res = {}
    for qq in (0.005, 0.5, 5.0, 50.0):
        tf = L.freezing_time(10.0, qq)
        res[qq] = 100 * L.clyne_kurz_eutectic_fraction(10.0, L.alpha_prime(L.back_diffusion_alpha(tf)))
    checks.append((f"slow cooling follows the diagram: eutectic {res[0.005]:.1f} % at 0.005 W/g and {res[0.5]:.1f} % at 0.5 W/g",
                   res[0.005] == 0.0 and res[0.5] == 0.0))
    checks.append((f"fast cooling breaks it: eutectic {res[5.0]:.1f} % at 5 W/g and {res[50.0]:.1f} % at 50 W/g (Scheil limit 7.2 %)",
                   abs(res[5.0] - 5.8) < 0.1 and abs(res[50.0] - 7.07) < 0.05 and res[50.0] <= 100 * fe))
    checks.append(("homogenising time scale lambda^2/D = 400 s", abs(L.LAMBDA ** 2 / L.D_SOLID - 400.0) < 1e-6))

    # --- mini-project design
    t30 = L.temperature_for_liquid_fraction(30.0, 0.6)
    checks.append((f"design: 30 wt% Sn is 60 percent liquid at {t30:.1f} C (lever rule check)",
                   abs(L.liquid_fraction_eq(30.0, t30) - 0.6) < 1e-9 and abs(t30 - 230.57) < 0.01))
    best = next(c for c in range(20, 61) if L.temperature_for_liquid_fraction(float(c), 0.6) <= 230.0)
    checks.append((f"design: smallest whole wt% Sn that is 60 percent liquid at or below 230 C is {best}", best == 31))
    checks.append(("edge: 50 wt% Sn is already 72 percent liquid just above 183 C, so 60 percent is only reached at the 183 C arrest",
                   abs(L.liquid_fraction_eq(50.0, 183.0 + 1e-7) - 0.7209) < 1e-3 and L.temperature_for_liquid_fraction(50.0, 0.6) == L.T_E))
    checks.append(("30 wt% Sn: eutectic fraction 25.6 percent in equilibrium and 35.1 percent with Scheil freezing",
                   round(100 * L.eutectic_mixture_fraction(30.0), 1) == 25.6 and round(100 * L.scheil_eutectic_fraction(30.0), 1) == 35.1))
    t31 = L.temperature_for_liquid_fraction(31.0, 0.6)
    checks.append((f"design: 31 wt% Sn is 60 percent liquid at {t31:.1f} C", round(t31, 1) == 227.4))
    ap = L.alpha_prime(L.back_diffusion_alpha(L.freezing_time(10.0, 10 ** 0.7)))
    checks.append(("app challenge: 10 wt% Sn at q = 10^0.7 W/g makes at least 5 percent eutectic",
                   L.clyne_kurz_eutectic_fraction(10.0, ap) >= 0.05))
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
