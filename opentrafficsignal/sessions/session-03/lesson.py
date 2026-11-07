"""Session 3 (Level 3): a junction simulator with random arrivals, checked against the formula.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: a junction simulator, checked against the formula
# **A. Real-world problem.** Real cars do not arrive at neat intervals; they come in random
# bunches. Does the tidy delay formula of Session 2 still describe them? Does a signal that
# reacts to the queue beat a fixed timetable? And what happens when more cars arrive than the
# junction can ever serve?
#
# **Plan.** (1) generate seeded random arrivals, (2) simulate the junction second by second
# with a fixed plan and a simple actuated rule, (3) validate against the formula and against
# conservation of cars, (4) vary the cycle time and the arrival rates, (5) provoke a failure.
#
# *This is a simplified educational model, not a traffic engineering tool.*

# %%
import pathlib
from collections import deque

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
S_SAT = 0.5       # saturation flow, cars per second per lane (a typical textbook value)
AMBER = 3.0       # seconds; no car leaves on amber, so it is the lost time of each phase
LOST = 2 * AMBER  # lost time per cycle for two phases


# %% [markdown]
# ## Step 1: arrivals
# Cars arrive at random with an average rate `q`: the gaps between cars are exponentially
# distributed (a Poisson process). A seeded generator makes every run repeatable. For
# validation we also keep a perfectly regular stream, which matches the "even arrivals" of the
# formula.

# %%
def poisson_arrivals(rng, q, T):
    """Arrival times (s) of a Poisson stream with rate q cars/s over [0, T)."""
    if q <= 0:
        return np.array([])
    n = int(q * T * 1.5 + 50)
    times = np.cumsum(rng.exponential(1.0 / q, size=n))
    while times[-1] < T:
        times = np.concatenate([times, times[-1] + np.cumsum(rng.exponential(1.0 / q, size=n))])
    return times[times < T]


def regular_arrivals(q, T):
    """Evenly spaced arrivals, one every 1/q seconds (the 'no randomness' case)."""
    if q <= 0:
        return np.array([])
    gap = 1.0 / q
    return np.arange(0.5 * gap, T, gap)


# %% [markdown]
# ## Step 2: two ways to run the signals
# Approach `i` belongs to phase `i % 2` (approaches 0 and 2 share phase 0; 1 and 3 share
# phase 1). A controller is called every step with the queue lengths and answers
# "which phase, and is it green or amber?".
# * **Fixed**: a timetable, `green0, amber, green1, amber`, repeated forever.
# * **Actuated**: stay green while the phase still has a queue, up to `max_green`; give up the
#   green when its queue is empty and the other phase waits, but not before `min_green`.

# %%
class FixedPlan:
    def __init__(self, greens, amber=AMBER):
        self.g = tuple(float(x) for x in greens)
        self.amber = float(amber)
        self.cycle = self.g[0] + self.g[1] + 2 * self.amber

    def __call__(self, t, queues):
        tau = t % self.cycle
        if tau < self.g[0]:
            return 0, True
        if tau < self.g[0] + self.amber:
            return 0, False
        if tau < self.g[0] + self.amber + self.g[1]:
            return 1, True
        return 1, False


class Actuated:
    def __init__(self, min_green=8.0, max_green=45.0, amber=AMBER):
        self.min_green, self.max_green, self.amber = min_green, max_green, amber
        self.phase, self.in_amber, self.timer, self.last_t = 0, False, 0.0, 0.0

    def __call__(self, t, queues):
        dt, self.last_t = t - self.last_t, t
        self.timer += dt
        mine = max([qv for i, qv in enumerate(queues) if i % 2 == self.phase], default=0)
        other = max([qv for i, qv in enumerate(queues) if i % 2 != self.phase], default=0)
        if self.in_amber:
            if self.timer >= self.amber:
                self.phase, self.in_amber, self.timer = 1 - self.phase, False, 0.0
        elif other > 0 and (self.timer >= self.max_green or (self.timer >= self.min_green and mine == 0)):
            self.in_amber, self.timer = True, 0.0
        return self.phase, not self.in_amber


# %% [markdown]
# ## Step 3: the simulator
# Every `dt` seconds: new cars join their queue; the controller picks the phase; cars on a
# green approach leave at the saturation flow `s` (a "credit" grows by `s dt` per step and a car
# leaves each time it reaches 1; the first car of a green leaves at once). Each car remembers its arrival time, so its delay is exact:
# time of leaving minus time of arrival. Cars still waiting at the end count their delay so far.
# We record the average delay, the largest queue and the numbers needed to check conservation.

# %%
def simulate(q, controller, s=S_SAT, T=3600.0, dt=0.5, seed=1, poisson=True):
    """Simulate len(q) approaches. q and s may be a list or one number. Returns a dict of results.

    Delay of a car = time it crosses the stop line minus its arrival time (the stop line is
    crossed in the middle of a step, but never before the car arrived).
    """
    q = list(q)
    n = len(q)
    s = [s] * n if np.isscalar(s) else list(s)
    rng = np.random.default_rng(seed)
    arr = [poisson_arrivals(rng, qi, T) if poisson else regular_arrivals(qi, T) for qi in q]
    ptr = [0] * n
    queues = [deque() for _ in range(n)]
    credit = [0.0] * n
    departed, delay_sum = [0] * n, 0.0
    steps = int(round(T / dt))
    qlen = np.zeros((steps, n))
    for k in range(steps):
        t = k * dt
        for i in range(n):
            while ptr[i] < len(arr[i]) and arr[i][ptr[i]] < t + dt:
                queues[i].append(arr[i][ptr[i]])
                ptr[i] += 1
        phase, green = controller(t, [len(x) for x in queues])
        for i in range(n):
            if green and i % 2 == phase:
                credit[i] = min(credit[i] + s[i] * dt, 1.0 + s[i] * dt)
                while credit[i] >= 1.0 and queues[i]:
                    a = queues[i].popleft()
                    delay_sum += max(a, t + dt / 2) - a
                    credit[i] -= 1.0
                    departed[i] += 1
            else:
                credit[i] = 1.0      # the first car of the next green may go at once (no start-up loss)
            qlen[k, i] = len(queues[i])
    waiting = sum(T - a for i in range(n) for a in queues[i])
    total_arrived = sum(len(a) for a in arr)
    return {"arrived": [len(a) for a in arr], "departed": departed, "in_queue": [len(x) for x in queues],
            "avg_delay": (delay_sum + waiting) / max(total_arrived, 1), "max_queue": float(qlen.max()),
            "qlen": qlen, "dt": dt, "total_delay": delay_sum + waiting}


# %% [markdown]
# ## Step 4: the references to check against
# * **Conservation**: every car that arrived has either left or is still in a queue.
# * **Uniform delay** (Session 2): `d = C (1 - g/C)^2 / (2 (1 - q/s))` for even arrivals.
# * **Webster cycle** (a classic rule of thumb): `C = (1.5 L + 5) / (1 - Y)` where `L` is the lost
#   time per cycle and `Y` the sum of the critical flow ratios of the phases; the green is shared
#   in proportion to the critical flow ratios of the phases.

# %%
def uniform_delay(C, g, q, s=S_SAT):
    """Seconds per car for even arrivals; infinity if the approach is oversaturated (x > 1)."""
    if g <= 0 or q * C / (g * s) > 1.0 + 1e-12:
        return float("inf")
    return C * (1.0 - g / C) ** 2 / (2.0 * (1.0 - q / s))


def fixed_plan_uniform_delay(q, plan, s=S_SAT):
    """Average of the uniform delays of all approaches, weighted by their flows."""
    s = [s] * len(q) if np.isscalar(s) else list(s)
    num = sum(qi * uniform_delay(plan.cycle, plan.g[i % 2], qi, s[i]) for i, qi in enumerate(q))
    return num / sum(q)


def conservation_gap(result):
    """arrived - departed - still waiting, per approach. Must be zero."""
    return [a - d - w for a, d, w in zip(result["arrived"], result["departed"], result["in_queue"])]


def webster_cycle(Y, lost=LOST):
    """Webster's classic optimum cycle (s); infinity if Y >= 1."""
    return float("inf") if Y >= 1.0 else (1.5 * lost + 5.0) / (1.0 - Y)


