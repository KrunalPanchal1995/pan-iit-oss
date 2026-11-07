"""Session 3 (Level 3): variable loads (rainflow + Miner), crack growth (Paris), scatter, a bracket.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: from one stress to a real load history
# **A. Real-world problem.** A bracket on a machine does not see a neat sine wave. It sees
# vibration, start-ups and now and then a hard knock. How many "shifts" will it last, and how
# often must we inspect it for cracks? Today we (1) count the cycles hidden in a messy history
# (*rainflow counting*), (2) add up their damage (*Miner's rule*), (3) grow a crack with
# *Paris' law*, (4) see how widely real lives scatter. All numbers are illustrative; this is a
# teaching model and never a method for certifying a real or safety-critical part.

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

SU, SE = 600.0, 300.0                                  # MPa, illustrative steel
B = -np.log10(0.9 * SU / SE) / 3.0                     # Basquin exponent b
A = (0.9 * SU) ** 2 / SE                               # Basquin coefficient, MPa


# %% [markdown]
# ## Step 1: rainflow counting
# A history is a list of stresses in time order. Only the *turning points* (peaks and valleys,
# called reversals) matter. The standard three-point rule (ASTM E1049) keeps a stack of turning
# points. When the newest range X is at least as large as the previous range Y, the range Y is
# a closed loop: it counts as one *full cycle* (or a *half cycle* if it contains the start of
# the history). What is left over at the end is counted as half cycles. A useful check: the sum
# of 2 * count * range over all counted cycles equals the total up-and-down travel of the history.

# %%
def reversals(x):
    """Turning points of a series (drops repeats and points in the middle of a slope)."""
    x = np.asarray(x, dtype=float)
    keep = [x[0]]
    for v in x[1:]:
        if v == keep[-1]:
            continue
        if len(keep) >= 2 and (keep[-1] - keep[-2]) * (v - keep[-1]) > 0:
            keep[-1] = v                 # still going the same way: extend
        else:
            keep.append(v)
    return np.array(keep)


def rainflow(x):
    """ASTM E1049 three-point rainflow. Returns a list of (range, mean, count), count 1.0 or 0.5."""
    stack, out = [], []
    for p in reversals(x):
        stack.append(p)
        while len(stack) >= 3:
            xr = abs(stack[-1] - stack[-2])
            yr = abs(stack[-2] - stack[-3])
            if xr < yr:
                break
            mean = 0.5 * (stack[-2] + stack[-3])
            if len(stack) == 3:                  # range Y contains the start: half cycle
                out.append((yr, mean, 0.5))
                stack.pop(0)
            else:                                # closed loop: full cycle
                out.append((yr, mean, 1.0))
                del stack[-3:-1]
    for i in range(len(stack) - 1):              # residue: half cycles
        out.append((abs(stack[i + 1] - stack[i]), 0.5 * (stack[i + 1] + stack[i]), 0.5))
    return out


# %% [markdown]
# ## Step 2: Miner's rule
# If a block of `n_i` cycles at some level has a life of `N_i` cycles at that level alone, it
# uses up the fraction `n_i / N_i` of the life. Failure is predicted when the sum reaches 1:
#
#     D = sum( n_i / N_i ) = 1
#
# This *linear damage rule* is standard but rough: it ignores the order of the loads (a few big
# cycles early change how later small cycles act) and in tests the sum at failure scatters
# roughly between 0.3 and 3. Each cycle's mean stress is handled with Goodman (Session 2).

# %%
def cycle_life(amplitude, mean=0.0, below="extend"):
    """Cycles to failure of one rainflow cycle (amplitude and mean in MPa).
    below='extend' keeps the Basquin line under S_e (conservative); below='ignore' gives inf."""
    if mean >= SU:
        return 1.0
    eq = amplitude / (1.0 - mean / SU)
    if below == "ignore" and eq <= SE:
        return np.inf
    if eq <= 0:
        return np.inf
    return max(1.0, float((eq / A) ** (1.0 / B)))


def miner_damage(cycles, below="extend"):
    """Total damage D of a rainflow list of (range, mean, count). Failure is predicted at D = 1."""
    return float(sum(c / cycle_life(r / 2.0, m, below) for r, m, c in cycles))


def damage_shares(cycles, below="extend"):
    """Damage of each rainflow entry, as a numpy array in the same order."""
    return np.array([c / cycle_life(r / 2.0, m, below) for r, m, c in cycles])


def damage_share_above(cycles, amplitude, below="extend"):
    """Fraction of the total damage that comes from cycles whose amplitude (range/2) exceeds `amplitude`."""
    sh = damage_shares(cycles, below)
    big = np.array([r / 2.0 > amplitude for r, _, _ in cycles])
    return float(sh[big].sum() / sh.sum())


# %% [markdown]
# ## Step 3: crack growth (Paris' law)
# Once a crack exists, every cycle makes it longer by `da/dN = C * (delta_K)^m`, with the
# stress-intensity range `delta_K = Y * delta_sigma * sqrt(pi * a)` (MPa sqrt(m) when the
# stress range is in MPa and the length a is in m). Y is a shape factor (1.12 for a small edge
# crack), C and m are material constants (typical steel: C = 6.9e-12 and m = 3 for da/dN in m
# per cycle). The crack becomes critical when the largest K reaches the fracture toughness K_Ic:
# `a_c = (K_Ic / (Y * sigma_max * sqrt(pi)))^2`. The cycles from a0 to a_c follow from
# integrating `dN = da / (C delta_K^m)`; for constant Y and m not equal to 2 there is a closed
# form, which we use to test the numerical integral.

# %%
C_PARIS, M_PARIS, Y_EDGE, KIC = 6.9e-12, 3.0, 1.12, 50.0


def delta_k(dsig, a, y=Y_EDGE):
    """Stress-intensity range, MPa sqrt(m), for stress range dsig (MPa) and crack length a (m)."""
    return y * dsig * np.sqrt(np.pi * a)


def critical_crack(sigma_max, kic=KIC, y=Y_EDGE):
    """Crack length (m) at which K_max = K_Ic."""
    return (kic / (y * sigma_max * np.sqrt(np.pi))) ** 2


def paris_closed_form(a0, ac, dsig, c=C_PARIS, m=M_PARIS, y=Y_EDGE):
    """Cycles from a0 to ac for constant Y and m != 2."""
    k = 1.0 - m / 2.0
    return (ac ** k - a0 ** k) / (c * y ** m * dsig ** m * np.pi ** (m / 2.0) * k)


def paris_numeric(a0, ac, dsig, c=C_PARIS, m=M_PARIS, y=Y_EDGE, n=4000):
    """Cycles from a0 to ac by trapezoid integration of a/(C dK^m) over u = ln a. y may be a function of a."""
    u = np.linspace(np.log(a0), np.log(ac), n + 1)
    a = np.exp(u)
    yy = y(a) if callable(y) else y
    f = a / (c * delta_k(dsig, a, yy) ** m)
    return float(np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(u)))


def paris_curve(a0, ac, dsig, c=C_PARIS, m=M_PARIS, y=Y_EDGE, n=400):
    """(cycles, crack length) arrays for plotting the growth of the crack."""
    u = np.linspace(np.log(a0), np.log(ac), n + 1)
    a = np.exp(u)
    f = a / (c * delta_k(dsig, a, y) ** m)
    cyc = np.concatenate([[0.0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(u))])
    return cyc, a


# %% [markdown]
# ## Step 4: scatter and sensitivity
# Identical parts at the same stress do not fail at the same time. Life N is roughly *lognormal*:
# log10(N) is a normal (bell-curve) number around the predicted value. We use a standard
# deviation of 0.3 in log10(N), an illustrative value. And because life goes as stress to the
# power 1/b, a small stress change has a big effect: a factor `r` in stress changes life by `r^(1/b)`.

# %%
def lognormal_lives(n_median, sigma_log10=0.3, size=10000, seed=42):
    """Random lives with median n_median and spread sigma_log10 (in log10 N). Seeded."""
    rng = np.random.default_rng(seed)
    return n_median * 10.0 ** rng.normal(0.0, sigma_log10, size)


def life_ratio_for_stress_change(ratio, exponent=B):
    """New life / old life when the stress amplitude is multiplied by `ratio` (Basquin)."""
    return ratio ** (1.0 / exponent)


# %% [markdown]
# ## Step 5: a bracket and a measured-style load history
# The function below builds a synthetic "measured" history of one shift: load in newtons at the
# bracket's hot spot, converted to stress with 0.1 MPa per newton (this factor includes the
# notch effect; an assumption). It has steady vibration, 10 start-ups and 6 rare hard knocks.

# %%
K_STRESS = 0.1      # MPa per newton at the hot spot (assumed)


def bracket_history(seed=7, n=4000, n_knocks=6):
    """Hot-spot stress (MPa) at 4000 equally spaced instants of one shift."""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    f = 1000 + 700 * np.sin(2 * np.pi * t / 37) * (1 + 0.4 * np.sin(2 * np.pi * t / 500)) / 1.4 + rng.normal(0, 60, n)
    pulse = np.array([0.1, 0.5, 1, 1, 0.5, 0.1])
    for k in range(250, n - 10, 400):
        f[k:k + 6] += 3000 * pulse
    for k in np.linspace(300, n - 300, n_knocks).astype(int):
        f[k - 2:k + 3] = [-500, -1200, 4500, -1200, -500]
    return K_STRESS * f


def effective_range(rng_, mean):
    """Part of a cycle's range that is in tension (a crack is closed in compression)."""
    smax, smin = mean + rng_ / 2.0, mean - rng_ / 2.0
    return max(smax, 0.0) - max(smin, 0.0)


