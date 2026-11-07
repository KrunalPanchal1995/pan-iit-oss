"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # --- search -------------------------------------------------------------
    tight = L.search_trains(20, 0.01, inline=True)
    best = tight[np.argmin(tight.sum(axis=1))]
    checks.append(("worked example: 19 in-line designs lie within 1 percent of 1:20 (17 to 90 teeth)", len(tight) == 19))
    checks.append(("worked example: the fewest-teeth in-line design is 17-76 then 17-76 with ratio 19.986",
                   list(best) == [17, 76, 17, 76] and abs(L.train_ratio(best) - 19.986) < 1e-3))
    checks.append(("worked example: both stages have N + N = 93, so centre distances are equal",
                   best[0] + best[1] == 93 and best[2] + best[3] == 93))
    checks.append(("no exact in-line 1:20 design exists with 17 to 90 teeth", len(L.search_trains(20, 0.0, inline=True)) == 0))
    checks.append(("without the in-line limit 467 designs lie within 1 percent", len(L.search_trains(20, 0.01, inline=False)) == 467))
    ratios = np.array([L.train_ratio(r) for r in tight])
    checks.append(("every design found respects the tolerance and the 17 tooth minimum",
                   np.all(np.abs(ratios / 20 - 1) <= 0.01) and tight.min() >= 17))
    checks.append(("edge case: an impossible target returns an empty list", len(L.search_trains(2000, 0.001)) == 0))
    # --- losses -------------------------------------------------------------
    checks.append(("6 meshes at 0.98 keep 0.8858 of the power", abs(L.train_efficiency(6) - 0.8858) < 1e-4))
    checks.append(("2 meshes keep 0.9604 and 4 meshes keep 0.9224",
                   abs(L.train_efficiency(2) - 0.9604) < 1e-4 and abs(L.train_efficiency(4) - 0.9224) < 1e-4))
    p_out, p_loss = L.power_balance(100.0, 6)
    checks.append(("power in = power out + loss: 100 W gives 88.58 W and 11.42 W",
                   abs(p_out - 88.58) < 0.01 and abs(p_loss - 11.42) < 0.01 and abs(p_out + p_loss - 100.0) < 1e-12))
    # --- inertia and simulation ------------------------------------------
    j_one = L.reflected_inertia([1e-4, 9e-3], [(20, 60)])
    checks.append(("J_eff = J1 + J2 (N1/N2)^2 for one stage: 1e-4 + 9e-3/9 = 1.1e-3", abs(j_one - 1.1e-3) < 1e-12))
    stages = [(17, 76), (17, 76)]
    J = [1.0e-4, 2.0e-4, 0.05]
    jeff = L.reflected_inertia(J, stages)
    hand = 1.0e-4 + 2.0e-4 * (17 / 76) ** 2 + 0.05 * (17 / 76) ** 4
    checks.append(("worked example: two-stage J_eff = 2.352e-4 kg m^2, equal to the hand formula",
                   abs(jeff - hand) < 1e-12 and abs(jeff - 2.352e-4) < 1e-7))
    stiff = L.simulate_train(stages, J, 100.0, 0.05, 0.0, 0.2, 0.05, 0.3)
    w_ideal = 0.2 * 0.05 / jeff
    checks.append(("worked example: after the 0.2 N m, 0.05 s pulse the input turns at 42.5 rad/s (impulse / J_eff)",
                   abs(w_ideal - 42.52) < 0.01 and abs(stiff["w"][-1, 0] - w_ideal) / w_ideal < 2e-3))
    checks.append(("with no backlash all three shafts end at the same referred speed",
                   np.ptp(stiff["w"][-1]) / stiff["w"][-1, 0] < 1e-3))
    rho = L.shaft_ratios(stages)
    out_rpm = stiff["w"][-1, 2] * rho[2] * 60 / (2 * np.pi)
    checks.append(("worked example: the output shaft turns at 20.3 rpm (about 406 rpm / 20)", abs(out_rpm - 20.3) < 0.1))
    back = L.simulate_train(stages, J, 100.0, 0.05, 0.02, 0.2, 0.05, 0.3)
    for name, r in (("no backlash", stiff), ("backlash", back)):
        checks.append((f"momentum grows by exactly the torque impulse ({name})", abs(r["momentum"][-1] - 0.01) / 0.01 < 2e-3))
        resid = abs(r["work"][-1] - (r["kinetic"][-1] + r["spring"][-1] + r["diss"][-1])) / r["work"][-1]
        checks.append((f"energy in = kinetic + spring + lost ({name})", resid < 1e-3))
    checks.append(("backlash makes the peak mesh torque larger (0.172 to 0.447 N m)",
                   back["peak_torque"] > 2 * stiff["peak_torque"] and abs(stiff["peak_torque"] - 0.172) < 5e-3
                   and abs(back["peak_torque"] - 0.447) < 5e-3))
    peaks = {b: L.simulate_train(stages, J, 100.0, 0.05, b, 0.2, 0.05, 0.3)["peak_torque"] for b in (0.01, 0.04)}
    checks.append(("peak mesh torque grows with backlash: 0.172, 0.345, 0.447, 0.588 N m for 0, 0.01, 0.02, 0.04 rad",
                   abs(peaks[0.01] - 0.345) < 5e-3 and abs(peaks[0.04] - 0.588) < 5e-3
                   and stiff["peak_torque"] < peaks[0.01] < back["peak_torque"] < peaks[0.04]))
    checks.append(("with backlash the load starts later than the input",
                   np.argmax(back["w"][:, 2] > 1.0) > np.argmax(back["w"][:, 0] > 1.0)))
    # --- planetary --------------------------------------------------------
    checks.append(("planetary, ring fixed, Ns = 20, Nr = 60: ratio 1 + Nr/Ns = 4", L.planetary_ratio_fixed_ring(20, 60) == 4.0))
    ok = True
    for ws, wr in ((100.0, 0.0), (100.0, 30.0), (-40.0, 25.0), (0.0, 50.0)):
        wc, wp = L.planet_kinematics(ws, wr, 20, 60)
        ok &= abs(wc - L.willis_carrier(ws, wr, 20, 60)) < 1e-9
        ok &= abs(ws * 20 + wr * 60 - wc * 80) < 1e-9
    checks.append(("the Willis relation matches the contact-point velocity solution", ok))
    wc, _ = L.planet_kinematics(100.0, 0.0, 20, 60)
    checks.append(("hand calculation: sun 100 rpm, ring fixed gives carrier 25 rpm", abs(wc - 25.0) < 1e-9))
    checks.append(("carrier fixed: the ring turns the other way at Ns/Nr of the sun speed",
                   abs(L.willis_carrier(100.0, -100.0 * 20 / 60, 20, 60)) < 1e-9))
    checks.append(("planets: 20 teeth fit and 4 planets space evenly, 3 do not",
                   L.planets_fit(20, 60, 4) and not L.planets_fit(20, 60, 3) and not L.planets_fit(20, 61, 4)))
    checks.append(("4 meshes at 0.98: 500 W in gives 461.2 W out and 38.8 W lost",
                   abs(L.power_balance(500.0, 4)[0] - 461.2) < 0.05 and abs(L.power_balance(500.0, 4)[1] - 38.8) < 0.05))
    checks.append(("planetary Ns = 24, Nr = 72, ring fixed: planets have 24 teeth, ratio 4, carrier 225 rpm at 900 rpm",
                   (72 - 24) // 2 == 24 and L.planetary_ratio_fixed_ring(24, 72) == 4.0
                   and abs(L.willis_carrier(900.0, 0.0, 24, 72) - 225.0) < 1e-9))
    t16 = L.search_trains(16, 0.01)
    b16 = t16[np.argmin(t16.sum(axis=1))]
    checks.append(("design problem: 46 in-line designs within 1 percent of 1:16; the smallest is 17-68-17-68, exactly 16",
                   len(t16) == 46 and list(b16) == [17, 68, 17, 68] and L.train_ratio(b16) == 16.0
                   and L.check_design(list(b16), 2.0, 16, 0.01) == []))
    # --- failure cases -----------------------------------------------------
    checks.append(("17-76-17-76 at module 2 passes every check",
                   L.check_design([17, 76, 17, 76], 2.0, 20, 0.01) == []))
    ideal_stage = 17 * np.sqrt(20)
    checks.append(("an equal-ratio split needs 76.03 teeth: not a whole number",
                   abs(ideal_stage - 76.03) < 0.01 and "not a whole number" in " ".join(L.check_design([17, ideal_stage, 17, ideal_stage], 2.0, 20, 0.01))))
    checks.append(("a 15-tooth pinion is flagged as undercut",
                   any("undercut" in s for s in L.check_design([15, 76, 17, 76], 2.0, 20, 0.5))))
    msg = " ".join(L.check_design([17, 68, 17, 85], 2.0, 20, 0.01))
    checks.append(("the smallest design of Session 2 fails: centre distances 85 mm and 102 mm", "85 mm and 102 mm" in msg))
    checks.append(("a too-small box is flagged (93 mm needed, 80 mm allowed)",
                   any("93 mm" in s for s in L.check_design([17, 76, 17, 76], 2.0, 20, 0.01, a_max_mm=80.0))))
    # --- winch ---------------------------------------------------------------
    w = L.WINCH
    checks.append(("winch: load torque 58.86 N m at the drum and 392.4 N at a 1:1 crank of 0.15 m",
                   abs(w["mass"] * w["g"] * w["r_drum"] - 58.86) < 1e-9 and abs(L.crank_force(1, 0) - 392.4) < 1e-9))
    checks.append(("winch: the best single stage (17 and 63 teeth) needs 108.0 N, more than 100 N",
                   abs(L.crank_force(63 / 17, 1) - 108.05) < 0.01 and len(L.winch_candidates(1)) == 0))
    strict = dict(w, f_max=85.0)
    cands = L.winch_candidates(2, strict)
    tot, st, ratio = cands[0]
    checks.append(("worked example: fewest-teeth winch train has 109 teeth, e.g. 17-34 then 17-41, ratio 4.824",
                   tot == 109 and st == ((17, 34), (17, 41)) and abs(ratio - 4.8235) < 1e-3))
    checks.append(("winch: that train needs 84.7 N and lifts at 0.104 m/s",
                   abs(L.crank_force(ratio, 2) - 84.7) < 0.1 and abs(L.rope_speed(ratio) - 0.104) < 1e-3))
    checks.append(("winch: all designs within the limits have a ratio between 4.81 and 5.03",
                   min(c[2] for c in cands) > 4.80 and max(c[2] for c in cands) < 5.03))
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
