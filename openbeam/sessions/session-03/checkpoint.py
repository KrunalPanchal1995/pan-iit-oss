"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    Ln, E, I = 4.0, 200e9, 8.0e-6
    EI = E * I
    P, q = 10e3, 5e3
    r = L.solve_beam(Ln, 2, EI, points=[(Ln / 2, P)])
    checks.append((f"worked example: centre load, 2 elements gives 8.333 mm (got {r['w'][1] * 1e3:.4f})",
                   abs(r["w"][1] - 8.3333e-3) < 1e-7 and abs(r["w"][1] - P * Ln ** 3 / (48 * EI)) < 1e-12))
    r = L.solve_beam(Ln, 8, EI, q=q)
    checks.append((f"worked example: uniform load gives 5 q L^4/(384 E I) = 10.417 mm (got {r['w'][4] * 1e3:.4f})",
                   abs(r["w"][4] - 10.4167e-3) < 1e-7))
    r = L.solve_beam(Ln, 16, EI, points=[(1.3, P)])
    checks.append(("off-node point load matches the exact curve at every node",
                   np.abs(r["w"] - L.exact_point(r["x"], P, 1.3, Ln, EI)).max() < 1e-9))
    rc = L.solve_beam(Ln, 8, EI, points=[(Ln, P)], support="cantilever")
    checks.append(("cantilever tip load matches P L^3 / (3 E I)", abs(rc["w"][-1] - P * Ln ** 3 / (3 * EI)) < 1e-9))
    checks.append(("supports of the simple beam do not deflect", r["w"][0] == 0 and r["w"][-1] == 0))
    # statics: shear next to the support equals the reaction, moment average at centre
    rs = L.solve_beam(Ln, 4, EI, points=[(Ln / 2, P)])
    checks.append(("shear next to the support equals the reaction P/2", abs(rs["V"][0] - P / 2) < 1e-6 and abs(rs["V"][-1] + P / 2) < 1e-6))
    ru = L.solve_beam(Ln, 4, EI, q=q)
    checks.append(("uniform load: shear next to the support is q L / 2", abs(ru["V"][0] - q * Ln / 4 * 1.0) < q * Ln / 2 * 0.51 and abs(ru["V"][0] - 7.5e3) < 1e-6))
    rows = L.convergence_table(Ln, EI, q)
    ratio = rows[2][2] / rows[3][2]
    checks.append((f"moment error falls about 4 times when the mesh is halved (got {ratio:.2f})", 3.8 < ratio < 4.2))
    checks.append(("moment error shrinks at every refinement", all(rows[i][2] > rows[i + 1][2] for i in range(len(rows) - 1))))
    EIt = L.tapered_EI(E, 0.05, 0.12, 0.06, Ln)
    ref = L.solve_beam(Ln, 512, EIt, points=[(Ln, P)], support="cantilever")["w"][-1]
    errs = [abs(L.solve_beam(Ln, n, EIt, points=[(Ln, P)], support="cantilever")["w"][-1] - ref) / ref for n in (4, 8, 16)]
    checks.append(("tapered beam: error falls by about 4 at each halving", 3.5 < errs[0] / errs[1] < 4.5 and 3.5 < errs[1] / errs[2] < 4.5))
    f_E = lambda e: L.solve_beam(Ln, 8, e * I, points=[(Ln / 2, P)])["w"][4]
    f_h = lambda h: L.solve_beam(Ln, 8, E * 0.05 * h ** 3 / 12, points=[(Ln / 2, P)])["w"][4]
    checks.append(("sensitivity: deflection ~ 1/E (slope -1)", abs(L.sensitivity_slope(f_E, E) + 1) < 1e-3))
    checks.append(("sensitivity: deflection ~ 1/h^3 (slope -3)", abs(L.sensitivity_slope(f_h, 0.2) + 3) < 1e-3))
    checks.append(("limit of theory: shear adds 3.1% at L/h = 10 and 78% at L/h = 2",
                   abs(L.shear_deflection_ratio(10) - 0.0311) < 1e-4 and abs(L.shear_deflection_ratio(2) - 0.78) < 1e-3))
    # hand calculation for the mini-project baseline: M = w L^2 / 8 + P L / 4
    sec = (0.15, 0.01, 0.006, 0.19)
    A, I2 = L.isection_props(*sec)
    wtot = 3500.0 + L.RHO * L.G_ACC * A
    r190 = L.check_footbridge(6.0, 3500.0, 5000.0, 200e9, 250e6, 1.5, sec)
    hand_M = wtot * 36 / 8 + 5000.0 * 6 / 4
    checks.append((f"hand calculation: M = w L^2/8 + P L/4 = {hand_M / 1e3:.2f} kN m (solver {r190['M'] / 1e3:.2f})",
                   abs(r190["M"] - hand_M) / hand_M < 0.002))
    checks.append(("mini-project: the 190 mm section passes both checks", r190["ok"]))
    r180 = L.check_footbridge(6.0, 3500.0, 5000.0, 200e9, 250e6, 1.5, (0.15, 0.01, 0.006, 0.18))
    checks.append(("mini-project: the 180 mm section fails the deflection limit", (not r180["ok_defl"]) and r180["ok_stress"]))
    r_a = L.check_footbridge(6.0, 3500.0, 5000.0, 200e9, 250e6, 1.5, sec, n=120)
    checks.append(("result does not depend on the mesh (120 versus 240 elements)", abs(r_a["w"] - r190["w"]) / r190["w"] < 1e-6))
    # continuous beams: supports at any node, reactions returned
    Lsp = 4.0
    two = L.solve_beam(2 * Lsp, 8, EI, q=q, supports=[(0.0, "pin"), (Lsp, "pin"), (2 * Lsp, "pin")])
    R = [rx[1] for rx in two["reactions"]]
    checks.append((f"two equal spans, uniform load: middle reaction is 1.25 q L = {1.25 * q * Lsp / 1e3:.1f} kN (got {R[1] / 1e3:.3f})",
                   abs(R[1] - 1.25 * q * Lsp) < 0.01 * 1.25 * q * Lsp))
    checks.append(("two equal spans: end reactions are 3 q L / 8 and the three reactions add up to the total load",
                   abs(R[0] - 0.375 * q * Lsp) < 1 and abs(R[2] - 0.375 * q * Lsp) < 1 and abs(sum(R) - q * 2 * Lsp) < 1e-6))
    checks.append(("two equal spans: the beam does not deflect at the middle support", abs(two["w"][4]) == 0.0 and two["w"][2] > 0))
    prop = L.solve_beam(Lsp, 8, EI, q=q, supports=[(0.0, "fixed"), (Lsp, "pin")])
    Rp = [rx[1] for rx in prop["reactions"]]
    checks.append(("propped cantilever: reactions 5 q L / 8 at the wall and 3 q L / 8 at the prop, wall moment q L^2 / 8 (hogging)",
                   abs(Rp[0] - 5 * q * Lsp / 8) < 1 and abs(Rp[1] - 3 * q * Lsp / 8) < 1
                   and abs(abs(prop["reactions"][0][2]) - q * Lsp ** 2 / 8) < 1))
    old = L.solve_beam(Ln, 4, EI, points=[(Ln / 2, P)])
    new = L.solve_beam(Ln, 4, EI, points=[(Ln / 2, P)], supports=[(0.0, "pin"), (Ln, "pin")])
    checks.append(("the supports option with two end pins gives the same beam as support='simple'",
                   np.abs(old["w"] - new["w"]).max() < 1e-15 and abs(old["reactions"][0][1] - P / 2) < 1e-6))
    try:
        L.solve_beam(2 * Lsp, 8, EI, q=q, supports=[(0.0, "pin"), (3.3, "pin"), (2 * Lsp, "pin")])
        off_node = False
    except ValueError:
        off_node = True
    checks.append(("a support that is not on a node is refused with a clear error", off_node))
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
