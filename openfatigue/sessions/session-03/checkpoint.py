"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- rainflow: hand-traced test sequence and known cases
    seq = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
    got = sorted((float(r), float(c)) for r, m, c in L.rainflow(seq))
    want = sorted([(3.0, 0.5), (4.0, 0.5), (4.0, 1.0), (8.0, 0.5), (9.0, 0.5), (8.0, 0.5), (6.0, 0.5)])
    checks.append(("rainflow of -2,1,-3,5,-1,3,-4,4,-2 gives one full cycle of range 4 and half cycles 3, 4, 8, 9, 8, 6", got == want))
    t = np.arange(0, 401)
    sine = 100.0 * np.cos(2 * np.pi * t / 40.0)           # exactly 10 full cycles, range 200
    cyc = L.rainflow(sine)
    checks.append(("constant-amplitude sine with 10 cycles gives 10 full cycles of range 200",
                   abs(sum(c for r, m, c in cyc) - 10.0) < 1e-9 and all(abs(r - 200.0) < 1e-6 for r, m, c in cyc)))
    checks.append(("a single rise 0 to 5 is one half cycle of range 5", [(float(r), c) for r, m, c in L.rainflow([0, 1, 3, 5])] == [(5.0, 0.5)]))
    rng = np.random.default_rng(3)
    walk = np.cumsum(rng.normal(size=300))
    rev = L.reversals(walk)
    cyc = L.rainflow(walk)
    total = float(np.abs(np.diff(rev)).sum())
    checks.append(("invariant: sum of 2 * count * range equals the total travel of the history (random walk)",
                   abs(sum(2 * c * r for r, m, c in cyc) - total) < 1e-9))
    checks.append(("edge: a constant history has no cycles", L.rainflow([3.0, 3.0, 3.0]) == []))

    # --- Miner
    n400, n350 = L.cycle_life(400), L.cycle_life(350)
    d1, d2 = 1e4 / n400, 5e4 / n350
    checks.append((f"worked example: 10,000 cycles at 400 MPa use 0.294 and 50,000 at 350 MPa use 0.306 (got {d1:.3f}, {d2:.3f}); sum 0.600",
                   abs(d1 - 0.294) < 5e-4 and abs(d2 - 0.306) < 5e-4 and abs(d1 + d2 - 0.600) < 5e-4))
    checks.append(("worked example: the remaining 0.400 allows about 13,600 more cycles at 400 MPa", abs(0.4 * n400 - 13607) < 5))
    half = [(800.0, 0.0, n400 / 2), (700.0, 0.0, n350 / 2)]
    checks.append(("Miner: half the life at each of two levels sums to D = 1", abs(L.miner_damage(half) - 1.0) < 1e-9))
    checks.append(("Miner: a full-life block of one level gives D = 1", abs(L.miner_damage([(800.0, 0.0, n400)]) - 1.0) < 1e-9))
    checks.append(("a tensile mean stress adds damage", L.cycle_life(250, 100) < L.cycle_life(250, 0)))
    checks.append(("below S_e: extend mode gives finite life, ignore mode gives infinite", np.isfinite(L.cycle_life(250)) and L.cycle_life(250, 0, "ignore") == np.inf))
    checks.append(("edge: mean at S_u gives a life of 1 cycle (no division by zero)", L.cycle_life(10, 600.0) == 1.0))

    # --- Paris' law
    a0, dsig = 1e-3, 100.0
    ac = L.critical_crack(dsig)
    dk0 = L.delta_k(dsig, a0)
    checks.append((f"worked example: delta_K at a0 = 1 mm is 6.28 MPa sqrt(m) (got {dk0:.2f}) and a_c = 63.4 mm (got {ac * 1000:.1f})",
                   abs(dk0 - 6.28) < 0.01 and abs(ac * 1000 - 63.4) < 0.05))
    ncf = L.paris_closed_form(a0, ac, dsig)
    nnum = L.paris_numeric(a0, ac, dsig)
    checks.append((f"worked example: closed form {ncf:,.0f} cycles from 1 mm to 63.4 mm (about 1.02 million); numeric agrees",
                   abs(ncf - 1024557) < 5 and abs(nnum / ncf - 1) < 1e-6))
    errs = []
    for m in (2.5, 3.0, 4.0):
        for a_0 in (0.5e-3, 2e-3):
            errs.append(abs(L.paris_numeric(a_0, 0.02, 150.0, m=m, c=1e-12) / L.paris_closed_form(a_0, 0.02, 150.0, m=m, c=1e-12) - 1))
    checks.append(("numeric integral matches the closed form for m = 2.5, 3, 4 (relative error below 1e-6)", max(errs) < 1e-6))
    m2 = L.paris_numeric(a0, 0.02, 100.0, m=2.0)
    ln_form = np.log(0.02 / a0) / (L.C_PARIS * L.Y_EDGE ** 2 * 100.0 ** 2 * np.pi)
    checks.append(("edge: m = 2 (closed form undefined) still integrates and matches the logarithmic formula", abs(m2 / ln_form - 1) < 1e-6))
    checks.append(("Y given as a function of a gives the same answer when it is constant", abs(L.paris_numeric(a0, ac, dsig, y=lambda a: np.full_like(a, 1.12)) / nnum - 1) < 1e-12))
    cy, aa = L.paris_curve(a0, ac, dsig)
    checks.append(("crack curve starts at 0 cycles and a0, ends at the closed-form life and a_c, and accelerates",
                   cy[0] == 0 and abs(cy[-1] / ncf - 1) < 1e-4 and abs(aa[-1] - ac) < 1e-12 and np.all(np.diff(cy) > 0)))
    r_same = L.paris_closed_form(a0, ac, 110.0) / ncf
    r_paris = L.paris_closed_form(a0, L.critical_crack(110.0), 110.0) / ncf
    checks.append((f"Paris: 10 percent more stress range cuts life to 1.1^-3 = 0.751 at the same a_c (got {r_same:.3f}), a cut of 25 percent; with the smaller a_c it is {r_paris:.3f}",
                   abs(r_same - 1.1 ** -3) < 1e-9 and abs(r_paris - 0.741) < 0.002))

    # --- scatter and sensitivity
    l1, l2 = L.lognormal_lives(1e5), L.lognormal_lives(1e5)
    checks.append(("seeded Monte Carlo is repeatable", bool(np.array_equal(l1, l2))))
    p1, p5, p95 = np.percentile(l1, [1, 5, 95])
    checks.append((f"median of 10,000 simulated lives is within 3% of 100,000 (got {np.median(l1):,.0f})", abs(np.median(l1) / 1e5 - 1) < 0.03))
    checks.append((f"5th to 95th percentile ratio is about 10 (got {p95 / p5:.1f}); theory 10^(2*1.645*0.3) = 9.7", abs(p95 / p5 - 9.7) < 0.7))
    checks.append((f"the 1st percentile life is about 0.2 of the median (got {p1 / 1e5:.2f})", abs(p1 / 1e5 - 0.2) < 0.02))
    r = L.life_ratio_for_stress_change(1.1)
    checks.append((f"S-N: 10 percent more stress multiplies life by 1.1^(1/b) = 0.326 (got {r:.3f}), a cut of 67 percent; note 1.1^b would be 0.992 (wrong)",
                   abs(r - 0.326) < 0.001 and abs(1.1 ** L.B - 0.992) < 0.001))

    # --- bracket
    s = L.bracket_history()
    cyc = L.rainflow(s)
    total_cycles = sum(c for r_, m_, c in cyc)
    d = L.miner_damage(cyc)
    checks.append((f"bracket: stress ranges from -120 to 450 MPa (got {s.min():.0f} to {s.max():.0f}); {total_cycles:.1f} cycles counted per shift",
                   abs(s.min() + 120) < 1 and abs(s.max() - 450) < 1 and abs(total_cycles - 920.5) < 1e-9))
    checks.append((f"bracket: damage per shift 2.0e-4, life about 5,000 shifts (got {d:.3e}, {1 / d:,.0f})", abs(d - 2.001e-4) < 1e-6 and abs(1 / d - 4998) < 5))
    d_ign = L.miner_damage(cyc, "ignore")
    checks.append((f"bracket: ignoring cycles below S_e gives about 5,050 shifts (got {1 / d_ign:,.0f}); the small cycles hardly matter", abs(1 / d_ign - 5046) < 5))
    share = L.damage_share_above(cyc, 250)
    n_big = sum(c for r_, m_, c in cyc if r_ / 2 > 250)
    checks.append((f"failure case: {n_big} of {total_cycles:.1f} cycles (about 1 percent) above 250 MPa carry {share:.1%} of the damage", n_big == 9.5 and abs(share - 0.967) < 0.001))
    life0 = 1 / L.miner_damage(L.rainflow(L.bracket_history(n_knocks=0)))
    checks.append((f"failure case: without the 6 hard knocks the life is 56,600 shifts, 11 times longer (got {life0:,.0f}, {life0 * d:.1f})", abs(life0 - 56607) < 10 and abs(life0 * d - 11.3) < 0.1))
    dsig_eq = L.equivalent_range(cyc)
    ac_b = L.critical_crack(s.max())
    iv = L.inspection_interval_shifts(s)
    checks.append((f"inspection: equivalent range {dsig_eq:.1f} MPa, a_c = {ac_b * 1000:.2f} mm, interval {iv:.1f} shifts (use 250)",
                   abs(dsig_eq - 112.6) < 0.1 and abs(ac_b * 1000 - 3.13) < 0.01 and abs(iv - 252.1) < 0.2))
    passing = [k for k in range(0, 15) if 1 / L.miner_damage(L.rainflow(L.bracket_history(n_knocks=k))) >= 4000]
    l8 = 1 / L.miner_damage(L.rainflow(L.bracket_history(n_knocks=8)))
    l12 = 1 / L.miner_damage(L.rainflow(L.bracket_history(n_knocks=12)))
    checks.append((f"mini-project: for a 4,000 shift requirement the most knocks per shift allowed is {max(passing)}; 8 knocks give {l8:,.0f}, 12 give {l12:,.0f}",
                   max(passing) == 7 and abs(l8 - 3799) < 5 and abs(l12 - 2781) < 5))
    checks.append(("mini-project: more knocks shorten the inspection interval (475 shifts with none, 174 with 12)",
                   abs(L.inspection_interval_shifts(L.bracket_history(n_knocks=0)) - 475.4) < 0.5 and abs(L.inspection_interval_shifts(L.bracket_history(n_knocks=12)) - 173.7) < 0.5))
    checks.append(("roadmap: the shipped Miner code treats the order of loads as irrelevant (reordered blocks give the same D)",
                   abs(L.miner_damage(half) - L.miner_damage(half[::-1])) < 1e-12))
    # extra numbers used in the text
    ac80 = L.critical_crack(80.0)
    checks.append((f"Section F: edge crack, 80 MPa, a0 = 2 mm: delta_K0 = 7.10, a_c = 99.1 mm, life about 1.39 million cycles (got {L.paris_closed_form(2e-3, ac80, 80.0):,.0f})",
                   abs(L.delta_k(80, 2e-3) - 7.10) < 0.005 and abs(ac80 * 1000 - 99.1) < 0.05 and abs(L.paris_closed_form(2e-3, ac80, 80.0) - 1388293) < 20))
    i05, i1, i2 = (L.inspection_interval_shifts(s, a_detect=a) for a in (0.5e-3, 1e-3, 2e-3))
    checks.append((f"Section F: detectable crack 0.5, 1, 2 mm gives intervals {i05:.0f}, {i1:.0f}, {i2:.0f} shifts", abs(i05 - 252.1) < 0.2 and abs(i1 - 129.1) < 0.2 and abs(i2 - 42.2) < 0.2))
    s7 = L.bracket_history(n_knocks=7)
    l7 = 1 / L.miner_damage(L.rainflow(s7))
    checks.append((f"mini-project: 7 knocks per shift give {l7:,.0f} shifts and an interval of {L.inspection_interval_shifts(s7):.0f} shifts", abs(l7 - 4310) < 5 and abs(L.inspection_interval_shifts(s7) - 233.7) < 0.2))
    checks.append(("app challenge: 60 MPa range, a0 = 2 mm, K_Ic = 50 gives at least 2 million cycles",
                   L.paris_closed_form(2e-3, L.critical_crack(60.0), 60.0) >= 2e6))
    checks.append(("Section F: 5th and 95th percentile lives are about 31,000 and 311,000 cycles; a 0.5 mm crack needs 3 x 252 = 756 shifts to become critical",
                   round(p5 / 1000) == 31 and round(p95 / 1000) == 311 and abs(3 * i05 - 756.3) < 0.5))
    checks.append(("the bracket history has 10 start-ups and 6 knocks (start-ups every 400 steps from step 250)", len(range(250, 4000 - 10, 400)) == 10 and abs(L.bracket_history(n_knocks=6).max() - 450) < 1))
    checks.append(("roadmap: the analytic 99 percent life is 0.2 of the median (10^(-2.326 x 0.3) = 0.2005)", abs(10 ** (-2.326 * 0.3) - 0.2005) < 0.0005))
    checks.append(("roadmap: the shipped K_t = 3 model gives about 326,000 cycles for the plate with nominal amplitude 110 MPa", abs(L.cycle_life(330) - 326247) < 20))
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
