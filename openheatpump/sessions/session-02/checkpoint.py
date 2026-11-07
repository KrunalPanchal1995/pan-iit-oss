"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("COP_heating = COP_cooling + 1", L.cop_heating_from_cooling(3.0) == 4.0))
    # Carnot from the cooling form: Tc/(Th-Tc) + 1 = Th/(Th-Tc)
    cc = float(L.carnot_cop_cooling(0.0, 35.0))
    ch = float(L.carnot_cop_heating(35.0, 0.0))
    checks.append((f"Carnot heating COP = Carnot cooling COP + 1 ({ch:.3f} = {cc:.3f} + 1)", abs(ch - (cc + 1.0)) < 1e-12))
    checks.append(("kelvin: 0 C is 273.15 K", abs(float(L.kelvin(0.0)) - 273.15) < 1e-12))
    # hand calculation: 308.15 / 35 = 8.804 ; real = 0.45 * 8.804 = 3.962
    checks.append(("hand calculation: Carnot COP_h at 35 C / 0 C is 308.15 / 35 = 8.804", abs(ch - 308.15 / 35.0) < 1e-9))
    checks.append(("real COP is 0.45 x Carnot = 3.962 at 0 C outdoors, 35 C supply", abs(float(L.real_cop(0.0, 35.0)) - 3.962) < 1e-3))
    checks.append(("real COP never exceeds the Carnot limit", bool(np.all(L.real_cop(np.linspace(-20, 15, 36), 35.0) <= L.carnot_cop_heating(35.0, np.linspace(-20, 15, 36)) + 1e-12))))
    checks.append(("real COP is capped when the gap is tiny", float(L.real_cop(34.0, 35.0)) == L.COP_MAX))
    cops = L.real_cop(np.array([-15.0, -5.0, 5.0, 15.0]), 35.0)
    checks.append(("COP rises with outdoor temperature", bool(np.all(np.diff(cops) > 0))))
    # worked example: design load and electricity
    q = L.design_size_kw(0.20, 20.0, -10.0)
    w = float(L.electric_kw(q, L.real_cop(-10.0, 35.0)))
    checks.append((f"worked example: design load 0.20 x 30 = 6.00 kW; heat pump electricity 6.00 / 3.08 = 1.95 kW (got {q:.2f}, {w:.2f})",
                   abs(q - 6.0) < 1e-12 and abs(w - 1.95) < 0.01))
    checks.append(("no heat loss when it is warmer outside than inside", float(L.heat_loss_kw(0.2, 20.0, 25.0)) == 0.0))
    # design problem: COP floor 2.0 at 35 C supply
    t2 = L.outdoor_temp_for_cop(2.0, 35.0)
    checks.append((f"design: COP falls to 2.0 at {t2:.1f} C (35 C supply), and the formula inverts real_cop",
                   abs(t2 - (-34.3)) < 0.1 and abs(float(L.real_cop(t2, 35.0)) - 2.0) < 1e-9))
    checks.append(("COP of 1.0 only at an absurdly low temperature (below -100 C)", L.outdoor_temp_for_cop(1.0, 35.0) < -100))
    # energy over the season
    s = L.season_energy(0.20)
    checks.append(("seasonal: heater electricity equals the heat needed", abs(s["heater_kwh"] - s["heat_kwh"]) < 1e-9))
    checks.append(("seasonal: heat pump uses less electricity than the heater", s["hp_kwh"] < s["heater_kwh"]))
    # hand check with constant temperature: 151 days at 0 C, UA 0.2: 24 x 0.2 x 20 x 151 = 14496 kWh
    c = L.season_energy(0.20, temps=np.zeros(151))
    checks.append(("hand calculation: 151 days at 0 C needs 24 x 0.2 x 20 x 151 = 14496 kWh of heat", abs(c["heat_kwh"] - 14496.0) < 1e-6))
    checks.append(("hand calculation: heat pump electricity at 0 C is 14496 / 3.962 = 3659 kWh", abs(c["hp_kwh"] - 14496.0 / 3.9619) < 2.0))
    # edge: invalid supply
    try:
        L.carnot_cop_heating(0.0, 10.0)
        rejected = False
    except ValueError:
        rejected = True
    checks.append(("a supply temperature below the outdoor temperature is rejected", rejected))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
