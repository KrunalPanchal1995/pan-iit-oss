# Roadmap: the path to the openreactionrate Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Temperature-dependent networks

**You will learn:** Giving every step its own Arrhenius constant and solving the network at several temperatures.

**You will build:** A network simulator in which every step has an activation energy and the temperature is an input.

**Checkpoint (not met by the shipped code):** For the chain A -> B -> C -> D with Ea = 40, 70 and 50 kJ/mol (rate constants 0.8, 0.05 and 0.6 1/s at 300 K), find the lowest whole-degree temperature at which the yield of D at 10 s is at least double its 300 K value of 0.295 (it is 309 K, giving 0.605; the shipped code has no temperature in its networks).

**Difficulty:** intermediate

## Session 5: Fit rate constants from noisy data

**You will learn:** Least-squares fitting of a network to measured concentrations, and why some constants cannot be found.

**You will build:** A fitting routine that recovers k1 and k2 of A -> B -> C from synthetic data.

**Checkpoint (not met by the shipped code):** Recover k1 and k2 to within 5 percent from data with 2 percent noise (the shipped code only simulates, it never fits).

**Difficulty:** intermediate

## Session 6: Heat of reaction: exothermic and endothermic

**You will learn:** An energy balance next to the species balance, so that the temperature changes as the reaction goes.

**You will build:** An adiabatic reactor in which the heat released changes k, with the catalyst as a switch.

**Checkpoint (not met by the shipped code):** Reproduce the adiabatic temperature rise dT = (-dH) c0 / (rho cp): 12.5 K for dH = -50 kJ/mol, c0 = 1 mol/L and rho cp = 4.0e6 J/(m3 K), within 1 percent (the shipped code has no heat).

**Difficulty:** advanced

## Session 7: An implicit solver for stiff nonlinear networks

**You will learn:** Newton iteration inside backward Euler (or BDF) and adaptive step control.

**You will build:** A stiff solver that handles the enzyme cycle with k1 = 1e6 L/(mol s).

**Checkpoint (not met by the shipped code):** Stay within 1 percent of a fine reference solution using fewer than 2000 steps, where the shipped explicit RK4 needs more than a million.

**Difficulty:** advanced

## Session 8: Oscillating reactions

**You will learn:** Autocatalysis and the Brusselator: a network that never settles.

**You will build:** A Brusselator simulation with a stability picture.

**Checkpoint (not met by the shipped code):** For A = 1 the concentration of X oscillates with amplitude above 1 at B = 3 over the last 20 s of a 100 s run and decays to below 0.001 at B = 1.5 (the shipped code has no autocatalytic step).

**Difficulty:** advanced

## The final step

Combine the milestones: a network simulator in which every step has its own activation energy, heat release and a catalyst you can aim at any step, with a stiff solver and a fit to data. If your result looks like the Target animation, open a pull request and tell us how you did it.
