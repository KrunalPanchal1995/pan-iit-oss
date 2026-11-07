"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- stiffness matrix basics
    nodes1 = np.array([[0.0, 0.0], [2.0, 0.0]])
    K1 = L.assemble_k(nodes1, [(0, 1)], 1000.0)
    checks.append(("one horizontal bar is a spring of stiffness EA/L = 500 kN/m", abs(K1[0, 0] - 500.0) < 1e-9 and abs(K1[0, 2] + 500.0) < 1e-9))
    n_p, m_p, s_p, l_p, EA = L.standard_case("pratt")
    K = L.assemble_k(n_p, m_p, EA)
    checks.append(("K is symmetric", np.allclose(K, K.T)))
    checks.append(("moving the whole truss sideways costs no force (K times a rigid shift is zero)",
                   np.allclose(K @ np.tile([1.0, 0.0], len(n_p)), 0.0, atol=1e-8)))

    # --- hand-solved triangle truss (Session 1 geometry), method of joints
    tri = np.array([[0.0, 0.0], [6.0, 0.0], [3.0, 3.0]])
    r = L.solve_truss(tri, [(0, 2), (2, 1), (0, 1)], 80000.0, {0: (1, 1), 1: (0, 1)}, {2: (0.0, -10.0)})
    checks.append(("triangle truss: top bars -7.07 kN and bottom bar +5.00 kN, as by hand",
                   np.allclose(r["forces"], [-7.0711, -7.0711, 5.0], atol=1e-3)))
    checks.append(("triangle truss: reactions are 5 kN up at each foot",
                   abs(r["reactions"][1] - 5.0) < 1e-9 and abs(r["reactions"][3] - 5.0) < 1e-9 and abs(r["reactions"][0]) < 1e-9))
    d_formula = L.triangle_apex_deflection(10.0, 6.0, 3.0, 80000.0)
    checks.append(("triangle truss apex sag by the solver equals the virtual-work formula (0.718 mm)",
                   abs(-r["u"][2, 1] - d_formula) < 1e-12 and abs(d_formula * 1000 - 0.718) < 0.0005))

    # --- Pratt, Howe, Warren under the same 10 kN load
    res = {}
    for kind in ("pratt", "howe", "warren"):
        nodes, members, sup, loads, EA = L.standard_case(kind)
        out = L.solve_truss(nodes, members, EA, sup, loads)
        res[kind] = (nodes, members, sup, loads, EA, out)
    ok_eq = all(np.allclose(L.joint_residuals(v[0], v[1], v[5]["forces"], v[5]["reactions"], v[3]), 0.0, atol=1e-9) for v in res.values())
    checks.append(("equilibrium at every joint (all three trusses): residual below 1e-9 kN", ok_eq))
    checks.append(("reactions add up to the 10 kN load (vertical sum)",
                   all(abs(v[5]["reactions"][1::2].sum() - 10.0) < 1e-9 for v in res.values())))

    nodes, members, sup, loads, EA, out = res["pratt"]
    F = out["forces"]
    checks.append(("Pratt by hand: end posts -7.07, diagonals +7.07, top chord -10.00, bottom chords +5.00 kN",
                   np.allclose(F[[9, 10]], -7.0711, atol=1e-3) and np.allclose(F[[11, 12]], 7.0711, atol=1e-3)
                   and np.allclose(F[[4, 5]], -10.0, atol=1e-9) and np.allclose(F[:4], 5.0, atol=1e-9)))
    checks.append(("Pratt: the three verticals carry zero force under this load", np.allclose(F[6:9], 0.0, atol=1e-9)))
    Fh = res["howe"][5]["forces"]
    checks.append(("Howe: diagonals are in compression (-7.07 kN) and the midspan vertical is in tension (+10 kN)",
                   np.allclose(Fh[[11, 12]], -7.0711, atol=1e-3) and abs(Fh[7] - 10.0) < 1e-9))
    Fw = res["warren"][5]["forces"]
    checks.append(("Warren: sloping bars alternate +-5.59 kN (5 / sin 63.4 degrees) and the middle top chord is -10.00 kN",
                   np.allclose(np.abs(Fw[7:]), 5.5902, atol=1e-3) and abs(Fw[5] + 10.0) < 1e-9))
    counts = {k: len(L.tension_members(v[1], v[5]["forces"])) for k, v in res.items()}
    checks.append(("bars in tension: Pratt 6, Howe 7, Warren 8", counts == {"pratt": 6, "howe": 7, "warren": 8}))
    sag = {k: -v[5]["u"][:, 1].min() * 1000.0 for k, v in res.items()}
    checks.append(("midspan sag (mm): Pratt 1.457, Howe 1.832, Warren 1.386; Warren is stiffest",
                   abs(sag["pratt"] - 1.457) < 0.0005 and abs(sag["howe"] - 1.832) < 0.0005 and abs(sag["warren"] - 1.386) < 0.0005
                   and sag["warren"] < sag["pratt"] < sag["howe"]))

    checks.append(("bars and joints: Pratt 13 and 8, Howe 13 and 8, Warren 15 and 9",
                   [len(res[k][1]) for k in res] == [13, 13, 15] and [len(res[k][0]) for k in res] == [8, 8, 9]))
    checks.append(("extreme forces (kN): Pratt +7.07 / -10.00, Howe +10.00 / -7.07, Warren +7.50 / -10.00",
                   np.allclose([res[k][5]["forces"].max() for k in res], [7.0711, 10.0, 7.5], atol=1e-3)
                   and np.allclose([res[k][5]["forces"].min() for k in res], [-10.0, -7.0711, -10.0], atol=1e-3)))
    checks.append(("worked example: doubling the EA of one bottom bar lowers the Pratt sag from 1.457 to 1.426 mm",
                   abs(-L.solve_truss(nodes, members, np.where(np.arange(len(members)) == 0, 2 * EA, EA), sup, loads)["u"][:, 1].min() * 1000 - 1.426) < 0.0005))
    checks.append(("failure case: the stress-sized bar buckles at under 2 percent of the 10 kN load", L.euler_load_kn(200.0, 10000.0 / 150.0, 2.0) / 10.0 < 0.02))
    checks.append(("footbridge trusses have 21, 21 and 23 bars", [len(L.footbridge_case(k)[1]) for k in ("pratt", "howe", "warren")] == [21, 21, 23]))
    # --- worked example: virtual work on the Pratt truss
    length, _ = L.member_geometry(nodes, members)
    sum_F2L = float(np.sum(F * F * length))
    unit = L.solve_truss(nodes, members, EA, sup, {2: (0.0, -1.0)})["forces"]
    vw = L.virtual_work_deflection(F, unit, length, EA)
    checks.append(("worked example: Pratt midspan sag by virtual work, sum(F^2 L) = 1165.69 kN^2 m, gives 1.457 mm like the solver",
                   abs(sum_F2L - 1165.69) < 0.005 and abs(vw * 1000 - 1.457) < 0.0005 and abs(vw + out["u"][2, 1]) < 1e-12
                   and abs(sum_F2L / 10.0 / EA * 1000 - 1.457) < 0.0005))

    # --- mechanism: a missing bar
    free = L.free_dofs(len(nodes), sup)[0]
    K_ok = L.assemble_k(nodes, members, EA)[np.ix_(free, free)]
    K_bad = L.assemble_k(nodes, members[:11] + members[12:], EA)[np.ix_(free, free)]
    raised = False
    try:
        L.solve_truss(nodes, members[:11] + members[12:], EA, sup, loads)
    except ValueError:
        raised = True
    checks.append(("missing diagonal: K is rank deficient, condition number above 1e12, solver refuses",
                   np.linalg.matrix_rank(K_bad) < len(free) and np.linalg.cond(K_bad) > 1e12 and raised
                   and np.linalg.matrix_rank(K_ok) == len(free) and np.linalg.cond(K_ok) < 1e3))

    # --- sensitivity to member stiffness
    ea2 = np.full(len(members), EA)
    ea2[0] *= 2.0
    o2 = L.solve_truss(nodes, members, ea2, sup, loads)
    checks.append(("determinate truss: doubling one bar's EA leaves every force unchanged but lowers the sag",
                   np.allclose(o2["forces"], F, atol=1e-9) and -o2["u"][:, 1].min() < -out["u"][:, 1].min()))
    o_half = L.solve_truss(nodes, members, EA * 2.0, sup, loads)
    checks.append(("doubling EA in every bar halves the sag", abs(-o_half["u"][:, 1].min() * 2 + out["u"][:, 1].min()) < 1e-12))
    m2 = members + [(1, 6)]
    extra = []
    for fac in (0.5, 1.0, 2.0):
        e = np.full(len(m2), EA)
        e[-1] *= fac
        extra.append(L.solve_truss(nodes, m2, e, sup, loads)["forces"][-1])
    checks.append(("indeterminate (m + r = 17 > 2 j = 16): the extra bar's force depends on its EA: -2.17, -2.80, -3.28 kN",
                   len(m2) + 3 == 17 and 2 * len(nodes) == 16 and np.allclose(extra, [-2.168, -2.803, -3.284], atol=0.0006)))

    # --- failure case: Euler buckling of the top chord, sized on stress only
    area = 10.0 * 1000.0 / 150.0
    d = np.sqrt(4 * area / np.pi)
    I_hand = np.pi * d ** 4 / 64.0                       # mm^4
    pcr_hand = np.pi ** 2 * 200e3 * I_hand / 2000.0 ** 2 / 1000.0   # N/mm^2 * mm^4 / mm^2 -> N -> kN
    pcr = L.euler_load_kn(200.0, area, 2.0)
    checks.append(("failure case: a 66.7 mm^2 round bar (stress-sized for 10 kN, 2 m long) has P_cr = 0.175 kN, far below 10 kN",
                   abs(pcr - pcr_hand) < 1e-9 and abs(pcr - 0.1745) < 0.0005 and pcr < 10.0))
    checks.append(("Euler load falls with the square of length: doubling L divides P_cr by 4",
                   abs(L.euler_load_kn(200.0, 300.0, 4.0) * 4 - L.euler_load_kn(200.0, 300.0, 2.0)) < 1e-12))

    # --- mini-project: 12 m footbridge, 6 kN/m, 150 MPa, 100 mm^2 minimum, sag limit 15 mm
    w, sg, sc = {}, {}, {}
    for kind in ("pratt", "howe", "warren"):
        n, m, s, lo = L.footbridge_case(kind)
        free_sag = L.size_truss(n, m, s, lo)
        lim = L.size_truss(n, m, s, lo, limit_mm=15.0)
        sg[kind] = free_sag["sag_mm"]
        w[kind] = lim["weight_kg"]
        sc[kind] = lim["scaled"]
    checks.append(("mini-project: stress-only designs sag 21.8, 25.4, 22.7 mm (Pratt, Howe, Warren), all above the 15 mm limit",
                   abs(sg["pratt"] - 21.80) < 0.005 and abs(sg["howe"] - 25.40) < 0.005 and abs(sg["warren"] - 22.68) < 0.005))
    checks.append(("mini-project: with the 15 mm limit the weights are 111, 135.6 and 115 kg: Pratt is lightest",
                   abs(w["pratt"] - 110.94) < 0.01 and abs(w["howe"] - 135.65) < 0.01 and abs(w["warren"] - 115.05) < 0.01
                   and w["pratt"] < w["warren"] < w["howe"]))
    checks.append(("mini-project: areas are scaled up by 1.45, 1.69 and 1.51 to meet the limit",
                   abs(sc["pratt"] - 1.453) < 0.001 and abs(sc["howe"] - 1.693) < 0.001 and abs(sc["warren"] - 1.512) < 0.001))
    # --- edge cases
    z = L.solve_truss(nodes, members, EA, sup, {2: (0.0, 0.0)})
    checks.append(("edge: zero load gives zero forces and zero deflection", np.allclose(z["forces"], 0.0) and np.allclose(z["u"], 0.0)))
    up = L.solve_truss(nodes, members, EA, sup, {2: (0.0, 10.0)})
    checks.append(("edge: reversing the load reverses every force (tension and compression swap)", np.allclose(up["forces"], -F, atol=1e-9)))
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