def equivalent_range(cycles, m=M_PARIS):
    """Constant stress range with the same Paris growth as the whole list (m-th power mean)."""
    num = sum(c * effective_range(r, mn) ** m for r, mn, c in cycles)
    den = sum(c for r, mn, c in cycles)
    return float((num / den) ** (1.0 / m))


def inspection_interval_shifts(stress, a_detect=0.5e-3, safety=3.0):
    """Shifts between inspections: (shifts for a crack to grow from a_detect to critical) / safety."""
    cyc = rainflow(stress)
    dsig = equivalent_range(cyc)
    ac = critical_crack(stress.max())
    n_cycles = paris_closed_form(a_detect, ac, dsig)
    per_shift = sum(c for r, mn, c in cyc)
    return n_cycles / per_shift / safety


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    seq = [-2, 1, -3, 5, -1, 3, -4, 4, -2]
    print("ASTM-style test sequence:", [(float(r), float(m), c) for r, m, c in rainflow(seq)])

    s = bracket_history()
    cyc = rainflow(s)
    d_ext, d_ign = miner_damage(cyc), miner_damage(cyc, "ignore")
    shares = damage_shares(cyc)
    cnt_big = sum(c for r, _, c in cyc if r / 2 > 250)
    print(f"cycles above 250 MPa amplitude: {cnt_big} of {sum(c for _, _, c in cyc)}, damage share {damage_share_above(cyc, 250):.3f}")
    print(f"no knocks: life {1 / miner_damage(rainflow(bracket_history(n_knocks=0))):,.0f} shifts")
    print(f"cycles counted {sum(c for _, _, c in cyc):.1f}; D per shift {d_ext:.3e} -> life {1 / d_ext:,.0f} shifts")
    print(f"ignoring cycles below S_e: D = {d_ign:.3e} -> {1 / d_ign:,.0f} shifts; ")
    print(f"inspection interval {inspection_interval_shifts(s):.1f} shifts")

    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    axs[0].plot(s, lw=0.6)
    axs[0].set_xlabel("time step within one shift")
    axs[0].set_ylabel("hot-spot stress (MPa)")
    axs[0].set_title("Synthetic load history of one shift")
    axs[0].grid(alpha=0.3)
    amps = np.array([r / 2 for r, _, _ in cyc])
    axs[1].scatter(amps, shares / shares.sum(), s=10)
    axs[1].set_yscale("log")
    axs[1].set_xlabel("cycle amplitude (MPa)")
    axs[1].set_ylabel("share of total damage")
    axs[1].set_title("A few big cycles carry almost all the damage")
    axs[1].grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(OUT / "history_damage.png", dpi=120)

    a0, dsig = 1e-3, 100.0
    ac = critical_crack(dsig)
    n_cf, n_num = paris_closed_form(a0, ac, dsig), paris_numeric(a0, ac, dsig)
    cyc2, a = paris_curve(a0, ac, dsig)
    fig2, ax2 = plt.subplots(figsize=(6.2, 4.0))
    ax2.plot(cyc2, a * 1000)
    ax2.set_xlabel("load cycles")
    ax2.set_ylabel("crack length (mm)")
    ax2.set_title("Paris' law: slow at first, then faster and faster")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "crack_growth.png", dpi=120)
    print(f"a_c = {ac * 1000:.1f} mm; closed form {n_cf:,.0f}; numeric {n_num:,.0f} cycles")

    lives = lognormal_lives(1e5)
    fig3, ax3 = plt.subplots(figsize=(6.2, 4.0))
    ax3.hist(np.log10(lives), bins=50)
    ax3.set_xlabel("log10 of cycles to failure")
    ax3.set_ylabel("number of parts (of 10000)")
    ax3.set_title("Scatter: same stress, very different lives")
    ax3.grid(alpha=0.3)
    fig3.tight_layout()
    fig3.savefig(OUT / "scatter.png", dpi=120)
    p5, p95 = np.percentile(lives, [5, 95])
    print(f"5th to 95th percentile ratio {p95 / p5:.1f}")
    print(f"10 percent more stress: life x {life_ratio_for_stress_change(1.1):.3f}")

# %% [markdown]
# ## Where this stops
# Miner's rule ignores load order, rainflow ignores timing, Paris' law uses a fixed Y and no
# crack closure, and the scatter width is only an example. Treat the outputs as estimates
# for learning, never as a certificate for a real part.
