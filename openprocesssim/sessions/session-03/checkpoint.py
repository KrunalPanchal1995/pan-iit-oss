"""Checkpoint for Session 3. Prints PASS or FAIL."""
import copy

import numpy as np


def _refused(L, fs):
    try:
        L.check_flowsheet(fs)
    except L.SpecError as e:
        return str(e)
    return None


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    fs = L.loop_flowsheet()
    ss = L.solve(fs, "substitution")
    wg = L.solve(fs, "wegstein")
    cl = L.closure(fs, wg)
    st = wg["streams"]
    checks.append(("graph: tear stream is R and the run order is M, RX, HX, FL, SP", wg["tear"] == ["R"] and wg["order"] == ["M", "RX", "HX", "FL", "SP"]))
    checks.append((f"substitution needs 18 iterations and Wegstein 7 at tolerance 1e-10 (got {ss['iterations']}, {wg['iterations']})",
                   ss["iterations"] == 18 and wg["iterations"] == 7 and ss["converged"] and wg["converged"]))
    checks.append(("both methods find the same solution (recycle flow agrees within 1e-8)", abs(ss["streams"]["R"].total() - st["R"].total()) < 1e-8))
    checks.append((f"product V = 83.70 mol/s with 0.6311 benzene, bottoms B = 16.30 mol/s (got {st['V'].total():.2f}, {L.purity(wg):.4f}, {st['B'].total():.2f})",
                   round(st["V"].total(), 2) == 83.70 and round(L.purity(wg), 4) == 0.6311 and round(st["B"].total(), 2) == 16.30))
    checks.append((f"recycle flow is 146.66 mol/s (got {st['R'].total():.2f})", round(st["R"].total(), 2) == 146.66))
    checks.append((f"mass closure of every component is below 1e-8 (got {cl['mass_error']:.1e})", cl["mass_error"] < 1e-8 and float(np.max(np.abs(cl["component_error"]))) < 1e-8))
    checks.append(("overall: product moles equal feed moles (reaction is mole for mole)", abs(st["V"].total() + st["B"].total() - 100.0) < 1e-8))
    checks.append((f"energy closure: products minus feed equals the sum of duties to within 1e-3 W (got {cl['energy_error']:.1e})", abs(cl["energy_error"]) < 1e-3))
    checks.append(("reactor extent is 54.49 mol/s (30 percent of the toluene entering it)", round(wg["extents"]["RX"], 2) == 54.49 and abs(wg["extents"]["RX"] - 0.3 * st["S1"].n[1]) < 1e-9))
    # phase rule: V and L compositions depend only on T (two phases, binary)
    pur = [L.purity(L.solve(L.loop_flowsheet(r=r), "wegstein")) for r in (0.5, 0.7, 0.95)]
    checks.append(("sensitivity: the split fraction does not change purity (0.6311 for r = 0.5, 0.7, 0.95)", all(round(p, 4) == 0.6311 for p in pur)))
    flows = [L.solve(L.loop_flowsheet(r=r), "wegstein")["streams"]["V"].total() for r in (0.5, 0.9, 0.99)]
    checks.append((f"sensitivity: product flow rises with r: 25.80, 83.70, 98.33 mol/s (got {flows[0]:.2f}, {flows[1]:.2f}, {flows[2]:.2f})",
                   [round(f, 2) for f in flows] == [25.80, 83.70, 98.33]))
    pt = {T: L.solve(L.loop_flowsheet(T_flash=T), "wegstein") for T in (364.0, 366.0, 368.0, 370.0, 372.0)}
    checks.append(("sensitivity: purity falls with flash T: 0.7493, 0.6921, 0.6311, 0.5662, 0.4973 for 364 to 372 K",
                   [round(L.purity(r), 4) for r in pt.values()] == [0.7493, 0.6921, 0.6311, 0.5662, 0.4973]))
    checks.append(("sensitivity: product flow rises with flash T: 71.13 to 92.38 mol/s", round(pt[364.0]["streams"]["V"].total(), 2) == 71.13 and round(pt[372.0]["streams"]["V"].total(), 2) == 92.38))
    # heat exchanger, UA mode
    s = L.Stream(np.array([0.0, 100.0, 0.0]), 320.0, L.P_ATM)
    out, q, _ = L.run_block({"type": "hx", "UA": 15700.0, "T_utility": 400.0}, [s])
    eps = 1.0 - np.exp(-1.0)
    checks.append((f"hand calculation: UA = n Cp gives T_out = 370.6 K and Q = 793.9 kW (got {out[0].T:.1f}, {q / 1000:.1f})",
                   round(out[0].T, 1) == 370.6 and abs(q - eps * 15700.0 * 80.0) < 1e-6 and round(q / 1000, 1) == 793.9))
    checks.append(("heat exchanger in outlet-spec mode: duty equals the enthalpy change", abs(L.run_block({"type": "hx", "T_out": 350.0}, [s])[1] - 100 * 157 * 30.0) < 1e-6))
    # degrees of freedom
    f1 = copy.deepcopy(fs)
    del f1["blocks"][3]["T"]
    m1 = _refused(L, f1)
    f2 = copy.deepcopy(fs)
    f2["feeds"]["R"] = f2["feeds"]["F"]
    m2 = _refused(L, f2)
    f3 = copy.deepcopy(fs)
    f3["blocks"][2]["UA"] = 1000.0
    m3 = _refused(L, f3)
    f4 = copy.deepcopy(fs)
    f4["feeds"]["F"] = None
    m4 = _refused(L, f4)
    checks.append(("DOF: a flash without its temperature is refused as under-specified (DOF -1)", m1 is not None and "UNDER-SPECIFIED" in m1 and "'T'" in m1 and "-1" in m1))
    checks.append(("DOF: a stream that is both a feed and a block output is refused as over-specified (DOF +1)", m2 is not None and "OVER-SPECIFIED" in m2 and "stream R" in m2 and "+1" in m2))
    checks.append(("DOF: a heat exchanger with both T_out and UA is refused as over-specified", m3 is not None and "OVER-SPECIFIED" in m3 and "block HX" in m3))
    checks.append(("DOF: a feed without values is refused as under-specified", m4 is not None and "UNDER-SPECIFIED" in m4 and "feed stream F" in m4))
    checks.append(("DOF: the good flowsheet has DOF 0 and no messages", L.degrees_of_freedom(fs) == (0, [])))
    try:
        L.solve(f1)
        refused = False
    except L.SpecError:
        refused = True
    checks.append(("the solver itself refuses the under-specified flowsheet", refused))
    # acyclic part
    fa = {"feeds": fs["feeds"], "blocks": [copy.deepcopy(b) for b in fs["blocks"] if b["name"] in ("RX", "HX", "FL")]}
    fa["blocks"][0]["in"] = ["F"]
    checks.append(("a flowsheet without a loop needs no tear stream and is ordered RX, HX, FL", L.find_tear_streams(fa) == [] and L.topological_order(fa) == ["RX", "HX", "FL"]))
    # mini-project
    fm = L.loop_flowsheet(r=0.85, T_flash=365.5)
    rm = L.solve(fm, "wegstein")
    clm = L.closure(fm, rm)
    sm = rm["streams"]
    checks.append((f"mini-project: T = 365.5 K, r = 0.85 gives purity 0.7067, product 65.54, recycle 195.25, bottoms 34.46 mol/s (got {L.purity(rm):.4f}, {sm['V'].total():.2f}, {sm['R'].total():.2f}, {sm['B'].total():.2f})",
                   round(L.purity(rm), 4) == 0.7067 and round(sm["V"].total(), 2) == 65.54 and round(sm["R"].total(), 2) == 195.25 and round(sm["B"].total(), 2) == 34.46))
    checks.append((f"mini-project closure below 1e-8 (got {clm['mass_error']:.1e})", clm["mass_error"] < 1e-8))
    p366 = L.purity(L.solve(L.loop_flowsheet(r=0.85, T_flash=366.0), "wegstein"))
    v80 = L.solve(L.loop_flowsheet(r=0.8, T_flash=365.5), "wegstein")["streams"]["V"].total()
    checks.append((f"mini-project levers: 366.0 K fails purity ({p366:.4f} < 0.70) and r = 0.80 fails flow ({v80:.2f} < 60)", p366 < 0.70 and v80 < 60.0 and L.purity(rm) >= 0.70 and sm["V"].total() >= 60.0))
    checks.append(("the default settings fail the mini-project purity target (0.6311 < 0.70)", L.purity(ss) < 0.70))
    # failure case 1: infeasible, nothing can leave
    fb = L.loop_flowsheet(r=1.0, T_flash=345.0)
    bs, bw = L.solve(fb, "substitution"), L.solve(fb, "wegstein")
    checks.append((f"failure: r = 1 with T = 345 K never converges; the tear changes by 100 mol/s per iteration, the feed (got {bs['history'][-1]:.0f}, {bw['history'][-1]:.0f})",
                   not bs["converged"] and not bw["converged"] and abs(bs["history"][-1] - 100.0) < 1e-6 and abs(bw["history"][-1] - 100.0) < 1e-6))
    msg = L.convergence_message(bw)
    checks.append(("failure: the report says NOT converged and tells you to check feasibility", msg.startswith("NOT converged") and "feasible" in msg))
    # worked example: no vapour at 345 K, hand answer R = r F / (1 - r) = 900
    fw = L.loop_flowsheet(r=0.9, T_flash=345.0)
    ws = L.solve(fw, "substitution", maxit=1000)
    ww = L.solve(fw, "wegstein", maxit=1000)
    checks.append((f"worked example: at 345 K there is no vapour; hand answer R = 0.9 * 100 / 0.1 = 900 mol/s, B = 100 (got {ww['streams']['R'].total():.1f}, {ww['streams']['B'].total():.1f})",
                   abs(ww["streams"]["R"].total() - 900.0) < 1e-6 and abs(ww["streams"]["B"].total() - 100.0) < 1e-6 and ww["streams"]["V"].total() == 0.0))
    checks.append((f"worked example: substitution needs 263 iterations, Wegstein 34 (got {ws['iterations']}, {ww['iterations']})", ws["iterations"] == 263 and ww["iterations"] == 34))
    w200 = L.solve(fw, "substitution", maxit=200)
    checks.append(("with a limit of 200 iterations substitution stops short of the tolerance", not w200["converged"]))
    # Wegstein is not guaranteed
    ft = L.loop_flowsheet(r=0.9, T_flash=368.0, feed=(0.0, 100.0, 0.0))
    ts, tw = L.solve(ft, "substitution"), L.solve(ft, "wegstein")
    checks.append((f"failure: with a pure-toluene feed substitution converges in 19 iterations but Wegstein does not within 200 (got {ts['iterations']}, {tw['converged']})",
                   ts["converged"] and ts["iterations"] == 19 and not tw["converged"]))
    # failure case 2: azeotrope
    xs = np.linspace(0.0, 1.0, 101)
    tb = [L.raoult_bubble_T(x) for x in xs]
    checks.append((f"azeotrope: Raoult's law gives a lowest bubble point of 351.5 K (pure ethanol), got {min(tb):.1f}", round(min(tb), 1) == 351.5 and int(np.argmin(tb)) == 100))
    gap = L.raoult_bubble_T(0.45) - L.REAL_AZEOTROPE_T
    checks.append((f"azeotrope: at 45 mole percent ethanol Raoult gives 352.3 K, 11.3 K above the real azeotrope (got {L.raoult_bubble_T(0.45):.1f}, {gap:.1f})",
                   round(L.raoult_bubble_T(0.45), 1) == 352.3 and round(gap, 1) == 11.3))
    vmax = max(L.flash_block(L.Stream(np.array([1 - x, 0.0, x]) * 100.0, 330.0, L.P_ATM), 345.0, L.P_ATM)[0].total() for x in xs)
    checks.append(("azeotrope: at 345 K an ideal ethanol-benzene liquid never boils, whatever its composition (V = 0), while the real 45 percent mixture boils near 341 K", vmax == 0.0 and 345.0 > L.REAL_AZEOTROPE_T))
    # edge: no recycle at all
    r0 = L.solve(L.loop_flowsheet(r=0.0), "wegstein")
    checks.append(("edge: r = 0 (no recycle) converges and R = 0", r0["converged"] and r0["streams"]["R"].total() == 0.0))
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
