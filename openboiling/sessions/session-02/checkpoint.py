"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    q_heat = L.energy_to_heat(1.7, 20.0)
    checks.append(("worked example: heating 1.7 kg from 20 C to 100 C takes 569.3 kJ", abs(q_heat - 569296.0) < 1.0))
    p = L.power_for_time(1.7, 240.0)
    checks.append(("worked example: 4 minutes needs about 2791 W of electrical power", abs(p - 2790.7) < 0.5))
    d = L.design_heater(1.7, 240.0, 0.01)
    checks.append(("worked example: on 100 cm2 the flux is 237 kW/m2 and the superheat 18.0 K",
                   abs(d["flux"] - 237207.0) < 5.0 and abs(d["superheat_k"] - 17.99) < 0.01))
    checks.append(("the safety factor on the CHF is about 4.6", abs(d["chf_margin"] - 4.64) < 0.01))
    checks.append(("latent heat of 0.1 kg is 225.7 kJ, far more than 10 K of warming",
                   abs(L.energy_to_vaporise(0.1) - 225700.0) < 1.0 and L.energy_to_vaporise(0.1) > L.energy_to_heat(0.1, 90.0)))
    checks.append(("round trip: heating_time(power_for_time(t)) = t", abs(L.heating_time(L.power_for_time(1.7, 240.0), 1.7) - 240.0) < 1e-9))
    checks.append(("doubling the power halves the heating time", abs(L.heating_time(2000.0, 1.0) * 0.5 - L.heating_time(4000.0, 1.0)) < 1e-9))
    q = 3.0e5
    checks.append(("inverse of the cubic law: nucleate_flux(superheat_from_flux(q)) = q",
                   abs(L.nucleate_flux(L.superheat_from_flux(q)) - q) < 1e-6 * q))
    ratio = L.nucleate_flux(20.0) / L.nucleate_flux(10.0)
    checks.append(("scaling: doubling the superheat multiplies the flux by 2^3 = 8", abs(ratio - 8.0) < 1e-9))
    rr = L.rohsenow_flux(20.0) / L.rohsenow_flux(10.0)
    checks.append(("the Rohsenow-type flux also scales as dT cubed", abs(rr - 8.0) < 1e-9))
    checks.append(("h grows with flux: h = q/dT = C dT^2 (4 times larger at twice the superheat)",
                   abs(L.heat_transfer_coeff(L.nucleate_flux(20.0)) / L.heat_transfer_coeff(L.nucleate_flux(10.0)) - 4.0) < 1e-9))
    chf = L.chf_zuber()
    checks.append(("Zuber critical heat flux of water at 1 atm is about 1.1 MW/m2", 1.0e6 < chf < 1.2e6))
    checks.append(("capillary length of water at 100 C is about 2.5 mm", abs(L.capillary_length() - 2.504e-3) < 5e-6))
    checks.append(("Fritz departure diameter at 45 degrees is 2.34 mm", abs(L.departure_diameter(45.0) - 2.34e-3) < 1e-5))
    checks.append(("departure diameter is proportional to the contact angle", abs(L.departure_diameter(60.0) / L.departure_diameter(30.0) - 2.0) < 1e-12))
    a3 = L.min_area_for_margin(p, 3.0)
    checks.append(("a safety factor of 3 needs at least 64.7 cm2", abs(a3 * 1e4 - 64.7) < 0.1))
    checks.append(("a smaller area than that gives a margin below 3", L.design_heater(1.7, 240.0, 0.9 * a3)["chf_margin"] < 3.0))
    checks.append(("edge: at the CHF flux the cubic law gives 30 K", abs(L.superheat_from_flux(1.1e6) - 30.0) < 1e-9))
    checks.append(("edge: zero flux gives zero superheat", L.superheat_from_flux(0.0) == 0.0))
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
