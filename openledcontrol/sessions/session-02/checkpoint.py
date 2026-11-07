"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("equal resistors give half the supply: 6800 / 6800 ohm -> 2.5 V",
                   abs(float(L.divider_voltage(5.0, 6800.0, 6800.0)) - 2.5) < 1e-12))
    lux = np.logspace(-1, 4, 50)
    v = L.divider_voltage(5.0, 6800.0, L.ldr_resistance(lux))
    checks.append(("divider voltage rises with light and stays between 0 and Vcc",
                   bool(np.all(np.diff(v) > 0) and v.min() > 0 and v.max() < 5.0)))
    checks.append(("lux_from_resistance undoes ldr_resistance",
                   np.allclose(L.lux_from_resistance(L.ldr_resistance(lux)), lux, rtol=1e-9)))

    r_ideal = L.fixed_resistor_for(20.0, 2.5)
    checks.append((f"worked example: 20 lux with V_th = 2.5 V needs R = 6156 ohm (got {r_ideal:.0f})", abs(r_ideal - 6156.0) < 2.0))
    checks.append(("worked example: 6800 ohm trips at 17.3 lux and 5600 ohm at 22.9 lux",
                   abs(L.trip_lux(6800.0, 2.5) - 17.3) < 0.05 and abs(L.trip_lux(5600.0, 2.5) - 22.9) < 0.05))
    checks.append(("trip_lux inverts fixed_resistor_for for a non-symmetric threshold (V_th = 1.5 V, 50 lux)",
                   abs(L.trip_lux(L.fixed_resistor_for(50.0, 1.5), 1.5) - 50.0) < 1e-6))
    checks.append(("the divider at the trip point equals the threshold voltage",
                   abs(float(L.divider_voltage(5.0, 6800.0, L.ldr_resistance(L.trip_lux(6800.0, 2.5)))) - 2.5) < 1e-9))

    checks.append(("worked example: LED resistor (5 - 2) / 0.010 = 300 ohm", abs(L.led_resistor() - 300.0) < 1e-9))
    checks.append(("E12 picks: 300 ohm up -> 330, 4730 down -> 4700, 6156 nearest -> 5600, exact 4700 stays",
                   L.e12_pick(300.0, "up") == 330.0 and L.e12_pick(4730.0, "down") == 4700.0
                   and L.e12_pick(6156.0) == 5600.0 and L.e12_pick(4700.0, "down") == 4700.0 and L.e12_pick(4700.0, "up") == 4700.0))
    checks.append(("E12 edge: values just under a decade (9500 ohm) round to 8200 down and 10000 up",
                   L.e12_pick(9500.0, "down") == 8200.0 and L.e12_pick(9500.0, "up") == 10000.0))
    r_b = L.base_resistor(0.00909)
    checks.append((f"worked example: base resistor for 9.09 mA, forced gain 10, is 4730 ohm (got {r_b:.0f})", abs(r_b - 4730.0) < 5.0))

    good = L.transistor_state(4700.0, 330.0)
    checks.append(("with 4.7 kohm the transistor saturates and the LED gets about 8.5 mA",
                   good["saturated"] and abs(good["i_c"] * 1e3 - 8.485) < 0.01))
    checks.append(("the saturated switch dissipates under 2 mW", good["p_q"] < 0.002))
    weak = L.transistor_state(470e3, 330.0)
    checks.append(("a 470 kohm base resistor leaves it unsaturated: LED current under 1 mA",
                   (not weak["saturated"]) and weak["i_c"] < 0.001))
    checks.append(("unsaturated: collector-emitter voltage is well above V_CE(sat)", weak["vce"] > 2.0))
    # edge: the boundary between saturated and unsaturated is where beta * I_B equals the LED current
    rb_edge = (5.0 - 0.7) * 100.0 / ((5.0 - 2.0 - 0.2) / 330.0)
    checks.append(("boundary: at R_B = beta (Vdrive - VBE) / I_sat the switch is just saturated",
                   L.transistor_state(rb_edge, 330.0)["saturated"] and not L.transistor_state(rb_edge * 1.01, 330.0)["saturated"]))
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
