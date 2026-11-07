# Roadmap: the path to the openunits Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Parse compound unit strings

**You will learn:** How a units library reads names like 'kN', 'mm/s^2' and 'kg*m/s^2' by splitting prefixes and powers.

**You will build:** A parser that builds the dimension and SI size of any compound unit string.

**Checkpoint (not met by the shipped code):** Correctly parses 20 given unit strings, including prefixed and compound ones (the shipped `UNITS` table only knows 16 fixed names and fails on 'kN' and 'mm/s^2').

**Difficulty:** intermediate

## Session 5: Units at the file boundary

**You will learn:** Why data files should carry units, and how a reader can enforce it.

**You will build:** A reader for small data files with a unit header that converts to SI and refuses files without units.

**Checkpoint (not met by the shipped code):** Accepts 2 well-formed files and rejects 3 faulty ones (no unit, unknown unit, wrong dimension); the shipped code has no file reader.

**Difficulty:** intermediate

## Session 6: Carry the uncertainty

**You will learn:** Propagating relative errors through products and powers, and reporting the right significant figures.

**You will build:** A Quantity that stores a value with an uncertainty and updates it under multiply, divide and power.

**Checkpoint (not met by the shipped code):** The audit result dv = I / m with 1 percent in each input is reported with an uncertainty within 1 percent of the root-sum-of-squares value (the shipped class carries no uncertainty).

**Difficulty:** advanced

## Session 7: A real orbit under gravity

**You will learn:** Two-body motion around the Sun and a Runge-Kutta 4 integrator.

**You will build:** A planar transfer from Earth's orbit radius (1.496e11 m) to Mars's orbit radius (2.279e11 m) integrated step by step.

**Checkpoint (not met by the shipped code):** Over the half-ellipse the energy drifts by less than 1e-9 in relative terms and the final radius is within 0.01 percent of the target orbit radius (the shipped toy has no gravity at all).

**Difficulty:** advanced

## Session 8: Reproduce the Target

**You will learn:** How a unit mistake on small firings grows into a miss when gravity acts on the changed path.

**You will build:** The Target comparison: intended and actual position under gravity, with the distance between them against time.

**Checkpoint (not met by the shipped code):** For 12 firings of 0.2 lbf*s on a 600 kg craft, sideways to the velocity between day 10 and day 150, the miss at the end of a 258.8 day half-ellipse is within 5 percent of 250 km (the shipped toy model gives 119 km at day 180 and does not reach this).

**Difficulty:** advanced

## The final step

Combine the milestones: an orbit simulation that reads thruster data from a unit-carrying file, refuses anything without a unit, reports the miss with an uncertainty and reproduces the Target comparison. If your result looks like the Target animation, open a pull request and tell us how you did it.
