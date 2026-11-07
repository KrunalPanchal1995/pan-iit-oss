"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("momentum of 1000 kg at 10 m/s is 10000 kg m/s", abs(L.momentum(1000.0, 10.0) - 1.0e4) < 1e-9))
    checks.append(("hand calculation: stopping 10000 kg m/s in 0.1 s needs 100 kN",
                   abs(L.force_from_time(1000.0, 10.0, 0.1) - 1.0e5) < 1e-6))
    v = L.kmh_to_ms(50.0)
    f_t = L.force_from_time(1000.0, v, L.stop_time(v, 0.5))
    f_d = L.force_from_distance(1000.0, v, 0.5)
    checks.append(("impulse view and energy view give the same force", abs(f_t - f_d) < 1e-6))
    checks.append(("a = v^2 / (2 d) equals F / m", abs(L.avg_decel(v, 0.5) - f_d / 1000.0) < 1e-9))
    d50 = L.distance_for_g(v, 20.0)
    checks.append((f"worked example: 50 km/h and 20 g need d = {d50:.3f} m (0.492 m)", abs(d50 - 0.4917) < 5e-4))
    checks.append(("with that distance the deceleration is exactly 20 g",
                   abs(L.g_force(L.avg_decel(v, d50)) - 20.0) < 1e-9))
    d100 = L.distance_for_g(L.kmh_to_ms(100.0), 20.0)
    checks.append((f"square law: 100 km/h needs 4 times the distance ({d100:.3f} m)", abs(d100 / d50 - 4.0) < 1e-9))
    checks.append(("max_speed_for_g inverts distance_for_g",
                   abs(L.max_speed_for_g(d50, 20.0) - v) < 1e-9))
    checks.append(("stop time for 50 km/h in 0.4917 m is about 70.8 ms",
                   abs(L.stop_time(v, d50) - 0.0708) < 5e-4))
    # second worked example: a 12000 kg lorry with the same speed and crumple distance
    m_l = 12000.0
    t_l = L.stop_time(v, d50)
    f_lt = L.force_from_time(m_l, v, t_l)
    f_ld = L.force_from_distance(m_l, v, d50)
    checks.append((f"lorry example: 12000 kg at 50 km/h in 0.4917 m feels {L.g_force(L.avg_decel(v, d50)):.1f} g for {t_l * 1000:.1f} ms, like the car",
                   abs(L.g_force(L.avg_decel(v, d50)) - 20.0) < 1e-9 and abs(t_l - 0.0708) < 5e-4))
    checks.append((f"lorry example: momentum {L.momentum(m_l, v):.0f} kg m/s and kinetic energy {L.kinetic_energy(m_l, v) / 1000:.0f} kJ",
                   abs(L.momentum(m_l, v) - 166667) < 1 and abs(L.kinetic_energy(m_l, v) / 1000 - 1157.4) < 0.1))
    checks.append((f"lorry example: impulse and energy both give {f_lt / 1000:.0f} kN, 12 times the car's force",
                   abs(f_lt - f_ld) < 1e-6 and abs(f_lt / 1000 - 2354.4) < 0.1
                   and abs(f_lt / L.force_from_distance(1000.0, v, d50) - 12.0) < 1e-9))
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
