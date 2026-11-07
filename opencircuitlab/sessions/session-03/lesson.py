"""Session 3 (Level 3): nodal analysis by the stamp method, Thevenin, bridges and tolerance.

Run:  python start.py 3
Low-voltage educational circuits only (never mains). Ideal sources, linear resistors.
"""
# %% [markdown]
# # Session 3: solve any resistor network with a matrix
# **A. Real-world problem.** A temperature sensor on a board is a resistor whose value changes a
# little with temperature. A Wheatstone bridge turns that small change into a measurable
# voltage. But every other resistor in the bridge has a tolerance of 5 percent. Hand solving
# is out: we need a method that works for ANY network, and a way to ask "how bad can it get?"
#
# **Plan.** (1) write Kirchhoff's current law at every node as one matrix equation G v = i,
# (2) fill the matrix with a stamp for each part, (3) validate against hand-solved circuits and
# against energy conservation, (4) Thevenin equivalent and maximum power transfer, (5) the
# bridge, a Monte Carlo of tolerances, and what happens when a circuit is ill-posed.

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: KCL at every node becomes G v = i
# Number the nodes 1..n and call the reference (0 V) node 0. A resistor R between nodes a and b
# carries (v_a - v_b)/R = g (v_a - v_b), with conductance g = 1/R. Current law at node a:
# the sum of g (v_a - v_b) over all resistors at a equals the current injected into a.
# That is row a of G v = i. The "stamp" of one resistor adds +g to G[a,a] and G[b,b] and -g to
# G[a,b] and G[b,a] (rows and columns of node 0 are dropped).
#
# An ideal voltage source (value V, plus terminal p, minus terminal m) forces v_p - v_m = V. We
# add its current j (flowing out of the plus terminal into the circuit) as an extra unknown and
# one extra equation. This is called modified nodal analysis.
#
# Check by hand (S2 circuit): V1 = 10 V, V2 = 4 V, R1 = 100, R2 = 200, R3 = 300 ohm gave V_A = 6.545 V.

# %%
def solve_network(n_nodes, resistors, vsources=(), isources=()):
    """Solve a resistor network. Nodes are 0 (ground) to n_nodes.

    resistors: (a, b, ohm). vsources: (plus, minus, volts). isources: (a, b, amperes): the
    source pushes that current from node a, through itself, into node b.
    Returns (v, j): node voltages v[0..n_nodes] (v[0] = 0) and the current j[k] that each
    voltage source delivers (positive = the source is supplying power).
    Raises ValueError for a floating node or contradictory sources (singular matrix).
    """
    n, m = n_nodes, len(vsources)
    size = n + m
    a = np.zeros((size, size))
    rhs = np.zeros(size)
    for na, nb, r in resistors:
        if r <= 0:
            raise ValueError("resistance must be positive (a 0 ohm wire is a short circuit)")
        g = 1.0 / r
        for p, q, s in ((na, na, g), (nb, nb, g), (na, nb, -g), (nb, na, -g)):
            if p > 0 and q > 0:
                a[p - 1, q - 1] += s
    for na, nb, cur in isources:
        if na > 0:
            rhs[na - 1] -= cur
        if nb > 0:
            rhs[nb - 1] += cur
    for k, (p, q, volts) in enumerate(vsources):
        if p > 0:
            a[p - 1, n + k] -= 1.0
            a[n + k, p - 1] += 1.0
        if q > 0:
            a[q - 1, n + k] += 1.0
            a[n + k, q - 1] -= 1.0
        rhs[n + k] = volts
    if size == 0:
        return np.zeros(1), np.zeros(0)
    if np.linalg.cond(a) > 1e12:
        raise ValueError("singular matrix: a node is floating (no path to ground) or sources contradict each other")
    x = np.linalg.solve(a, rhs)
    return np.concatenate(([0.0], x[:n])), x[n:]


# %% [markdown]
# ## Step 2: branch currents and the power balance
# Once the node voltages are known, every resistor current is (v_a - v_b)/R. Energy is
# conserved: power supplied by the sources must equal power dissipated in the resistors.

# %%
def branch_currents(v, resistors):
    """Current in each resistor from a to b (A)."""
    return np.array([(v[a] - v[b]) / r for a, b, r in resistors])


def power_balance(v, j, resistors, vsources=(), isources=()):
    """Returns (supplied, dissipated) in watts."""
    dissipated = float(sum((v[a] - v[b]) ** 2 / r for a, b, r in resistors))
    supplied = float(sum(volts * j[k] for k, (_, _, volts) in enumerate(vsources)))
    supplied += float(sum(cur * (v[b] - v[a]) for a, b, cur in isources))
    return supplied, dissipated


