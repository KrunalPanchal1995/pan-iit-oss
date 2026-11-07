"""The Target, rebuilt: Otto, Diesel and Carnot side by side, with live P-V and T-S loops.

    python target/target.py --check      print the final efficiencies and the checks (PASS or FAIL)
    python target/target.py              also write the animation to docs/figures/target_reproduction.gif

Method (see target/README.md): every cycle is a chain of simple processes of an ideal gas.
Each process is sampled finely; the work so far is the running sum of P dv, the entropy is
s = cv ln(T / T1) + R ln(v / v1). Same heat in (1100 kJ/kg) for all three engines.
"""
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
GIF = ROOT / "docs" / "figures" / "target_reproduction.gif"

# Air with the usual textbook table values at 300 K (cp, cv in kJ/(kg K)); R and gamma follow from them.
CP, CV = 1.005, 0.718
R = CP - CV                    # 0.287 kJ/(kg K)
G = CP / CV                    # 1.3997
T1, P1, Q_IN = 300.0, 100.0, 1100.0
V1 = R * T1 / P1               # m3/kg at state 1
N = 400                        # samples per process


# ---- one process = arrays of v (m3/kg) and T (K); P and s follow from the gas laws ----
def isentrope(v_a, t_a, v_b):
    v = np.geomspace(v_a, v_b, N)
    return v, t_a * (v_a / v) ** (G - 1.0)


def isochore(v, t_a, t_b):
    return np.full(N, v), np.linspace(t_a, t_b, N)


def isobar(v_a, t_a, v_b):
    v = np.linspace(v_a, v_b, N)
    return v, t_a * v / v_a


def isotherm(v_a, t, v_b):
    return np.geomspace(v_a, v_b, N), np.full(N, t)


def otto(r=9.0, q=Q_IN):
    v2 = V1 / r
    t2 = T1 * r ** (G - 1.0)
    t3 = t2 + q / CV
    t4 = t3 / r ** (G - 1.0)
    return [isentrope(V1, T1, v2), isochore(v2, t2, t3), isentrope(v2, t3, V1), isochore(V1, t4, T1)]


def diesel(r=18.0, q=Q_IN):
    v2 = V1 / r
    t2 = T1 * r ** (G - 1.0)
    t3 = t2 + q / CP
    v3 = v2 * t3 / t2
    t4 = t3 * (v3 / V1) ** (G - 1.0)
    return [isentrope(V1, T1, v2), isobar(v2, t2, v3), isentrope(v3, t3, V1), isochore(V1, t4, T1)]


def carnot(t_hot, v_hot, q=Q_IN, t_cold=T1):
    """Carnot cycle that takes q at t_hot, starting from the hot, smallest-volume state (v_hot, t_hot)."""
    vb = v_hot * math.exp(q / (R * t_hot))                 # isothermal expansion takes in q
    k = (t_hot / t_cold) ** (1.0 / (G - 1.0))              # isentropic volume ratio between the two isotherms
    return [isotherm(v_hot, t_hot, vb), isentrope(vb, t_hot, vb * k), isotherm(vb * k, t_cold, v_hot * k),
            isentrope(v_hot * k, t_cold, v_hot)]


def trace(processes):
    """Join the processes into one closed path with P, s, the running work and the heat taken in."""
    v = np.concatenate([p[0] for p in processes])
    t = np.concatenate([p[1] for p in processes])
    p = R * t / v
    s = CV * np.log(t / T1) + R * np.log(v / V1)
    dw = 0.5 * (p[1:] + p[:-1]) * np.diff(v)               # P dv of each small step
    dq = 0.5 * (t[1:] + t[:-1]) * np.diff(s)               # T ds of each small step
    w_so_far = np.concatenate([[0.0], np.cumsum(dw)])
    q_in = float(np.sum(dq[dq > 0]))
    return {"v": v, "p": p, "t": t, "s": s, "w": w_so_far, "work": float(w_so_far[-1]),
            "q_in": q_in, "ts_area": float(np.sum(dq)), "eta": float(w_so_far[-1]) / Q_IN}


def target():
    """The three Target engines: Otto r = 9, Diesel r = 18, Carnot between Otto's peak temperature and 300 K."""
    o = otto()
    t_hot, v_hot = o[1][1][-1], o[1][0][-1]                # state 3 of the Otto cycle
    return {"Otto, r = 9": trace(o), "Diesel, r = 18": trace(diesel()), "Carnot": trace(carnot(t_hot, v_hot))}


def analytic():
    """Closed-form efficiencies with the same properties (Session 2 formulas)."""
    r_d = 18.0
    t2 = T1 * r_d ** (G - 1.0)
    rho = (t2 + Q_IN / CP) / t2
    t3_otto = T1 * 9.0 ** (G - 1.0) + Q_IN / CV
    return {"Otto, r = 9": 1.0 - 9.0 ** (1.0 - G),
            "Diesel, r = 18": 1.0 - r_d ** (1.0 - G) * (rho ** G - 1.0) / (G * (rho - 1.0)),
            "Carnot": 1.0 - T1 / t3_otto}


def checks():
    cyc, ana = target(), analytic()
    out = []
    for name, want in zip(cyc, (0.585, 0.624, 0.867)):
        c = cyc[name]
        out.append((f"{name}: end-of-cycle W/Qin = {c['eta']:.4f}, shown as {c['eta']:.3f} (Target {want})", f"{c['eta']:.3f}" == f"{want:.3f}"))
        out.append((f"{name}: P dv sum agrees with the closed form {ana[name]:.5f} within 1e-4", abs(c["eta"] - ana[name]) < 1e-4))
        out.append((f"{name}: heat taken in from T ds is 1100 kJ/kg within 0.5 percent ({c['q_in']:.1f})", abs(c["q_in"] - Q_IN) / Q_IN < 5e-3))
        out.append((f"{name}: T-S area equals P-V area within 0.5 percent", abs(c["ts_area"] - c["work"]) / c["work"] < 5e-3))
        out.append((f"{name}: the path is closed (back to state 1)", abs(c["v"][-1] - c["v"][0]) < 1e-9 and abs(c["t"][-1] - c["t"][0]) < 1e-6))
    e = [cyc[k]["eta"] for k in cyc]
    out.append(("order: Otto < Diesel < Carnot, as in the Target", e[0] < e[1] < e[2]))
    return out


