# Roadmap: the path to the opencircuitlab Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 6: An amplifier from a controlled source

**You will learn:** Dependent sources and the ideal operational amplifier as a very high gain voltage-controlled source.

**You will build:** A controlled-source stamp and an inverting amplifier built with it.

**Checkpoint (not met by the shipped code):** An inverting amplifier with Rf = 10 kohm and Rin = 1 kohm gives a gain within 0.1 percent of -10 (the shipped solver has only resistors and independent sources).

**Difficulty:** intermediate

## Session 7: Sensitivity without Monte Carlo

**You will learn:** How the adjoint idea gives the derivative of an output with respect to every resistor from a single extra solve.

**You will build:** A function returning dVout/dR for every resistor of any network.

**Checkpoint (not met by the shipped code):** For the Wheatstone bridge all four sensitivities match finite differences to 1e-6 relative error, and the predicted spread for 5 percent parts is within 1 percent of the 20000-draw Monte Carlo value (shipped: 20000 solves; the shipped prediction only handles four equal resistors).

**Difficulty:** advanced

## Session 8: Time enters: the RC circuit

**You will learn:** Capacitors as time-dependent stamps and the backward Euler step.

**You will build:** A transient solver for a resistor and a capacitor on a step input.

**Checkpoint (not met by the shipped code):** The time to reach 63.2 percent of the final voltage is within 1 percent of R C for a stable time step (the shipped solver has no time at all).

**Difficulty:** advanced

## The final step

Combine the milestones: read a netlist from a text file, sweep one component, and export an animated schematic that shows every node voltage, every branch current and the Thevenin load line of a chosen port, like the Target animation. If your result looks like the Target, open a pull request and tell us how you did it.
