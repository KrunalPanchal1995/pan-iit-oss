"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # hand calculation of the solar day: sum of 12 midpoint sines = 1 / sin(pi/24)
    per_kwp = L.solar_day(1.0).sum() / L.DERATE
    checks.append((f"solar day sums to 1/sin(pi/24) = 7.661 per kWp (got {per_kwp:.3f})", abs(per_kwp - 1 / np.sin(np.pi / 24)) < 1e-9))
    checks.append(("hourly sum is within 0.5% of the exact area 24/pi", abs(per_kwp - 24 / np.pi) / (24 / np.pi) < 0.005))
    checks.append(("no sun at night", L.solar_day(2.0)[[0, 3, 5, 18, 22]].sum() == 0))
    checks.append(("load day with a 2 h heater is 8.26 kWh", abs(L.load_day().sum() - 8.26) < 1e-9))

    # worked example: 1 kWp, average weather (cloud 0.85, no random variation)
    day_net = 8.26 - 0.85 * L.DERATE * 7.661297575
    hand_net = 30 * day_net
    hand_bill = 50 + 100 * 3.0 + (hand_net - 100) * 5.0
    r = L.simulate_month(random=False, kwp=1.0)
    checks.append((f"worked example: net {hand_net:.1f} kWh, bill Rs {hand_bill:.1f} by hand (got {r['net']:.1f}, Rs {r['bill_net']:.1f})",
                   abs(r["net"] - hand_net) < 0.01 and abs(r["bill_net"] - hand_bill) < 0.1))
    checks.append(("import - export equals load - generation", abs(r["import"] - r["export"] - (r["load"] - r["gen"])) < 1e-6))
    r0 = L.simulate_month(random=False, kwp=0.0)
    checks.append(("no panels: bill equals the Session 2 bill of Rs 1208.50", abs(r0["bill_net"] - 1208.5) < 1e-6 and r0["export"] == 0))
    checks.append(("exports earning nothing never lowers the bill", r["bill_no_credit"] >= r["bill_net"]))
    bills = [L.simulate_month(random=False, kwp=k)["bill_net"] for k in np.arange(0, 3.01, 0.25)]
    checks.append(("more panels never raise the bill", all(b2 <= b1 + 1e-9 for b1, b2 in zip(bills, bills[1:]))))
    big = L.simulate_month(random=False, kwp=3.0)
    checks.append(("limit: net energy below zero, bill floors at the fixed charge Rs 50", big["net"] < 0 and abs(big["bill_net"] - 50.0) < 1e-9))

    a = L.simulate_month(seed=5, kwp=1.0)
    b = L.simulate_month(seed=5, kwp=1.0)
    c = L.simulate_month(seed=6, kwp=1.0)
    checks.append(("same seed gives the same month, another seed a different one", a["bill_net"] == b["bill_net"] and a["bill_net"] != c["bill_net"]))
    mean_load = np.mean([L.simulate_month(seed=s, kwp=0.0)["load"] for s in range(200)])
    checks.append((f"mean random load within 1% of the hand value 247.8 kWh (got {mean_load:.1f})", abs(mean_load - 247.8) / 247.8 < 0.01))
    m, s = L.bill_spread(100, kwp=1.0)
    checks.append((f"random months: mean Rs {m:.0f} within 5% of the average-weather Rs {r['bill_net']:.0f}, spread above 0", abs(m - r["bill_net"]) / r["bill_net"] < 0.05 and s > 0))
    hi = L.simulate_month(random=False, kwp=1.0, rate_mult=1.2)["bill_net"]
    checks.append(("sensitivity: tariff x1.2 raises the energy part of the bill by 20%", abs((hi - 50) / (r["bill_net"] - 50) - 1.2) < 1e-9))
    checks.append(("sensitivity: more usage gives a bigger bill", L.simulate_month(random=False, usage=1.2)["bill_net"] > L.simulate_month(random=False, usage=0.8)["bill_net"]))
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