def webster_plan(q, s=S_SAT, lost=LOST, amber=AMBER):
    """Fixed two-phase plan from flows: critical flow ratio of each phase = its largest q/s."""
    s = [s] * len(q) if np.isscalar(s) else list(s)
    y = [max(q[i] / s[i] for i in range(len(q)) if i % 2 == ph) for ph in (0, 1)]
    Y = y[0] + y[1]
    C = webster_cycle(Y, lost)
    if not np.isfinite(C):
        raise ValueError("Y >= 1: no fixed plan can serve this demand")
    spare = C - lost
    return FixedPlan((spare * y[0] / Y, spare * y[1] / Y), amber)


def mean_over_seeds(q, make_controller, seeds=range(1, 13), **kw):
    """Average delay and largest queue over several seeds (a fresh controller each time)."""
    runs = [simulate(q, make_controller(), seed=sd, **kw) for sd in seeds]
    return float(np.mean([r["avg_delay"] for r in runs])), float(np.mean([r["max_queue"] for r in runs]))


# %% [markdown]
# ## Step 5: run the experiments
# Two approaches, `q = (0.20, 0.10)` cars/s, `s = 0.5`, one hour per run.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    q = [0.20, 0.10]
    plan60 = FixedPlan((27.0, 27.0))

    print("--- validation 1: even arrivals against the uniform-delay formula")
    reg = simulate(q, plan60, poisson=False, T=7200.0)
    d_formula = fixed_plan_uniform_delay(q, plan60)
    print(f"simulated {reg['avg_delay']:.2f} s, formula {d_formula:.2f} s, "
          f"difference {100 * (reg['avg_delay'] / d_formula - 1):+.1f} %")
    print("--- validation 2: conservation of cars (arrived - departed - waiting)")
    print("gap per approach:", conservation_gap(reg), "arrived", reg["arrived"])
    print("--- validation 3: delay summed over cars equals the area under the queue curve (Little)")
    area = reg["qlen"].sum() * reg["dt"]
    print(f"sum of delays {reg['total_delay']:.0f} car-s, area under queue {area:.0f} car-s")
    print("--- random arrivals add delay (Poisson, 12 seeds)")
    dr, mqr = mean_over_seeds(q, lambda: plan60)
    print(f"Poisson: {dr:.2f} s average delay, {mqr:.1f} cars largest queue; even arrivals: {reg['avg_delay']:.2f} s, {reg['max_queue']:.0f} cars")

    print("--- sensitivity to cycle length (greens shared 2:1, 12 seeds)")
    Y = sum(qi / S_SAT for qi in q)
    print(f"Webster cycle: Y = {Y:.2f}, C = {webster_cycle(Y):.1f} s")
    cycles = [20, 25, 30, 35, 40, 50, 60, 80, 100, 120]
    sweep = []
    for Cc in cycles:
        spare = Cc - LOST
        res = mean_over_seeds(q, lambda: FixedPlan((spare * 2 / 3, spare / 3)))
        sweep.append(res[0])
        print(f"C = {Cc:3d} s -> average delay {res[0]:5.2f} s, largest queue {res[1]:4.1f} cars")
    print(f"best simulated cycle: {cycles[int(np.argmin(sweep))]} s")

    print("--- fixed (Webster plan) against actuated, demand scaled by f")
    base = webster_plan(q)
    print(f"Webster plan: green {base.g[0]:.1f} / {base.g[1]:.1f} s, C = {base.cycle:.1f} s")
    factors = [0.6, 0.8, 1.0, 1.2, 1.4]
    fixed_d, act_d = [], []
    for f in factors:
        qf = [f * x for x in q]
        fixed_d.append(mean_over_seeds(qf, lambda: base)[0])
        act_d.append(mean_over_seeds(qf, Actuated)[0])
        print(f"f = {f:.1f}: fixed {fixed_d[-1]:6.2f} s, actuated {act_d[-1]:6.2f} s")

    print("--- failure case: demand above capacity (Y > 1)")
    qo = [0.35, 0.20]
    print(f"Y = {sum(x / S_SAT for x in qo):.2f} -> Webster cycle {webster_cycle(sum(x / S_SAT for x in qo))}")
    over = {}
    for name, make in (("fixed 27/27", lambda: plan60), ("actuated", Actuated)):
        r = simulate(qo, make(), T=7200.0)
        over[name] = r
        half = len(r["qlen"]) // 2
        print(f"{name}: waiting cars after 1 h {r['qlen'][half - 1].sum():.0f}, after 2 h {r['qlen'][-1].sum():.0f}")

    fig, ax = plt.subplots(figsize=(6.4, 4))
    ax.plot(cycles, sweep, "o-", label="simulated (Poisson, 12 seeds)")
    ax.axvline(webster_cycle(Y), color="tab:red", ls="--", label="Webster C = 35 s")
    ax.set_xlabel("cycle time C (s)")
    ax.set_ylabel("average delay (s per car)")
    ax.set_title("Delay against cycle length: a shallow valley")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "delay_vs_cycle.png", dpi=120)

    fig2, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.8))
    a1.plot(factors, fixed_d, "o-", label="fixed (Webster plan)")
    a1.plot(factors, act_d, "s-", label="actuated rule")
    a1.set_xlabel("demand multiplier f (1.0 = 0.20 and 0.10 cars/s)")
    a1.set_ylabel("average delay (s per car)")
    a1.set_title("Fixed against actuated timing")
    a1.grid(alpha=0.3)
    a1.legend(fontsize=8)
    for name, r in over.items():
        a2.plot(np.arange(len(r["qlen"])) * r["dt"] / 60.0, r["qlen"].sum(axis=1), label=name)
    a2.set_xlabel("time (minutes)")
    a2.set_ylabel("cars waiting, both approaches")
    a2.set_title("Failure: demand above capacity (Y = 1.1)")
    a2.grid(alpha=0.3)
    a2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "fixed_vs_actuated.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint. The mini-project at the end of the README asks you to time a junction from counts.