# the Session 2 two-loop circuit as a network: node 1 = A, node 2 above V1/R1, node 3 above V2/R2
TWO_LOOP = dict(n_nodes=3,
                resistors=[(2, 1, 100.0), (3, 1, 200.0), (1, 0, 300.0)],
                vsources=[(2, 0, 10.0), (3, 0, 4.0)])


# %% [markdown]
# ## Step 3: Thevenin equivalent and maximum power transfer
# Any linear network seen from two terminals behaves like ONE source V_th in series with ONE
# resistor R_th. V_th is the open-circuit voltage between the terminals. R_th is found by turning
# every source off (voltage sources become wires, current sources are removed) and measuring
# V/I at the terminals, here by injecting 1 A.
# A load R_L on the terminals gets I = V_th/(R_th + R_L) and P_L = V_th^2 R_L/(R_th + R_L)^2,
# which is largest when R_L = R_th, giving P_max = V_th^2/(4 R_th) (efficiency only 50 percent).
# Check by hand: 12 V, R1 = 1000, R2 = 2000 ohm, terminals across R2: V_th = 8 V,
# R_th = 1000 || 2000 = 666.7 ohm, P_max = 64/(4 * 666.7) = 24 mW at R_L = 666.7 ohm.

# %%
def thevenin(n_nodes, resistors, vsources, isources, port):
    """Thevenin equivalent (v_th, r_th) seen between port = (a, b), with v_th = v_a - v_b."""
    a, b = port
    v_open, _ = solve_network(n_nodes, resistors, vsources, isources)
    zeroed = [(p, q, 0.0) for p, q, _ in vsources]
    v_test, _ = solve_network(n_nodes, resistors, zeroed, [(b, a, 1.0)])
    return float(v_open[a] - v_open[b]), float(v_test[a] - v_test[b])


def load_power(vth, rth, rl):
    """Power in a load rl fed by a Thevenin source (W)."""
    return vth ** 2 * rl / (rth + rl) ** 2


DIVIDER_12V = dict(n_nodes=2, resistors=[(1, 2, 1000.0), (2, 0, 2000.0)], vsources=[(1, 0, 12.0)], isources=[])


def load_power_by_nodal(rl, net=DIVIDER_12V, port=(2, 0)):
    """Same power, but by adding the load as a real resistor in the network and solving it."""
    res = list(net["resistors"]) + [(port[0], port[1], rl)]
    v, _ = solve_network(net["n_nodes"], res, net["vsources"], net["isources"])
    return float((v[port[0]] - v[port[1]]) ** 2 / rl)


# %% [markdown]
# ## Step 4: the Wheatstone bridge
# Two dividers share one supply. Top node T = V_s, bottom = ground. Left arm: R1 (T to A) and
# R3 (A to ground). Right arm: R2 (T to B) and R4 (B to ground). The meter reads V_A - V_B:
#     V_out = V_s (R3/(R1+R3) - R4/(R2+R4)).
# It is zero (balanced) when R1/R3 = R2/R4, that is R1 R4 = R2 R3, whatever V_s is.
# If all four are R and one changes by a small dR, V_out is about V_s dR/(4 R).

# %%
def bridge_out(vs, r1, r2, r3, r4):
    """Bridge output V_A - V_B (V). Works on numpy arrays as well as on numbers."""
    return vs * (r3 / (r1 + r3) - r4 / (r2 + r4))


def bridge_by_nodal(vs, r1, r2, r3, r4):
    """The same output from the general solver (node 1 = T, node 2 = A, node 3 = B)."""
    res = [(1, 2, r1), (1, 3, r2), (2, 0, r3), (3, 0, r4)]
    v, _ = solve_network(3, res, [(1, 0, vs)])
    return float(v[2] - v[3])


def monte_carlo_bridge(n=20000, tol=0.05, vs=5.0, r=1000.0, seed=1):
    """Bridge output for n random draws of the four resistors, each uniform in r*(1 +- tol)."""
    rng = np.random.default_rng(seed)
    r1, r2, r3, r4 = (r * (1 + tol * rng.uniform(-1, 1, n)) for _ in range(4))
    return bridge_out(vs, r1, r2, r3, r4)


def predicted_offset_std(vs=5.0, tol=0.05):
    """Small-change prediction of the output spread: four resistors each add Vs/4 * (dR/R)."""
    return vs / 4.0 * 2.0 * tol / np.sqrt(3.0)


