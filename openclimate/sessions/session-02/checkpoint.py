"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    te = L.bare_temperature()
    checks.append(("limit: eps = 0 (transparent air) gives back the Session 1 answer 254.6 K",
                   abs(L.surface_temperature(0.0) - te) < 1e-9 and abs(te - 254.58) < 0.05))
    checks.append(("limit: eps = 1 gives Ts = 2^(1/4) Te = 302.7 K",
                   abs(L.surface_temperature(1.0) - 2 ** 0.25 * te) < 1e-9 and abs(L.surface_temperature(1.0) - 302.7) < 0.1))
    eps = L.eps_for_surface(288.0)
    checks.append((f"worked example: eps for 288 K is {eps:.3f} (hand value 0.779)", abs(eps - 0.779) < 0.001))
    checks.append(("round trip: surface_temperature(eps_for_surface(288)) = 288 K", abs(L.surface_temperature(eps) - 288.0) < 1e-9))
    checks.append(("worked example: layer temperature 288 / 2^(1/4) = 242.2 K", abs(L.layer_temperature(eps) - 242.2) < 0.05))
    f = L.fluxes(eps)
    checks.append(("worked example: ground 390.1, window 86.2, layer up 151.9, back-radiation 151.9 W/m2",
                   abs(f["ground"] - 390.1) < 0.1 and abs(f["through_window"] - 86.2) < 0.1
                   and abs(f["layer_up"] - 151.9) < 0.1 and abs(f["back_radiation"] - 151.9) < 0.1))
    ok_bal = all(abs(L.fluxes(e)[k]) < 1e-9 for e in (0.0, 0.3, 0.779, 1.0)
                 for k in ("toa_residual", "layer_residual", "surface_residual"))
    checks.append(("energy conservation: top, layer and surface balances all close for eps = 0, 0.3, 0.779, 1", ok_bal))
    checks.append(("outgoing infrared equals absorbed sunlight (238.2 W/m2)", abs(f["olr"] - 238.175) < 1e-9))
    ts = [L.surface_temperature(e) for e in np.linspace(0, 1, 21)]
    checks.append(("more absorption always means a warmer surface", all(b > a for a, b in zip(ts, ts[1:]))))
    checks.append(("the layer is always colder than the surface", all(L.layer_temperature(e) < L.surface_temperature(e) for e in (0.1, 0.5, 1.0))))
    checks.append(("N opaque layers: N = 1 matches the one-layer model at eps = 1",
                   abs(L.n_layer_surface_temperature(1) - L.surface_temperature(1.0)) < 1e-9))
    checks.append(("N opaque layers: Ts = Te (N + 1)^(1/4), so N = 15 doubles Te",
                   abs(L.n_layer_surface_temperature(15) / te - 2.0) < 1e-12))
    nv = L.layers_needed(737.0, 2601.0, 0.77)
    checks.append((f"Venus needs about {nv:.0f} opaque layers (between 80 and 140)", 80 < nv < 140))
    fo = L.instant_forcing(eps, eps + 0.019)
    checks.append((f"forcing: d(eps) = 0.019 removes {fo:.2f} W/m2 of outgoing infrared (about the 3.7 W/m2 of doubled CO2)",
                   abs(fo - 3.71) < 0.05))
    checks.append(("forcing is zero when eps does not change", L.instant_forcing(eps, eps) == 0.0))
    bad = 0
    for call in (lambda: L.surface_temperature(1.5), lambda: L.eps_for_surface(400.0), lambda: L.n_layer_surface_temperature(-1)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
