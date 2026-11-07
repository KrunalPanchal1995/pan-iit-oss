# Roadmap: the path to the openohm Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Network synthesis for any target

**You will learn:** Searching mixed E12 series and parallel pairs, and why two parts can already be very accurate.

**You will build:** A function that, for any target resistance from 10 to 1000 ohm, returns the best network of at most two different E12 resistors.

**Checkpoint (not met by the shipped code):** Worst-case error below 1 percent over 300 log-spaced targets between 10 and 1000 ohm (the shipped identical-resistor grids give 4.0 percent at worst with up to 8 parts).

**Difficulty:** intermediate

## Session 5: Self-heating resistor

**You will learn:** A resistance that depends on its own temperature and the fixed-point iteration that solves it.

**You will build:** A heater model R(T) = R0 (1 + alpha (T - T0)) with a thermal resistance to the surroundings.

**Checkpoint (not met by the shipped code):** The iterated steady-state temperature agrees with the closed-form solution of the quadratic to within 0.1 percent (the shipped code has no temperature at all).

**Difficulty:** intermediate

## Session 6: Tolerance and Monte Carlo

**You will learn:** How 5 percent resistors turn one design number into a distribution.

**You will build:** A Monte Carlo run of the 2 x 3 grid with random resistor values.

**Checkpoint (not met by the shipped code):** The simulated 99 percent interval of the current is within 5 percent of the interval predicted from the tolerance (the shipped code treats parts as exact).

**Difficulty:** advanced

## Session 7: Real battery and maximum power transfer

**You will learn:** Internal resistance and why the load that gets the most power is not the biggest or smallest one.

**You will build:** A battery with internal resistance r feeding a load R, with the power in the load swept over R.

**Checkpoint (not met by the shipped code):** The load that maximises load power is found to within 1 percent of R = r (the shipped supply is ideal, which has no maximum).

**Difficulty:** advanced

## Session 8: Add a capacitor: the RC time constant

**You will learn:** A first time-dependent circuit and exponential charging.

**You will build:** A numerical step response of a resistor and capacitor in series.

**Checkpoint (not met by the shipped code):** The time to reach 63.2 percent of the supply is within 1 percent of R C for a stable step size.

**Difficulty:** advanced

## The final step

Combine the milestones: a solver that takes a supply, a current and power limit and a tolerance, and returns a safe network of standard parts with a validated operating point. If your result looks like the Target animation, open a pull request and tell us how you did it.