# %% [markdown]
# ## Step 5: when the matrix cannot be solved
# A circuit with a node that has no connection to the reference has no definite voltage: the
# matrix is singular. So are two ideal sources of different voltage across the same two nodes.
# A real short circuit is different: the matrix is fine, the answer is a huge current limited
# only by the small internal resistance of the battery.

# %%
def short_circuit(vbatt=9.0, r_internal=1.0, r_wire=0.01):
    """A battery with internal resistance shorted by a wire. Returns (current A, heat in battery W)."""
    i = vbatt / (r_internal + r_wire)
    return i, i * i * r_internal


# %% [markdown]
# ## Step 6: mini-project tools (a Pt1000 temperature sensor in a bridge)
# A Pt1000 sensor has R(T) = 1000 (1 + 0.00385 T) ohm, T in degrees Celsius (a straight-line
# approximation). It goes in the R3 position, the other three resistors equal R_fixed = 1000 ohm.

# %%
def pt1000(t_c):
    return 1000.0 * (1.0 + 0.00385 * np.asarray(t_c, dtype=float))


def sensor_bridge_out(vs, t_c, r_fixed=1000.0):
    return bridge_out(vs, r_fixed, r_fixed, pt1000(t_c), r_fixed)


def sensor_power(vs, t_c, r_fixed=1000.0):
    """Heat in the sensor itself (W): too much heats it and falsifies the reading."""
    rt = pt1000(t_c)
    return (vs / (r_fixed + rt)) ** 2 * rt


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    v, j = solve_network(**TWO_LOOP)
    print("two-loop by nodal analysis: V_A =", round(v[1], 4), "V, battery currents (mA) =", np.round(1000 * j, 3))
    s, d = power_balance(v, j, TWO_LOOP["resistors"], TWO_LOOP["vsources"])
    print(f"power supplied {1000 * s:.4f} mW, dissipated {1000 * d:.4f} mW")
    vth, rth = thevenin(**DIVIDER_12V, port=(2, 0))
    print(f"Thevenin of the 12 V divider: Vth = {vth:.3f} V, Rth = {rth:.1f} ohm, Pmax = {1000 * vth ** 2 / (4 * rth):.2f} mW")
    rl = np.linspace(50, 3000, 300)
    best = rl[np.argmax([load_power_by_nodal(x) for x in rl])]
    print(f"numerical search: maximum power at R_L = {best:.0f} ohm")
    mc = monte_carlo_bridge()
    print(f"bridge, 5 percent resistors: std of V_out = {1000 * mc.std():.1f} mV (predicted {1000 * predicted_offset_std():.1f} mV)")
    print(f"  fraction of bridges within +-10 mV of balance: {np.mean(np.abs(mc) < 0.01):.3f}")
    print("short circuit of a 9 V pack: %.1f A, %.0f W inside the battery" % short_circuit())
    for t in (0, 50, 100):
        print(f"Pt1000 at {t:3d} C: {float(pt1000(t)):.1f} ohm, V_out {1000 * float(sensor_bridge_out(5.0, t)):.1f} mV at 5 V, "
              f"sensor heat {1000 * float(sensor_power(5.0, t)):.2f} mW")

    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(rl, [1000 * load_power(vth, rth, x) for x in rl], label="Thevenin formula")
    ax.plot(rl[::15], [1000 * load_power_by_nodal(x) for x in rl[::15]], "o", label="nodal solver")
    ax.axvline(rth, color="gray", ls=":")
    ax.set_xlabel("load resistance R_L (ohm)")
    ax.set_ylabel("power in the load (mW)")
    ax.set_title("Maximum power transfer at R_L = R_th (dotted)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "max_power_transfer.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4))
    ax2.hist(1000 * mc, bins=60, color="#4c72b0")
    ax2.set_xlabel("bridge output at nominal balance (mV)")
    ax2.set_ylabel("number of bridges out of 20000")
    ax2.set_title("5 percent resistors: the balanced bridge is never balanced")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(OUT / "bridge_tolerance.png", dpi=120)

    fig3, ax3 = plt.subplots(figsize=(6.4, 4))
    t = np.linspace(0, 100, 101)
    for vs in (1.5, 2.0, 5.0):
        ax3.plot(t, 1000 * sensor_bridge_out(vs, t), label=f"supply {vs} V")
    ax3.set_xlabel("temperature (degrees C)")
    ax3.set_ylabel("bridge output (mV)")
    ax3.set_title("Pt1000 sensor bridge output")
    ax3.grid(alpha=0.3)
    ax3.legend()
    fig3.tight_layout()
    fig3.savefig(OUT / "sensor_bridge.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
