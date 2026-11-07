"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    gen = dict(turns=250, b_field=0.2, area=0.0016, freq=50.0, ra=2.0, rl=10.0, ind=0.03)
    ss = L.steady_state(**gen)
    sim = L.simulate_generator(**gen)
    z_hand = np.sqrt(12.0 ** 2 + (2 * np.pi * 50 * 0.03) ** 2)
    checks.append((f"worked example: Z = 15.26 ohm, I_rms = 1.165 A, load power = 13.57 W (got {ss['z']:.2f}, {ss['i_rms']:.3f}, {ss['p_load']:.2f})",
                   abs(ss["z"] - z_hand) < 1e-9 and abs(ss["z"] - 15.26) < 0.01 and abs(ss["i_rms"] - 1.1647) < 1e-3 and abs(ss["p_load"] - 13.565) < 0.01))
    checks.append(("RK4 load power matches the exact steady state within 0.01 percent", abs(sim["p_load"] / ss["p_load"] - 1) < 1e-4))
    checks.append(("RK4 RMS current matches the exact steady state within 0.01 percent", abs(sim["i_rms"] / ss["i_rms"] - 1) < 1e-4))
    checks.append(("energy: mechanical work in = load energy + coil heat + change in stored energy",
                   abs(L.energy_balance(sim)) < 1e-6 * sim["w_mech"]))
    checks.append(("mechanical power = load power + coil heat power", abs(sim["p_mech"] - sim["p_load"] - sim["p_arm"]) < 1e-4))
    checks.append(("Lenz: the magnetic torque on the coil opposes the rotation on average", sim["torque"][-1600:].mean() < 0))
    k = 250 * 0.2 * 0.0016
    pw = sim["torque"] * sim["omega"]
    em = k * sim["omega"] * np.sin(sim["omega"] * sim["t"])
    checks.append(("magnetic power on the coil is exactly minus e times i at every instant",
                   float(np.abs(pw + em * sim["i"]).max()) < 1e-9))
    tiny = L.steady_state(250, 0.2, 0.0016, 50.0, 2.0, 10.0, 1e-9)
    hand = (tiny["em"] / 12.0) ** 2 / 2 * 10.0
    checks.append(("limit L -> 0: power is (Em / (Ra + RL))^2 / 2 * RL", abs(tiny["p_load"] - hand) < 1e-6))
    big = L.steady_state(250, 0.2, 0.0016, 50.0, 2.0, 10.0, 3.0)
    checks.append(("a large inductance cuts the current", big["i_rms"] < 0.1 * ss["i_rms"]))

    r = L.transformer_load(6.0)
    checks.append(("worked example: transformer at 6 ohm: V2 about 11.7 V, efficiency about 91.5 percent, regulation about 2.6 percent",
                   abs(r["v2"] - 11.68) < 0.02 and abs(r["eff"] - 0.915) < 0.002 and abs(r["regulation"] - 0.026) < 0.002))
    checks.append(("transformer power balance: P_in = P_out + copper + core",
                   abs(r["p_in"] - r["p_out"] - r["p_cu"] - r["p_core"]) < 1e-9))
    checks.append(("no load: output voltage is V1 / a and output power is tiny",
                   abs(L.transformer_load(1e9)["v2"] - 230.0 * 24 / 460) < 0.01 and L.transformer_load(1e9)["p_out"] < 1e-3))
    loads = np.logspace(np.log10(0.7), np.log10(500), 400)
    effs = np.array([L.transformer_load(x)["eff"] for x in loads])
    best = loads[int(np.argmax(effs))]
    rb = L.transformer_load(best)
    checks.append(("efficiency is best where copper loss is close to core loss", abs(rb["p_cu"] / rb["p_core"] - 1) < 0.1))
    regs = [L.transformer_load(x)["regulation"] for x in (50.0, 12.0, 6.0, 3.0)]
    checks.append(("regulation grows as the load grows", bool(np.all(np.diff(regs) > 0))))

    lo = L.saturating_core(0.5)
    hi = L.saturating_core(2.5)
    lam_pk = 0.5 * 12 * np.sqrt(2) / (2 * np.pi * 50)
    i_lin = lam_pk / (0.108 / 0.05)
    checks.append(("small drive: magnetising current matches the linear value lambda / L within 5 percent",
                   abs(abs(lo["i"][3 * lo["steps"]:]).max() / i_lin - 1) < 0.05))
    checks.append(("small drive: secondary voltage is a clean sine (THD below 0.1 percent)", L.thd(lo["v_wind"], lo["steps"], lo["periods"]) < 1e-3))
    checks.append(("saturation: current spikes more than 100 times and the output THD exceeds 10 percent",
                   abs(hi["i"][3 * hi["steps"]:]).max() > 100 * abs(lo["i"][3 * lo["steps"]:]).max() and L.thd(hi["v_wind"], hi["steps"], hi["periods"]) > 0.10))

    p15, p25 = L.dynamo_power(310, 15), L.dynamo_power(310, 25)
    checks.append((f"dynamo N = 310: at least 3 W at 15 km/h and at most 4.5 W at 25 km/h (got {p15:.2f} and {p25:.2f})", p15 >= 3.0 and p25 <= 4.5))
    checks.append(("dynamo N = 300 is too weak and N = 330 over-drives the lamp at 25 km/h",
                   L.dynamo_power(300, 15) < 3.0 and L.dynamo_power(330, 25) > 4.5))
    checks.append(("dynamo power grows more slowly than speed squared (self-limiting)",
                   L.dynamo_power(310, 25) / L.dynamo_power(310, 15) < (25 / 15) ** 2))
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
