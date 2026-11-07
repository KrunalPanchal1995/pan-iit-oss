"""Checkpoint for Session 4. Prints PASS or FAIL."""
import numpy as np


def _raises(f, *a):
    try:
        f(*a)
    except ValueError:
        return True
    return False


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    volts, amps = L.solve_netlist(L.TWO_LOOP_TEXT)
    v, j = L.solve_network(**L.TWO_LOOP)
    checks.append(("worked example: the text version of the two-loop circuit gives V(A) = 6.545 V and source currents 34.55 mA and -12.73 mA",
                   abs(volts["a"] - 6.54545) < 1e-4 and abs(amps["v1"] - 0.034545) < 1e-6 and abs(amps["v2"] + 0.012727) < 1e-6))
    checks.append(("text and Python lists give the same answer to 1e-12 (the reader builds the same circuit)",
                   abs(volts["a"] - v[1]) < 1e-12 and abs(volts["top1"] - 10.0) < 1e-12 and abs(volts["top2"] - 4.0) < 1e-12))

    table = {"1k": 1e3, "4.7K": 4700.0, "2.2meg": 2.2e6, "2.2MEG": 2.2e6, "1M": 1e-3, "100m": 0.1, "5V": 5.0, "2mA": 2e-3,
             "1kohm": 1e3, "2.2e3": 2200.0, "1F": 1e-15, "10u": 1e-5, "3.3n": 3.3e-9, "-5": -5.0, ".5k": 500.0, "1t": 1e12, "47p": 4.7e-11}
    bad = [s for s, x in table.items() if abs(L.parse_value(s) / x - 1) > 1e-12]
    checks.append((f"value suffixes: {len(table)} values read correctly, including 1M = 0.001 (milli, not mega), 2.2meg and 1F = 1e-15" + (f" (wrong: {bad})" if bad else ""), not bad))
    checks.append(("a value that cannot be read is rejected: '', 'abc', '1..2', '1k2', '--5'", all(_raises(L.parse_value, s) for s in ("", "abc", "1..2", "1k2", "--5"))))

    text = "* a comment\n\nV1 Top gnd DC 12  ; supply\nr1 TOP mid 1K\nR2 mid 0 2k\n.end\nR9 junk 0 1\n"
    net = L.parse_netlist(text)
    vv, _ = L.solve_netlist(text)
    checks.append(("format rules: comments, blank lines, '; ...', 'DC', capital letters, 'gnd' and '.end' are handled; nodes are numbered in order of appearance",
                   net["nodes"] == {"0": 0, "top": 1, "mid": 2} and len(net["resistors"]) == 2 and abs(vv["mid"] - 8.0) < 1e-12))

    rng = np.random.default_rng(5)
    worst, ok = 0.0, True
    for _ in range(30):
        n = int(rng.integers(3, 7))
        rs = [(k, k + 1, float(rng.choice([100, 220, 470, 1000, 4700, 10000]))) for k in range(0, n)]
        rs += [(int(rng.integers(0, n)), n, float(rng.choice([330, 680, 2200]))) for _ in range(2)]
        vs = [(1, 0, float(rng.choice([5, 9, 12])))]
        isrc = [(0, 2, 0.002)]
        back = L.parse_netlist(L.to_netlist(n, rs, vs, isrc))
        ok &= back["resistors"] == rs and back["vsources"] == vs and back["isources"] == isrc and back["n_nodes"] == n
        a, _ = L.solve_network(n, rs, vs, isrc)
        b, _ = L.solve_network(back["n_nodes"], back["resistors"], back["vsources"], back["isources"])
        worst = max(worst, float(np.abs(a - b).max()))
    checks.append((f"round trip: parse(to_netlist(circuit)) is the same circuit for 30 random networks (largest voltage difference {worst:.0e})", ok and worst < 1e-12))
    checks.append(("format_value and parse_value are inverses: 4700 -> '4.7k', 0.001 -> '1m', 2.2e6 -> '2.2meg'",
                   L.format_value(4700) == "4.7k" and L.format_value(0.001) == "1m" and L.format_value(2.2e6) == "2.2meg"
                   and all(abs(L.parse_value(L.format_value(x)) / x - 1) < 1e-12 for x in (1.0, 0.047, 33e3, 1.5e-9, 7.2e9))))

    def msg(t):
        try:
            L.parse_netlist(t)
        except L.NetlistError as e:
            return str(e)
        return ""
    cases = [("V1 a 0 5\nR1 a 0 1k\nQ1 a 0 1\n", "line 3"), ("V1 a 0 5\nR1 a 0\n", "line 2"), ("V1 a 0 5\nR1 a 0 1k\nR1 a 0 2k\n", "line 3"),
             ("V1 a 0 5\nR1 a a 1k\n", "line 2"), ("V1 a b 5\nR1 a b 1k\n", "ground"), ("V1 a 0 5\nR1 a 0 -1k\n", "line 2"),
             ("V1 a 0 5\nR1 a 0 1x2\n", "line 2"), ("V1 a 0 5\n.tran 1 2\n", "line 2"), ("* nothing\n", "empty")]
    wrong = [t for t, k in cases if k not in msg(t)]
    checks.append((f"failure cases: {len(cases)} broken files are refused with a message that names the line (or the ground)", not wrong))
    checks.append(("a floating part parses but the solver rejects it (singular matrix)", _raises(L.solve_netlist, "V1 a 0 5\nR1 a 0 1k\nR2 c d 2k\n")))

    # the checker
    found = L.check_netlist(L.TECH_NETLIST)
    kinds = {(ln, kd) for ln, kd, _ in found}
    checks.append((f"technician's file: the checker reports the three planted faults at lines 6 (warning), 7 and 8 (errors) and nothing else; found {sorted(kinds)}",
                   kinds == {(6, "warning"), (7, "error"), (8, "error")} and len(found) == 3))
    checks.append(("a clean file gives no problems; the repaired bridge and the two-loop file are clean", L.check_netlist(L.corrected_bridge()) == [] and L.check_netlist(L.TWO_LOOP_TEXT) == []))
    garbage = ["", "\n\n", "R1", "V1 a", "!!!", "R1 a b c d e f", ".end", "x" * 50, "R1 0 0 1k", "I1 a 0 1\nI2 a 0 1m\n"]
    try:
        for g in garbage:
            L.check_netlist(g)
        no_crash = True
    except Exception:
        no_crash = False
    checks.append(("the checker never crashes, even on 10 strange inputs", no_crash))
    many = "V1 a 0 5\nR1 a 0 1k\nR1 a 0 1M\nR3 b c 2k\nQ9 a 0 1\nR4 a 0 1..5\n"
    checks.append(("the checker lists every problem, not only the first (at least 5 for a file with five faults)", len(L.check_netlist(many)) >= 5))

    # worked example of Section E: the 1M trap
    typo = "V1 in 0 12\nR1 in out 10k\nR2 out 0 1M\n"
    vt, at = L.solve_netlist(typo)
    vi, ai = L.solve_netlist(typo.replace("1M", "1meg"))
    checks.append((f"worked example (Section E): typed 1M the divider gives V(out) = {vt['out']:.2e} V and 1.2 mA; the intended 1meg gives {vi['out']:.2f} V and {1e6 * ai['v1']:.2f} uA; the checker warns about line 3",
                   abs(vt["out"] - 1.2e-6) < 1e-9 and abs(at["v1"] - 1.2e-3) < 1e-8 and abs(vi["out"] - 11.8812) < 1e-4 and abs(ai["v1"] - 11.881e-6) < 1e-8
                   and [(a, b) for a, b, _ in L.check_netlist(typo)] == [(3, "warning")]))
    # mini-project
    formula = L.bridge_formula(5.0, 1000.0, 1000.0, 1385.0, 1000.0)
    checks.append(("mini-project: the repaired bridge read from text gives 403.56 mV, the same as the closed formula", abs(L.bridge_output() - formula) < 1e-12 and abs(L.bridge_output() - 0.40356) < 1e-5))
    r_th = 1000 * 1385 / 2385 + 500.0
    hand = formula * 10000.0 / (r_th + 10000.0)
    checks.append((f"hand check (Section F): R_th = {r_th:.1f} ohm, so a 10 kohm meter reads V_th x 10 / (R_th + 10) = {1000 * hand:.2f} mV", abs(L.bridge_output(10000.0) - hand) < 1e-12 and abs(hand - 0.36420) < 1e-5))
    checks.append(("a meter loads the bridge less when its resistance is larger (loading error 52 % at 1 kohm, 9.8 % at 10 kohm, 1.1 % at 100 kohm)",
                   L.loading_error(1e3) > L.loading_error(1e4) > L.loading_error(1e5) > L.loading_error(1e6)
                   and abs(L.loading_error(1e3) - 0.5194) < 1e-3 and abs(L.loading_error(1e4) - 0.0975) < 1e-3 and abs(L.loading_error(1e5) - 0.0107) < 1e-3))
    sm = L.smallest_meter(0.01)
    checks.append((f"mini-project: the smallest meter from the 1-2-5 list with a loading error of at most 1 % is {L.format_value(sm) if sm else None} ohm (100 kohm just fails); the typo R4 = 1M makes node b 0 V instead of 2.5 V",
                   sm == 2e5 and L.solve_netlist(L.TECH_NETLIST.replace("R2 a b 10k\n", "").replace("R5 c d 2.2k\n", ""))[0]["b"] < 1e-5))
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
