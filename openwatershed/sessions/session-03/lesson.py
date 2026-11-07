"""Session 3 (Level 3): the unit hydrograph, routing, urbanisation and a detention pond.

Educational model only. Real flood studies use gauged data, official rainfall and a qualified hydrologist.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: building the flood hydrograph
# **A. Real-world problem.** A stream gauge does not show one peak number, it shows a curve of
# flow against time: the *hydrograph*. A storm has several bursts, and each burst makes its own
# small flood; the river carries the sum. Then a developer paves part of the valley. How much
# higher and earlier is the new peak, and how big a pond keeps it at the old value?
#
# **Plan.** (1) excess rain from the curve number, (2) a triangular unit hydrograph (UH),
# (3) convolution of burst by burst, (4) Muskingum channel routing, (5) a detention pond by
# level-pool routing, (6) the story of urbanisation.
#
# *Educational model.* Real flood design belongs to qualified hydrologists and official agencies.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

DT = 0.5                                                          # time step and burst length (h)
STORM = np.array([4.0, 8.0, 14.0, 26.0, 18.0, 10.0, 6.0, 4.0])    # rain per 0.5 h burst (mm), total 90 mm
AREA = 12.0                                                       # km2, a made-up catchment
CN_PRE, TC_PRE = 70.0, 2.0                                        # before development: curve number, Tc (h)
CN_POST, TC_POST = 90.0, 1.2                                      # after: paved and smoother, so faster


# %% [markdown]
# ## Step 1: excess rain for each burst
# The SCS run-off (Session 2) is applied to the *cumulative* rain, and each burst gets the extra
# run-off it adds. Early bursts mostly fill the ground (Ia), later ones run off more.

# %%
def scs_runoff(P, CN):
    """Run-off depth (mm) from rain depth P (mm), curve number CN (S = 25400/CN - 254, Ia = 0.2 S)."""
    S = 25400.0 / CN - 254.0
    x = np.asarray(P, dtype=float) - 0.2 * S
    pos = np.where(x > 0, x, 0.0)
    return np.where(x > 0, pos ** 2 / (pos + S), 0.0)


def excess_rain(pulses, CN):
    """Effective rain per burst (mm): differences of the run-off of the cumulative rain."""
    cum = np.concatenate([[0.0], np.cumsum(pulses)])
    return np.diff(scs_runoff(cum, CN))


# %% [markdown]
# ## Step 2: the triangular unit hydrograph
# The *unit hydrograph* is the river's response to 1 mm of effective rain over the whole
# catchment during one burst of length D. The SCS triangular form (standard, approximate):
#
#     Tp = D/2 + 0.6 Tc            time to peak (h)
#     Qp = 0.208 * A * Pe / Tp     peak (m3/s), A in km2, Pe = 1 mm, Tp in h
#     base time = 2.67 Tp
#
# Check of the 0.208: the area under the triangle is 0.5 * Qp * 2.67 Tp * 3600 s. For that to
# equal 1 mm over A km2, i.e. 1000 * A m3, we need Qp = 1000 A / (0.5 * 2.67 * 3600 Tp) =
# 0.208 A / Tp. The UH keeps the water: its volume is 1 mm over the catchment.

# %%
def triangular_uh(A, Tc, D=DT, dt=DT, normalize=True):
    """Ordinates (m3/s) at times 0, dt, 2dt, ... of the unit hydrograph for 1 mm of effective rain."""
    Tp = D / 2.0 + 0.6 * Tc
    Qp = 0.208 * A / Tp
    tb = 2.67 * Tp
    t = np.arange(0.0, tb + dt, dt)
    u = np.where(t <= Tp, Qp * t / Tp, np.maximum(Qp * (tb - t) / (tb - Tp), 0.0))
    if normalize:                                # make the sampled volume exactly 1 mm over A
        u = u * (1000.0 * A) / (u.sum() * dt * 3600.0)
    return u


def uh_volume_mm(u, A, dt=DT):
    """Depth (mm) of water under the unit hydrograph spread over the catchment (should be 1)."""
    return u.sum() * dt * 3600.0 / (A * 1000.0)


# %% [markdown]
# ## Step 3: convolution = add up the small floods
# Burst k with effective rain Pe[k] produces Pe[k] times the UH, starting at time k*dt. The river
# flow at step n is the sum over bursts: Q[n] = sum_k Pe[k] * U[n - k]. That is a
# *discrete convolution*; `np.convolve` does exactly this.

# %%
def convolve_manual(pe, u):
    """Q[n] = sum_k pe[k] * u[n-k] written as two plain loops."""
    q = np.zeros(len(pe) + len(u) - 1)
    for k, p in enumerate(pe):
        for j, uj in enumerate(u):
            q[k + j] += p * uj
    return q


def flood(pulses=STORM, CN=CN_PRE, Tc=TC_PRE, A=AREA, dt=DT):
    """Hydrograph of the whole storm. Returns (t in h, Q in m3/s, effective rain per burst)."""
    pe = excess_rain(pulses, CN)
    q = np.convolve(pe, triangular_uh(A, Tc, dt, dt))
    return np.arange(len(q)) * dt, q, pe


def peak_and_time(t, q):
    j = int(np.argmax(q))
    return float(q[j]), float(t[j])


# %% [markdown]
# ## Step 4: Muskingum channel routing
# A flood wave travelling down a river is delayed and flattened. Muskingum routing:
#
#     O[n+1] = C0 I[n+1] + C1 I[n] + C2 O[n]
#     C0 = (-K X + dt/2) / D1,  C1 = (K X + dt/2) / D1,  C2 = (K (1-X) - dt/2) / D1,
#     D1 = K (1-X) + dt/2         (so C0 + C1 + C2 = 1)
#
# I = inflow, O = outflow (m3/s), K = travel time of the reach (h), X = weighting 0..0.5
# (0 = most flattening, 0.5 = pure delay). Keep dt between 2KX and 2K(1-X) so all C are >= 0.

# %%
def muskingum(inflow, K, X, dt=DT):
    """Route an inflow series through a reach. Returns (outflow, (C0, C1, C2))."""
    d1 = K * (1.0 - X) + dt / 2.0
    c0, c1, c2 = (-K * X + dt / 2.0) / d1, (K * X + dt / 2.0) / d1, (K * (1.0 - X) - dt / 2.0) / d1
    out = np.zeros(len(inflow))
    out[0] = inflow[0]
    for n in range(len(inflow) - 1):
        out[n + 1] = c0 * inflow[n + 1] + c1 * inflow[n] + c2 * out[n]
    return out, (c0, c1, c2)


# %% [markdown]
# ## Step 5: a detention pond (level-pool routing)
# A pond with vertical walls of surface area Ap (m2) and an orifice at the bottom.
# Water balance: Ap dh/dt = I(t) - O(h). The orifice law (simplified): O = c sqrt(h), with c
# chosen so that O = Qmax at the full depth H. Find the smallest Ap that keeps the stage below
# H, then the volume is Ap * H. We step with RK4 and interpolate the inflow linearly.

# %%
def route_pond(inflow, dt_h, Ap, H, Qmax, sub=40, t_end_h=None, h0=0.0):
    """Level-pool routing from initial stage h0 (m). Returns (t in h, outflow m3/s, stage in m, stored volume left in m3)."""
    c = Qmax / np.sqrt(H)
    n_in = len(inflow)
    t_end = t_end_h if t_end_h is not None else (n_in - 1) * dt_h + 12.0
    n = int(round(t_end / dt_h))
    I = np.concatenate([inflow, np.zeros(max(n + 2 - n_in, 0))])
    h = h0
    hs, outs = [h0], [c * np.sqrt(h0)]
    hsub = dt_h * 3600.0 / sub

    def rhs(hh, i_now):
        return (i_now - c * np.sqrt(max(hh, 0.0))) / Ap

    for k in range(n):
        for s in range(sub):
            i0 = I[k] + (I[k + 1] - I[k]) * s / sub
            im = I[k] + (I[k + 1] - I[k]) * (s + 0.5) / sub
            i1 = I[k] + (I[k + 1] - I[k]) * (s + 1) / sub
            k1 = rhs(h, i0)
            k2 = rhs(h + 0.5 * hsub * k1, im)
            k3 = rhs(h + 0.5 * hsub * k2, im)
            k4 = rhs(h + hsub * k3, i1)
            h = max(h + hsub * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0, 0.0)
        hs.append(h)
        outs.append(c * np.sqrt(h))
    return np.arange(n + 1) * dt_h, np.array(outs), np.array(hs), Ap * h


def size_pond(inflow, dt_h, Qtarget, H, lo=1.0e3, hi=1.0e7, iters=45):
    """Smallest surface area (m2) for which the stage just reaches H, so the outflow peak is Qtarget."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if route_pond(inflow, dt_h, mid, H, Qtarget)[2].max() > H:
            lo = mid        # pond too small: water would overtop
        else:
            hi = mid
    return hi


