"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    A, dt = L.AREA, L.DT
    # --- unit hydrograph
    Tp = 0.25 + 0.6 * 2.0
    Qp = 0.208 * A / Tp
    checks.append((f"worked example: UH for A = 12 km2, Tc = 2 h, D = 0.5 h has Tp = 1.45 h and Qp = 1.72 m3/s (got {Tp:.2f}, {Qp:.2f})",
                   abs(Tp - 1.45) < 1e-12 and abs(Qp - 1.72) < 0.005))
    raw = L.triangular_uh(A, 2.0, normalize=False)
    checks.append((f"the unit hydrograph holds 1 mm: raw sampled volume {L.uh_volume_mm(raw, A):.4f} mm (within 0.5 percent)",
                   abs(L.uh_volume_mm(raw, A) - 1.0) < 0.005))
    u = L.triangular_uh(A, 2.0)
    checks.append(("normalised UH holds exactly 1 mm = 12 000 m3 over 12 km2",
                   abs(L.uh_volume_mm(u, A) - 1.0) < 1e-12 and abs(u.sum() * dt * 3600 - 12000.0) < 1e-6))
    checks.append(("0.208 follows from the triangle: 1000 / (0.5 * 2.67 * 3600) = 0.208",
                   abs(1000.0 / (0.5 * 2.67 * 3600.0) - 0.208) < 5e-4))
    # --- excess rain and convolution
    t0, q0, pe0 = L.flood(L.STORM, L.CN_PRE, L.TC_PRE)
    t1, q1, pe1 = L.flood(L.STORM, L.CN_POST, L.TC_POST)
    checks.append(("storm of 90 mm: effective rain is 26.3 mm at CN 70 and 63.2 mm at CN 90",
                   abs(L.STORM.sum() - 90.0) < 1e-12 and abs(pe0.sum() - 26.3) < 0.05 and abs(pe1.sum() - 63.2) < 0.05))
    checks.append(("at CN 70 the first hour of rain (12 mm) is all absorbed (Ia = 21.8 mm)",
                   pe0[0] == 0.0 and pe0[1] == 0.0 and abs(0.2 * (25400 / 70 - 254) - 21.77) < 0.01))
    checks.append(("effective rain never exceeds rain and is never negative",
                   bool(np.all(pe0 >= 0) and np.all(pe0 <= L.STORM + 1e-12) and np.all(pe1 >= 0))))
    qm = L.convolve_manual(pe0, L.triangular_uh(A, L.TC_PRE))
    checks.append(("convolution by two loops equals np.convolve", np.allclose(qm, q0, atol=1e-9)))
    checks.append(("hydrograph volume equals effective rain times area (mass kept)",
                   abs(q0.sum() * dt * 3600 - pe0.sum() * A * 1000) < 1e-6 * pe0.sum() * A * 1000
                   and abs(q1.sum() * dt * 3600 - pe1.sum() * A * 1000) < 1e-6 * pe1.sum() * A * 1000))
    pk0, tp0 = L.peak_and_time(t0, q0)
    pk1, tp1 = L.peak_and_time(t1, q1)
    checks.append((f"before urbanisation: peak 32.3 m3/s at 4.0 h (got {pk0:.1f} at {tp0:.1f})",
                   abs(pk0 - 32.3) < 0.05 and abs(tp0 - 4.0) < 1e-9))
    checks.append((f"after urbanisation: peak 94.6 m3/s at 3.0 h, 2.9 times higher and 1 h earlier (got {pk1:.1f} at {tp1:.1f}, ratio {pk1 / pk0:.2f})",
                   abs(pk1 - 94.6) < 0.05 and abs(tp1 - 3.0) < 1e-9 and abs(pk1 / pk0 - 2.93) < 0.01))
    pkc = L.peak_and_time(*L.flood(L.STORM, L.CN_POST, L.TC_PRE)[:2])
    pkt = L.peak_and_time(*L.flood(L.STORM, L.CN_PRE, L.TC_POST)[:2])
    checks.append((f"CN alone gives 76.0 m3/s at 3.5 h; a faster Tc alone gives 39.3 m3/s at 3.0 h (got {pkc[0]:.1f} at {pkc[1]:.1f}; {pkt[0]:.1f} at {pkt[1]:.1f})",
                   abs(pkc[0] - 76.0) < 0.05 and abs(pkc[1] - 3.5) < 1e-9 and abs(pkt[0] - 39.3) < 0.05 and abs(pkt[1] - 3.0) < 1e-9))
    checks.append(("lag to peak shortens from Tp = 1.45 h to 0.97 h when Tc falls from 2.0 to 1.2 h",
                   abs((0.25 + 0.6 * 2.0) - 1.45) < 1e-12 and abs((0.25 + 0.6 * 1.2) - 0.97) < 1e-12))
    # --- limits and failure cases
    cn3 = 23 * 70 / (10 + 0.13 * 70)
    p3 = L.flood(L.STORM, cn3, L.TC_PRE)
    checks.append((f"saturated soil: CN 70 becomes about 84.3, effective rain 50.7 mm and peak 61.4 m3/s, 1.9 times dry (got {cn3:.1f}, {p3[2].sum():.1f}, {p3[1].max():.1f})",
                   abs(cn3 - 84.3) < 0.05 and abs(p3[2].sum() - 50.7) < 0.05 and abs(p3[1].max() - 61.4) < 0.05 and abs(p3[1].max() / pk0 - 1.90) < 0.01))
    window = max(L.STORM[k:k + 4].sum() for k in range(5))
    rational = (pe0.sum() / L.STORM.sum()) * (window / 2.0) * A / 3.6
    checks.append((f"rational cross-check (C = 0.292, i = 34 mm/h over Tc = 2 h): 33.1 m3/s, within 3 percent of the UH peak (got {rational:.1f})",
                   window == 68.0 and abs(rational - 33.1) < 0.05 and abs(rational - pk0) / pk0 < 0.03))
    # --- Muskingum
    padded = np.concatenate([q0, np.zeros(30)])
    out, (c0, c1, c2) = L.muskingum(padded, 1.5, 0.1)
    checks.append(("Muskingum K = 1.5 h, X = 0.1: C0, C1, C2 = 0.0625, 0.25, 0.6875, and they add to 1",
                   np.allclose([c0, c1, c2], [0.0625, 0.25, 0.6875], atol=1e-4) and abs(c0 + c1 + c2 - 1) < 1e-12))
    checks.append((f"routing flattens and delays: peak 32.3 falls to 23.7 m3/s and moves from 4.0 h to 5.0 h (got {out.max():.1f} at {out.argmax() * dt:.1f})",
                   abs(out.max() - 23.7) < 0.05 and abs(out.argmax() * dt - 5.0) < 1e-9 and out.max() < padded.max()))
    checks.append(("routing keeps the water (volume within 0.01 percent) and stays non-negative",
                   abs(out.sum() - padded.sum()) / padded.sum() < 1e-4 and out.min() >= -1e-12))
    pulse = np.array([0, 0, 5, 10, 5, 0, 0, 0.0])
    o2, cc = L.muskingum(pulse, 1.0, 0.5, dt=1.0)
    checks.append(("limit X = 0.5 with dt = K: pure delay by one step, no flattening",
                   np.allclose(cc, [0.0, 1.0, 0.0]) and np.allclose(o2[1:], pulse[:-1])))
    # --- pond
    H = 2.0
    Ap = L.size_pond(q1, dt, pk0, H)
    tp, qo, hh, left = L.route_pond(q1, dt, Ap, H, pk0)
    checks.append((f"worked example: pond for the urbanised flood needs about 454 thousand m3 (226 857 m2 at 2 m); got {Ap * H:,.0f} m3",
                   abs(Ap * H - 453714) < 200 and abs(Ap - 226857) < 100))
    checks.append((f"with that pond the outflow peak equals the old peak, 32.3 m3/s, and the stage reaches 2.0 m (got {qo.max():.1f}, {hh.max():.2f})",
                   abs(qo.max() - pk0) < 0.05 and abs(hh.max() - H) < 1e-3))
    checks.append((f"pond peak outflow comes at 4.5 h, 1.5 h after the inflow peak (got {tp[qo.argmax()]:.1f} h)",
                   abs(tp[qo.argmax()] - 4.5) < 1e-9))
    vin = q1.sum() * dt * 3600
    vout = (qo.sum() - 0.5 * (qo[0] + qo[-1])) * dt * 3600
    checks.append(("water balance of the pond: inflow = outflow + water left (within 0.1 percent)",
                   abs(vin - vout - left) / vin < 1e-3))
    h_half = L.route_pond(q1, dt, 0.5 * Ap, H, pk0)
    checks.append((f"half the volume overtops: stage 3.31 m and outflow peak 41.5 m3/s (got {h_half[2].max():.2f}, {h_half[1].max():.1f})",
                   abs(h_half[2].max() - 3.31) < 0.01 and abs(h_half[1].max() - 41.5) < 0.1 and h_half[2].max() > H))
    ap1 = L.size_pond(q1, dt, pk0, 1.0)
    ap3 = L.size_pond(q1, dt, pk0, 3.0)
    checks.append(("the volume does not depend on the chosen depth (1 m, 2 m, 3 m give the same volume within 0.1 percent)",
                   abs(ap1 * 1.0 - Ap * H) / (Ap * H) < 1e-3 and abs(ap3 * 3.0 - Ap * H) / (Ap * H) < 1e-3))
    extra = (pe1.sum() - pe0.sum()) * A * 1000
    checks.append((f"the extra run-off of urbanisation is 443 thousand m3; the pond (454 thousand) is slightly larger (got {extra:,.0f})",
                   abs(extra - 443052) < 100 and Ap * H > extra))
    # drain test against the analytic solution sqrt(h) = sqrt(h0) - c t / (2 Ap)
    Ap2, h0 = 1.0e5, 1.5
    c = pk0 / math.sqrt(H)
    r = L.route_pond(np.zeros(3), dt, Ap2, H, pk0, t_end_h=3.0, h0=h0)
    ex = (math.sqrt(h0) - c * r[0][2] * 3600 / (2 * Ap2)) ** 2
    checks.append((f"pond emptying with no inflow matches the exact formula (got {r[2][2]:.4f} m, exact {ex:.4f} m)",
                   abs(r[2][2] - ex) < 1e-6))
    qa = 0.208 * 8.0 / (0.25 + 0.6 * 1.5)
    checks.append((f"UH for A = 8 km2, Tc = 1.5 h: Tp = 1.15 h and Qp = 1.45 m3/s (got {qa:.2f})", abs(qa - 1.447) < 0.001))
    checks.append((f"a 1 m deep pond needs about 454 thousand m2 (45 ha), got {ap1:,.0f} m2", abs(ap1 - 453714) < 500))
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
