"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # analytic reference for the solar model
    analytic = sum(L.clear_day_energy_per_kw(d) for d in range(365))
    hourly = float(L.clear_sky_per_kw().sum())
    checks.append((f"worked example: yearly clear-sky energy per kW, hourly sum {hourly:.0f} kWh vs analytic sum of A x 2D/pi {analytic:.0f} kWh (within 1 percent)",
                   abs(hourly - analytic) / analytic < 0.01))
    day0 = float(L.clear_sky_per_kw()[0].sum())
    checks.append(("a single clear winter day matches A x 2D/pi within 2 percent", abs(day0 - L.clear_day_energy_per_kw(0)) / L.clear_day_energy_per_kw(0) < 0.02))
    k = L.clearness(0.5, 1)
    checks.append(("clearness K is between 0.55 and 1 and has mean near 1 - 0.45 c = 0.775 (within 0.06)",
                   bool(k.min() >= 0.55 - 1e-12 and k.max() <= 1.0) and abs(k.mean() - 0.775) < 0.06))
    checks.append(("cloudiness 0 gives K = 1 on every day", bool(np.all(L.clearness(0.0, 7) == 1.0))))
    checks.append(("the same seed gives the same year, a different seed does not",
                   bool(np.array_equal(L.clearness(0.5, 3), L.clearness(0.5, 3))) and not np.array_equal(L.clearness(0.5, 3), L.clearness(0.5, 4))))
    bill = [300] * 12
    d = L.monthly_to_daily(bill)
    checks.append(("monthly bills convert to 365 days that add back to the bill total", len(d) == 365 and abs(d.sum() - 3600) < 1e-9))

    pv_unit = L.pv_unit_year(0.5, 1)
    load = L.load_year(L.default_daily(10.0))
    pv = 4.0 * pv_unit

    # conservation over 8760 hours
    res = L.simulate_year(pv, load, 8.0, 4.0, 0.9)
    resid = L.conservation_residual(res, pv, load, 0.9)
    checks.append((f"energy conservation over the year (residual {resid:.1e} kWh)", abs(resid) < 1e-6))

    # no battery: import = sum of max(load - pv, 0), computed independently
    nb = L.simulate_year(pv, load, 0.0, 0.0, 0.9)
    checks.append(("no battery: import equals the sum of max(demand - solar, 0)", abs(nb["imp"].sum() - np.maximum(load - pv, 0).sum()) < 1e-6))
    # no array: everything is imported
    na = L.simulate_year(np.zeros_like(load), load, 8.0, 4.0, 0.9)
    checks.append(("no array: all demand is imported and reliability is 0", abs(na["imp"].sum() - load.sum()) < 1e-6))
    # lower bound: no design can beat solar / demand
    ok = True
    for pk, cap in ((1.0, 40.0), (2.0, 24.0), (4.0, 8.0), (8.0, 24.0)):
        m = L.evaluate(pk, cap, pv_unit, load)
        ok &= m["reliability"] <= L.reliability_ceiling(pk * pv_unit, load) + 1e-9
    checks.append(("edge case: reliability never exceeds the ceiling solar/demand (a 1 kW array stays below 0.531 even with 40 kWh)", ok))
    m1 = L.evaluate(1.0, 40.0, pv_unit, load)
    checks.append(("a huge battery cannot rescue a 1 kW array: reliability stays below 0.55", m1["reliability"] < 0.55))

    # reliability behaviour
    rs = [L.evaluate(4.0, c, pv_unit, load)["reliability"] for c in (0.0, 4.0, 8.0, 16.0)]
    checks.append(("more battery never lowers reliability (4 kW array)", all(b >= a - 1e-9 for a, b in zip(rs, rs[1:]))))
    checks.append(("diminishing returns: the first 8 kWh add much more than the next 8", rs[2] - rs[0] > 5 * (rs[3] - rs[2])))
    rc = [L.evaluate(4.0, 8.0, L.pv_unit_year(c, 1), load)["reliability"] for c in (0.0, 0.5, 1.0)]
    checks.append(("cloudier years are less reliable", rc[0] >= rc[1] >= rc[2] and rc[0] > rc[2]))
    rd = [L.evaluate(4.0, 8.0, pv_unit, load * s)["reliability"] for s in (0.7, 1.0, 1.3)]
    checks.append(("higher demand lowers reliability", rd[0] > rd[1] > rd[2]))
    m = L.evaluate(4.0, 8.0, pv_unit, load)
    checks.append(("loss-of-load hours are counted from the hourly import (4 kW, 8 kWh gives 218)", m["lolh"] == int((L.simulate_year(pv, load, 8.0, 4.0, 0.9)["imp"] > L.LOL_LIMIT_KW).sum()) == 218))

    # search
    designs = L.search(pv_unit, load)
    best = L.cheapest(designs, 0.9)
    checks.append((f"cost-optimal design for R >= 0.9 is 2.5 kW + 7 kWh, cost 5300 (got {best['peak_kw']} kW, {best['cap_kwh']} kWh, {best['cost']:.0f})",
                   best["peak_kw"] == 2.5 and best["cap_kwh"] == 7.0 and abs(best["cost"] - 5300.0) < 1e-9))
    cheaper_ok = [x for x in designs if x["cost"] < best["cost"] - 1e-9 and x["reliability"] >= 0.9]
    checks.append(("no cheaper design on the grid meets the target", len(cheaper_ok) == 0))
    front = L.pareto_front(designs)
    costs = [f["cost"] for f in front]
    rels = [f["reliability"] for f in front]
    checks.append(("Pareto front: cost and reliability both increase along it", costs == sorted(costs) and all(b > a for a, b in zip(rels, rels[1:]))))
    dominated = any(x["cost"] < f["cost"] - 1e-9 and x["reliability"] > f["reliability"] + 1e-12 for f in front for x in designs)
    checks.append(("no design beats a Pareto-front design on both cost and reliability", not dominated))
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