# %% [markdown]
# ## Step 6: run the story

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    t, q0, pe0 = flood(STORM, CN_PRE, TC_PRE)
    t1, q1, pe1 = flood(STORM, CN_POST, TC_POST)
    pk0, tp0 = peak_and_time(t, q0)
    pk1, tp1 = peak_and_time(t1, q1)
    print(f"before: effective rain {pe0.sum():.1f} mm, peak {pk0:.1f} m3/s at {tp0:.1f} h")
    print(f"after : effective rain {pe1.sum():.1f} mm, peak {pk1:.1f} m3/s at {tp1:.1f} h")

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 6), sharex=True, gridspec_kw={"height_ratios": [1, 2]})
    tb = np.arange(len(STORM)) * DT
    a1.bar(tb, STORM, width=DT, align="edge", color="lightsteelblue", label="rain")
    a1.bar(tb, pe0, width=DT, align="edge", color="tab:blue", label="effective rain, CN 70")
    a1.invert_yaxis()
    a1.set_ylabel("rain per 0.5 h (mm)")
    a1.legend(fontsize=8)
    uh = triangular_uh(AREA, TC_PRE)
    for k, p in enumerate(pe0):
        a2.plot(np.arange(len(uh)) * DT + k * DT, p * uh, color="0.7", lw=0.8)
    a2.plot(t, q0, color="tab:blue", lw=2, label=f"sum of bursts: peak {pk0:.1f} m3/s at {tp0:.1f} h")
    a2.set_xlabel("time since the storm began (h)")
    a2.set_ylabel("river flow (m3/s)")
    a2.legend()
    a1.set_title("Each burst makes a small flood; the river adds them")
    for a in (a1, a2):
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "convolution.png", dpi=120)

    H = 2.0
    Ap = size_pond(q1, DT, pk0, H)
    tp, qo, hh, left = route_pond(q1, DT, Ap, H, pk0)
    print(f"pond: area {Ap:,.0f} m2, depth {H} m, volume {Ap * H:,.0f} m3, outflow peak {qo.max():.1f} m3/s")
    fig2, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(t, q0, color="tab:blue", label=f"before: {pk0:.1f} m3/s")
    ax.plot(t1, q1, color="tab:red", label=f"after urbanisation: {pk1:.1f} m3/s")
    ax.plot(tp, qo, color="tab:green", lw=2, label=f"after, with pond: {qo.max():.1f} m3/s")
    ax.set_xlim(0, 12)
    ax.set_xlabel("time since the storm began (h)")
    ax.set_ylabel("river flow (m3/s)")
    ax.set_title("Urbanisation raises the peak; a detention pond brings it back")
    ax.grid(alpha=0.3)
    ax.legend()
    fig2.tight_layout()
    fig2.savefig(OUT / "urban_and_pond.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
