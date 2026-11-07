# Roadmap: the path to the openbatterycell Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 5: Pulse loads and recovery

**You will learn:** Why a cell sags under a heavy pulse and slowly recovers: a diffusion layer at the electrode with a time constant.

**You will build:** A surface-concentration state with a relaxation time that feeds the Nernst term, driven by a load that has pulses.

**Checkpoint (not met by the shipped code):** After a heavy pulse ends, the voltage is still at least 5 mV below its final value one minute later and has recovered at least 90 percent of the sag after ten minutes, for a time constant of about four minutes (the shipped model recovers instantly, a gap of 0 mV).

**Difficulty:** advanced

## Session 6: Rechargeable cell and cycle life

**You will learn:** Reversing the reaction, charge efficiency and capacity fade over many cycles.

**You will build:** A charge-discharge cycle simulation with a small loss of capacity per cycle.

**Checkpoint (not met by the shipped code):** With 0.2 percent capacity loss per cycle the model reports 90.5 percent of the starting capacity after 50 cycles (0.998 to the power 50); the shipped code has no cycling at all.

**Difficulty:** intermediate

## Session 7: Heat feeds back on resistance

**You will learn:** Coupling the lumped thermal model to the discharge: the cell warms, its resistance falls, the current rises.

**You will build:** A discharge simulation where the temperature changes in time instead of being fixed.

**Checkpoint (not met by the shipped code):** The energy balance (chemical = delivered + heat) still closes within 0.1 percent while the cell temperature rises by more than 0.5 K during a 2 ohm discharge (the shipped model keeps the temperature fixed).

**Difficulty:** advanced

## Session 8: Fit a real cell

**You will learn:** Estimating internal resistance and the discharge curve of a real AA cell from measurements.

**You will build:** A fitting script that reads a measured voltage-time table taken with a resistor load and adjusts r and the capacity.

**Checkpoint (not met by the shipped code):** The model voltage is within 20 mV of the measurement over 80 percent of the discharge (the shipped zinc-copper parameters do not describe an alkaline cell at all).

**Difficulty:** advanced

## The final step

Combine the milestones: a live animated cell with a pulse load, temperature feedback and a pack designer that sizes a battery for a lamp at several temperatures. If your result looks like the Target animation, open a pull request and tell us how you did it.
