"""Checkpoint for Session 4. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    K = L.kelvin
    # ---- temperature and resistance --------------------------------------------------------------
    f = {t: L.resistance_factor(K(t)) for t in (-10, 0, 25, 45)}
    checks.append((f"resistance factor r(T)/r(25 C): 2.924 at -10 C, 2.093 at 0 C, 1 at 25 C, 0.602 at 45 C (got {f[-10]:.3f}, {f[0]:.3f}, {f[25]:.3f}, {f[45]:.3f})",
                   abs(f[-10] - 2.924) < 0.002 and abs(f[0] - 2.093) < 0.002 and abs(f[25] - 1.0) < 1e-12 and abs(f[45] - 0.602) < 0.002))
    r = [float(L.r_internal(0.0, K(t))) for t in (0, 25, 45)]
    checks.append(("fresh-cell resistance: 1.758 ohm at 0 C, 0.840 ohm at 25 C, 0.506 ohm at 45 C (the 1.05 is the fresh-solution term)",
                   abs(r[0] - 1.7578) < 5e-4 and abs(r[1] - 0.84) < 1e-9 and abs(r[2] - 0.5058) < 5e-4 and abs(r[1] / 0.8 - 1.05) < 1e-12))
    p = [L.max_power(K(t)) for t in (0, 25, 45)]
    checks.append((f"maximum power of a fresh cell E^2 / (4 r): 0.181 W at 0 C, 0.380 W at 25 C, 0.633 W at 45 C (got {p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f})",
                   abs(p[0] - 0.181) < 0.001 and abs(p[1] - 0.380) < 0.001 and abs(p[2] - 0.633) < 0.001))
    # ---- the pack from Session 3 ------------------------------------------------------------------
    rep = {t: L.pack_report(10, 2, T=K(t)) for t in (0, 25, 45)}
    checks.append((f"worked example, 10 x 2 = 20 cells: 25 C start 9.909 V and 5.95 h; 45 C 10.436 V and 6.13 h (got {rep[25]['v_start']:.3f} V, {rep[25]['hours']:.2f} h; {rep[45]['v_start']:.3f} V, {rep[45]['hours']:.2f} h)",
                   abs(rep[25]["v_start"] - 9.9086) < 5e-4 and abs(rep[25]["hours"] - 5.951) < 0.002 and abs(rep[45]["v_start"] - 10.4358) < 5e-4 and abs(rep[45]["hours"] - 6.134) < 0.002))
    checks.append((f"worked example: the same pack at 0 C starts at {rep[0]['v_start']:.3f} V (below 9 V) and gives 0 h, limited by the start",
                   abs(rep[0]["v_start"] - 8.7172) < 5e-4 and rep[0]["hours"] == 0.0 and rep[0]["limit"] == "start" and rep[25]["limit"] == "cutoff"))
    r9 = L.pack_report(9, 2, T=K(25))
    checks.append(("9 x 2 at 25 C starts at 9.03 V but is below 9 V after 0.19 h (Session 3's coarser grid gave 0.20)",
                   abs(r9["v_start"] - 9.0286) < 5e-4 and abs(r9["hours"] - 0.1922) < 0.001 and r9["limit"] == "cutoff"))
    hs = [L.pack_runtime_hours(ns, 2, 30.0, 9.0, K(25)) for ns in (10, 11, 12, 13)]
    checks.append((f"more cells in series can shorten the run (2 strings, 25 C): 10 -> 5.95 h, 11 -> 5.93, 12 -> 5.62, 13 -> 5.31 (got {', '.join(f'{h:.2f}' for h in hs)})",
                   all(a > b for a, b in zip(hs, hs[1:])) and abs(hs[0] - 5.951) < 0.002 and abs(hs[3] - 5.307) < 0.002))
    big = L.pack_report(12, 6, T=K(25))
    checks.append(("heavy parallelism: 12 x 6 = 72 cells runs 15.5 h (limited by the cutoff as the Cu2+ runs out, not by the lamp at the start)",
                   abs(big["hours"] - 15.523) < 0.01 and big["limit"] == "cutoff"))
    # ---- validation --------------------------------------------------------------------------------
    worst_rk = worst_eq = 0.0
    for ns, npar, tc, kw in ((10, 2, 25, {}), (12, 2, 0, {}), (11, 2, 0, {}), (9, 2, 25, {}), (11, 2, 45, {}), (11, 2, 0, {"r0": 0.56}), (11, 2, 0, {"dT": 5.0}), (13, 3, -10, {})):
        h = L.pack_runtime_hours(ns, npar, 30.0, 9.0, K(tc), **kw)
        worst_rk = max(worst_rk, abs(h - L.rk4_runtime_hours(ns, npar, 30.0, 9.0, K(tc), **kw)))
        worst_eq = max(worst_eq, abs(h - L.single_cell_equivalent_hours(ns, npar, 30.0, 9.0, K(tc), **kw)))
    checks.append((f"validation: an independent RK4 solver in time agrees with the pack runtime to {worst_rk:.4f} h over 8 designs", worst_rk < 2e-3))
    checks.append((f"validation: a pack equals one cell with load R npar / ns and cutoff v_min / ns (largest gap {worst_eq:.4f} h)", worst_eq < 2e-3))
    r_eq = 30.0 * 2 / 10
    checks.append(("the 10 x 2 pack looks like one cell feeding 6 ohm, and its lamp voltage is 10 times that cell's terminal voltage",
                   abs(r_eq - 6.0) < 1e-12 and abs(float(L.pack_curve(10, 2, 30.0)["v"][0]) - 10 * float(L.ocv(0.0)) * 6.0 / (6.0 + float(L.r_internal(0.0)))) < 1e-9))
    # ---- design search -----------------------------------------------------------------------------
    best = L.design_search()["best"]
    checks.append((f"design search at 0, 25 and 45 C: the smallest working pack is 12 x 2 = 24 cells with 5.60, 5.62 and 5.37 h (got {best['ns']} x {best['npar']}, {', '.join(f'{h:.2f}' for h in best['hours'])})",
                   (best["ns"], best["npar"]) == (12, 2) and np.allclose(best["hours"], (5.6009, 5.6192, 5.3719), atol=0.002)))
    singles = {tc: L.design_search(temps_c=(tc,))["best"] for tc in (0.0, 25.0, 45.0)}
    checks.append(("each temperature alone: 24 cells at 0 C (12 x 2), 20 at 25 C (10 x 2, the Session 3 answer), 18 at 45 C (9 x 2): the coldest day sets the size",
                   [(b["cells"], b["ns"], b["npar"]) for b in singles.values()] == [(24, 12, 2), (20, 10, 2), (18, 9, 2)]))
    res = L.design_search()
    cells_ok = sorted(row["cells"] for row in res["rows"] if row["ok"])
    checks.append(("no pack with fewer than 24 cells works at all three temperatures: of 13 x 6 = 78 packs, 39 work, the smallest are 24, 26 and 30 cells",
                   len(res["rows"]) == 78 and all(not row["ok"] for row in res["rows"] if row["cells"] < 24) and len(cells_ok) == 39 and cells_ok[:3] == [24, 26, 30]))
    need = L.coldest_designable([-25, -20, -15, -10, -5, 0, 25, 45])
    checks.append((f"smallest pack for one ambient temperature: 42, 39, 32, 28, 26, 24 cells at -25, -20, -15, -10, -5, 0 C; 20 at 25 C; 18 at 45 C (got {need})",
                   need == [42, 39, 32, 28, 26, 24, 20, 18]))
    # ---- design levers: the roadmap checkpoint -----------------------------------------------------
    h_low = L.pack_runtime_hours(11, 2, 30.0, 9.0, K(0), r0=L.R0_LOW)
    v_low = float(L.pack_curve(11, 2, 30.0, K(0), r0=L.R0_LOW)["v"][0])
    checks.append((f"roadmap checkpoint: with a cell of 0.56 ohm (30 percent lower resistance) a 11 x 2 = 22 cell pack keeps the 30 ohm lamp at 9 V or more for {h_low:.2f} h at 0 C (start {v_low:.2f} V): fewer than 24 cells",
                   22 < 24 and h_low >= 5.0 and v_low >= 9.0 and abs(h_low - 5.876) < 0.002 and abs(v_low - 10.116) < 5e-3))
    lv = {row["name"]: row["best"] for row in L.levers_table()}
    names = list(lv)
    checks.append(("levers, smallest pack working at 0, 25 and 45 C: plain 24 cells, lower-resistance cell 22, pack held 5 K warm 22, both together 20",
                   [lv[n]["cells"] for n in names] == [24, 22, 22, 20] and [(lv[n]["ns"], lv[n]["npar"]) for n in names] == [(12, 2), (11, 2), (11, 2), (10, 2)]))
    checks.append(("every lever design still meets 5 h at 0 C: 5.88 h, 5.37 h and 5.36 h",
                   abs(lv[names[1]]["hours"][0] - 5.876) < 0.002 and abs(lv[names[2]]["hours"][0] - 5.374) < 0.002 and abs(lv[names[3]]["hours"][0] - 5.355) < 0.002 and all(min(lv[n]["hours"]) >= 5.0 for n in names)))
    cold = {"12x2": L.coldest_ok(12, 2), "10x2": L.coldest_ok(10, 2), "11x2 low-r": L.coldest_ok(11, 2, r0=0.56), "11x2 warm": L.coldest_ok(11, 2, dT=5.0)}
    checks.append((f"coldest ambient at which a pack still works: 12 x 2 down to {cold['12x2']:.1f} C, 10 x 2 only down to {cold['10x2']:.1f} C, 11 x 2 with 0.56 ohm to {cold['11x2 low-r']:.1f} C, 11 x 2 held 5 K warm to {cold['11x2 warm']:.1f} C",
                   abs(cold["12x2"] + 3.83) < 0.02 and abs(cold["10x2"] - 15.11) < 0.02 and abs(cold["11x2 low-r"] + 7.83) < 0.02 and abs(cold["11x2 warm"] + 1.89) < 0.02))
    # ---- failures and limits -----------------------------------------------------------------------
    none = L.design_search(temps_c=(-30.0,), ns_range=range(6, 15), np_range=range(1, 4))["best"]
    wide = L.design_search(temps_c=(-30.0,), ns_range=range(6, 41), np_range=range(1, 13))["best"]
    checks.append(("failure: at -30 C a search window of up to 14 x 3 = 42 cells finds nothing and says so (None); a wider window finds 17 x 3 = 51 cells",
                   none is None and wide is not None and (wide["cells"], wide["ns"], wide["npar"]) == (51, 17, 3)))
    checks.append(("failure: a pack that is too small for even 45 C (8 x 2) has no coldest working temperature (None); 12 x 6 works down to -37.3 C; 15 x 6 works to the -40 C limit",
                   L.coldest_ok(8, 2) is None and abs(L.coldest_ok(12, 6) + 37.26) < 0.02 and L.coldest_ok(15, 6) == -40.0))
    bad = 0
    for fn in (lambda: L.pack_runtime_hours(0, 1, 30.0, 9.0), lambda: L.pack_curve(3, 0, 30.0), lambda: L.design_search(hours=0.0),
               lambda: L.design_search(temps_c=()), lambda: L.nernst(0.0)):
        try:
            fn()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs (empty pack, no strings, zero hours, no temperatures, Q = 0) are rejected", bad == 5))
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
