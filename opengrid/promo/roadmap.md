# Roadmap: the path to the opengrid Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Synthetic inertia from a battery

**You will learn:** How a battery can respond to the rate of change of frequency, not only to the deviation.

**You will build:** A battery model with power proportional to RoCoF and a power limit, added to the swing equation.

**Checkpoint (not met by the shipped code):** A 10 percent loss at H = 2 s keeps the nadir at or above 49.4 Hz with a battery of at most 0.05 pu (the shipped proportional battery gives 49.329 Hz).

**Difficulty:** intermediate

## Session 5: Limited governor headroom

**You will learn:** Why spinning reserve matters: the governor can only add as much as its headroom.

**You will build:** The governor output clipped to a reserve limit, with a settled-value formula.

**Checkpoint (not met by the shipped code):** With a headroom of 0.06 pu and a 10 percent loss, the settled frequency is 48.0 Hz (the shipped unlimited governor settles at 49.762 Hz).

**Difficulty:** intermediate

## Session 6: Under-frequency load shedding

**You will learn:** How protection sheds load in stages to arrest a deep fall.

**You will build:** Staged shedding steps at set frequencies added to the simulation.

**Checkpoint (not met by the shipped code):** A 20 percent loss at H = 2 s keeps the nadir above 48.5 Hz while shedding at most 12 percent of the load (the shipped model gives 47.84 Hz with no shedding).

**Difficulty:** advanced

## Session 7: AC power flow with voltage and reactive power

**You will learn:** Newton-Raphson load flow and how voltages and reactive flows differ from the DC approximation.

**You will build:** A three-bus AC power flow solved iteratively.

**Checkpoint (not met by the shipped code):** Mismatches below 1e-8 pu and a load-bus voltage below 1.0 pu (the shipped DC flow assumes 1.0 pu everywhere).

**Difficulty:** advanced

## Session 8: Estimate inertia from a noisy trace

**You will learn:** How operators estimate H from a measured frequency record.

**You will build:** A fitting routine that recovers H from a noisy simulated event.

**Checkpoint (not met by the shipped code):** H recovered within 10 percent from a trace with 0.01 Hz of noise, for H between 2 s and 8 s.

**Difficulty:** advanced

## The final step

Combine the milestones: a multi-generator grid with realistic governors, a battery that stops the fall, load shedding as a last defence, and a live panel showing the frequency and the power triangle. If your result looks like the Target animation, open a pull request and tell us how you did it.
