"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    Lsp, P, d = 12.0, 10e3, 3.0
    grp = L.make_group([P, P], [d])

    # ---- worked example: two axles 2 x 10 kN, 3 m apart, 12 m span ------------------------------
    hand = P * (Lsp - d / 2) ** 2 / (2 * Lsp)
    checks.append((f"hand value: M = P (L - d/2)^2 / (2 L) = {hand / 1e3:.2f} kN m (45.9)", abs(hand - 45.9375e3) < 1.0 and abs(hand / 1e3 - 45.9) < 0.1))
    env = L.envelope(grp, Lsp)
    checks.append((f"roadmap checkpoint: the peak of the moment envelope is {env['peak_M'] / 1e3:.2f} kN m, within 1% of the hand value 45.9 kN m",
                   abs(env["peak_M"] / 1e3 - 45.9) / 45.9 < 0.01))
    checks.append((f"the peak is under an axle at x = {env['x_peak']:.2f} m (or its mirror image), L/2 - d/4 = 5.25 m, with the rear axle at 5.25 m",
                   min(abs(env["x_peak"] - 5.25), abs(env["x_peak"] - 6.75)) < 0.06))
    r = L.reactions(grp, 5.25, Lsp)
    checks.append((f"at that position R_A = {r[0] / 1e3:.3f} kN and R_B = {r[1] / 1e3:.3f} kN (8.75 and 11.25), and they add up to the 20 kN on the beam",
                   abs(r[0] - 8.75e3) < 1e-6 and abs(r[1] - 11.25e3) < 1e-6 and abs(sum(r) - 2 * P) < 1e-9))
    checks.append(("moment at that position under the rear axle: R_A x 5.25 = 45.94 kN m", abs(L.moment(5.25, grp, 5.25, Lsp) - 8.75e3 * 5.25) < 1e-6))
    checks.append(("naive values for comparison: both axles at mid-span 60 kN m and one axle 30 kN m bracket the true 45.9 kN m",
                   30e3 < env["peak_M"] < 60e3))

    # ---- statics ---------------------------------------------------------------------------------
    one = L.make_group([P], [])
    a, b = 4.0, Lsp - 4.0
    checks.append(("one load: reactions P b / L and P a / L and the moment P a b / L of Session 1",
                   np.allclose(L.reactions(one, a, Lsp), [P * b / Lsp, P * a / Lsp]) and abs(L.moment(a, one, a, Lsp) - P * a * b / Lsp) < 1e-9))
    ok_eq = True
    for s in (-1.0, 0.0, 1.7, 5.0, 9.5, 10.9):
        ra, rb = L.reactions(grp, s, Lsp)
        on_span = sum(pp for o, pp in grp if 0.0 <= s + o <= Lsp)
        ok_eq &= abs(ra + rb - on_span) < 1e-9 and abs(L.moment(0.0, grp, s, Lsp)) < 1e-9 and abs(L.moment(Lsp, grp, s, Lsp)) < 1e-6
    checks.append(("for any position: R_A + R_B equals the load on the span, and the moment is zero at both supports", ok_eq))
    checks.append(("an axle off the span carries nothing into the beam: with the rear axle at -1 m only the front axle (at 2 m) counts, R_A = 8.33 kN",
                   abs(L.reactions(grp, -1.0, Lsp)[0] - P * 10.0 / 12.0) < 1e-9))

    # ---- influence lines: the independent route --------------------------------------------------
    rng = np.random.default_rng(4)
    ok_inf = True
    g3 = L.make_group([20e3, 80e3, 80e3], [4.0, 5.0])
    for _ in range(200):
        x = rng.uniform(0.0, 20.0)
        s = rng.uniform(-9.0, 20.0)
        ok_inf &= abs(L.moment(x, g3, s, 20.0) - L.moment_by_influence(x, g3, s, 20.0)) < 1e-6
        ok_inf &= abs(L.shear(x, g3, s, 20.0) - L.shear_by_influence(x, g3, s, 20.0)) < 1e-6
    checks.append(("200 random sections and positions of a 3-axle group: statics and influence lines agree on moment and shear", ok_inf))
    checks.append(("influence line of moment at mid-span: a unit load at mid-span gives L/4, at the support 0",
                   abs(float(L.influence_moment(6.0, 6.0, 12.0)) - 3.0) < 1e-12 and abs(float(L.influence_moment(6.0, 0.0, 12.0))) < 1e-12))

    # ---- envelope properties ---------------------------------------------------------------------
    ok_env = True
    for s in np.linspace(-3, 12, 31):
        ok_env &= all(L.moment(x, grp, s, Lsp) <= e + 1e-6 for x, e in zip(env["x"][::12], env["M_max"][::12]))
    checks.append(("no snapshot of the moving group goes outside the envelope", ok_env))
    checks.append(("the envelope is zero at both supports and symmetric about mid-span for this symmetric group",
                   abs(env["M_max"][0]) < 1e-6 and abs(env["M_max"][-1]) < 1e-6 and np.allclose(env["M_max"], env["M_max"][::-1], atol=5.0)))
    checks.append((f"largest shear is at the supports, 17.5 kN = P (2L - d)/L (got {env['V_max'][0] / 1e3:.2f} kN and {-env['V_min'][-1] / 1e3:.2f} kN)",
                   abs(env["V_max"][0] - 17.5e3) < 30.0 and abs(-env["V_min"][-1] - 17.5e3) < 30.0 and abs(L.support_shear_peak(grp, Lsp) - 17.5e3) < 1.0))

    # ---- worst position by hand against the sweep ------------------------------------------------
    for name, gp, Lg in (("two equal axles", grp, 12.0), ("three axles 20, 80, 80 kN (4 m, 5 m apart) on 20 m", g3, 20.0),
                         ("unequal two axles 30 and 70 kN, 2.5 m apart, on 9 m", L.make_group([30e3, 70e3], [2.5]), 9.0)):
        hm = L.worst_moment_by_hand(gp, Lg)[0]
        sw = L.envelope(gp, Lg, nx=401, ds=0.005)["peak_M"]
        checks.append((f"{name}: equal-distance rule {hm / 1e3:.2f} kN m against sweep {sw / 1e3:.2f} kN m (within 0.1%)", abs(hm - sw) / sw < 1e-3))
    # spacing study: the two-axle formula and its crossover with one axle at mid-span
    d_cross = 2 * Lsp * (1 - 1 / math.sqrt(2))
    sp_ok = True
    for dd in (1.0, 3.0, 5.0, 7.0, 8.0, 10.0, 13.0):
        pk = L.envelope(L.make_group([P, P], [dd]), Lsp, nx=241, ds=0.01)["peak_M"]
        sp_ok &= abs(pk - L.two_axle_peak(P, dd, Lsp)) / pk < 2e-3
    checks.append((f"two-axle hand formula holds for spacings 1 to 13 m, and beyond d = {d_cross:.2f} m (0.586 L) one axle at mid-span, P L / 4 = 30 kN m, governs", sp_ok))
    far = L.envelope(L.make_group([P, P], [14.0]), Lsp)
    checks.append(("axles farther apart than the span never share it: the peak is P L / 4 and the largest shear is P", abs(far["peak_M"] - P * Lsp / 4) < 1.0 and abs(far["V_max"][0] - P) < 30.0))
    # a group that is not symmetric needs both directions
    uns = L.make_group([30e3, 70e3], [2.5])
    e_one = L.envelope(uns, 9.0, both_directions=False)
    e_two = L.envelope(uns, 9.0, both_directions=True)
    checks.append(("an unequal group crossing one way gives a lopsided envelope; both directions make it symmetric and larger or equal",
                   not np.allclose(e_one["M_max"], e_one["M_max"][::-1], atol=5.0) and np.allclose(e_two["M_max"], e_two["M_max"][::-1], atol=5.0) and e_two["peak_M"] >= e_one["peak_M"] - 1e-6))

    # ---- girder: stress and deflection ------------------------------------------------------------
    A, I = L.isection_props(0.15, 0.010, 0.006, 0.37)
    checks.append((f"I-section 150 x 10 flanges, 6 mm web, 370 mm deep: A = {A * 1e4:.1f} cm^2, I = {I * 1e8:.0f} cm^4 (51.0 and 11 866 by hand: b h^3/12 - (b - t_w)(h - 2 t_f)^3/12)",
                   abs(A * 1e4 - 51.0) < 0.05 and abs(I * 1e8 - 11866) < 5))
    EI = 200e9 * 8.0e-6
    checks.append(("mid-span deflection of one load at mid-span is P L^3 / (48 E I)",
                   abs(L.midspan_deflection(L.make_group([P], []), 6.0, 12.0, EI) - P * 12.0 ** 3 / (48 * EI)) < 1e-12))
    dsym = 2 * P * ((Lsp - d) / 2) * (3 * Lsp ** 2 - 4 * ((Lsp - d) / 2) ** 2) / (48 * EI)
    checks.append((f"two axles placed symmetrically about mid-span give the largest mid-span deflection {dsym * 1e3:.3f} mm (the sweep agrees)",
                   abs(L.max_midspan_deflection(grp, Lsp, EI) - dsym) / dsym < 1e-4))
    depths = np.arange(0.15, 0.801, 0.01)
    kw = dict(deck_w=3000.0, fos=1.5)
    h_env, r_env = L.lightest_depth(grp, Lsp, 0.15, 0.010, 0.006, depths, **kw)
    h_both, r_both = L.lightest_depth(grp, Lsp, 0.15, 0.010, 0.006, depths, fixed_moment=2 * P * Lsp / 4, **kw)
    h_one, r_one = L.lightest_depth(grp, Lsp, 0.15, 0.010, 0.006, depths, fixed_moment=P * Lsp / 4, **kw)
    checks.append((f"mini-project: lightest passing depth {1e3 * h_env:.0f} mm ({r_env['mass']:.1f} kg/m); designing for both axles at mid-span gives {1e3 * h_both:.0f} mm ({r_both['mass']:.1f} kg/m), too heavy",
                   abs(h_env - 0.37) < 1e-9 and abs(h_both - 0.41) < 1e-9 and h_both > h_env and abs(r_env["mass"] - 40.0) < 0.1))
    bad = L.check_girder(grp, Lsp, (0.15, 0.010, 0.006, h_one), **kw)
    checks.append((f"designing for one axle gives {1e3 * h_one:.0f} mm, which fails the true envelope check (stress {bad['sigma'] / 1e6:.1f} MPa x 1.5 > 250)",
                   abs(h_one - 0.35) < 1e-9 and (not bad["ok_stress"]) and bad["ok_defl"]))
    checks.append(("the stress limit governs the 370 mm answer: the 360 mm section fails on stress and passes on deflection",
                   (lambda r: (not r["ok_stress"]) and r["ok_defl"])(L.check_girder(grp, Lsp, (0.15, 0.010, 0.006, 0.36), **kw))))

    # ---- edge cases -----------------------------------------------------------------------------
    errs = 0
    for args in (([], []), ([1.0, 2.0], []), ([1.0, -2.0], [1.0]), ([1.0, 2.0], [0.0])):
        try:
            L.make_group(*args)
        except ValueError:
            errs += 1
    checks.append(("an empty group, a missing or zero spacing and a negative load are refused", errs == 4))
    checks.append(("a vehicle that has left the span (rear axle at 30 m) gives zero reactions and zero moment",
                   L.reactions(grp, 30.0, Lsp) == (0.0, 0.0) and L.moment(6.0, grp, 30.0, Lsp) == 0.0))
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