# ---- animation ----
def animate(path=GIF, frames=60, hold=12):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import animation, cm, colors
    from matplotlib.ticker import NullFormatter

    cyc = target()
    names = list(cyc)
    titles = dict(zip(names, (names[0], names[1], f"Carnot, {cyc[names[2]]['t'].max():.0f} K and 300 K")))
    style = {names[0]: ("#0072B2", "-"), names[1]: ("#D55E00", "--"), names[2]: ("#009E73", ":")}   # Okabe-Ito + line styles
    tnorm = colors.Normalize(300, 2300)
    cmap = cm.get_cmap("inferno") if hasattr(cm, "get_cmap") else matplotlib.colormaps["inferno"]
    fig = plt.figure(figsize=(8.0, 7.6), dpi=72)
    fig.suptitle("Same heat in (1100 kJ/kg), three ideal cycles", fontsize=12)
    gs = fig.add_gridspec(4, 3, height_ratios=[1.0, 1.15, 1.15, 0.55], hspace=0.65, wspace=0.45)
    art = []
    for j, name in enumerate(names):
        c, (col, ls) = cyc[name], style[name]
        ax0 = fig.add_subplot(gs[0, j]); ax0.set_xlim(0, 1); ax0.set_ylim(0, 1); ax0.axis("off")
        ax0.set_title(titles[name], fontsize=10)
        ax0.plot([0.3, 0.3, 0.7, 0.7], [1.0, 0.05, 0.05, 1.0], color="0.3", lw=2)        # cylinder walls and head
        gas = ax0.add_patch(plt.Rectangle((0.3, 0.05), 0.4, 0.5, color=cmap(0.0)))
        piston, = ax0.plot([0.28, 0.72], [0.55, 0.55], color="0.2", lw=5)
        rod, = ax0.plot([0.5, 0.5], [0.55, 1.0], color="0.2", lw=3)
        lv = np.log(c["v"]); lv = (lv - lv.min()) / (lv.max() - lv.min())               # piston height: log volume
        ax1 = fig.add_subplot(gs[1, j]); ax1.set_xscale("log"); ax1.set_yscale("log")
        ax1.plot(c["v"], c["p"], color=col, ls=ls, lw=1, alpha=0.25)
        pv, = ax1.plot([], [], color=col, ls=ls, lw=2.2); d1, = ax1.plot([], [], "o", color="k", ms=5)
        ax1.xaxis.set_minor_formatter(NullFormatter()); ax1.yaxis.set_minor_formatter(NullFormatter())
        ax1.set_title("P-V (log scales)", fontsize=9); ax1.set_xlabel("v (m3/kg)", fontsize=8); ax1.set_ylabel("P (kPa)", fontsize=8)
        ax2 = fig.add_subplot(gs[2, j]); ax2.set_xlim(-0.05, 1.4); ax2.set_ylim(0, 2400)
        ax2.plot(c["s"], c["t"], color=col, ls=ls, lw=1, alpha=0.25)
        ts, = ax2.plot([], [], color=col, ls=ls, lw=2.2); d2, = ax2.plot([], [], "o", color="k", ms=5)
        ax2.set_title("T-S: area = heat", fontsize=9); ax2.set_xlabel("s (kJ/kg K)", fontsize=8); ax2.set_ylabel("T (K)", fontsize=8)
        for a in (ax1, ax2):
            a.tick_params(labelsize=7); a.grid(alpha=0.3, which="both")
        ax3 = fig.add_subplot(gs[3, j]); ax3.axis("off")
        txt = ax3.text(0.5, 0.75, "", ha="center", fontsize=9, color=col, weight="bold")
        ax3.text(0.5, 0.05, f"end of cycle W/Qin = {c['eta']:.3f}", ha="center", fontsize=8)
        art.append((c, lv, gas, piston, rod, pv, d1, ts, d2, txt))

    def frame(k):
        f = min(1.0, k / (frames - 1))
        out = []
        for c, lv, gas, piston, rod, pv, d1, ts, d2, txt in art:
            i = int(round(f * (len(c["v"]) - 1)))
            y = 0.15 + 0.75 * lv[i]
            gas.set_height(y - 0.05); gas.set_color(cmap(tnorm(c["t"][i])))
            piston.set_ydata([y, y]); rod.set_ydata([y, 1.0])
            pv.set_data(c["v"][:i + 1], c["p"][:i + 1]); d1.set_data([c["v"][i]], [c["p"][i]])
            ts.set_data(c["s"][:i + 1], c["t"][:i + 1]); d2.set_data([c["s"][i]], [c["t"][i]])
            txt.set_text(f"work so far {c['w'][i]:5.0f} kJ/kg\nW/Qin so far {c['w'][i] / Q_IN:.3f}")
            out += [gas, piston, rod, pv, d1, ts, d2, txt]
        return out

    anim = animation.FuncAnimation(fig, frame, frames=frames + hold, blit=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    anim.save(path, writer=animation.PillowWriter(fps=12))
    plt.close(fig)
    return path


if __name__ == "__main__":
    ok = True
    for label, passed in checks():
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    if ok and "--check" not in sys.argv:
        print("Animation written to", animate().relative_to(ROOT))
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
