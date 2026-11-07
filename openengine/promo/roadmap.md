# Roadmap: the path to the openengine Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Temperature-dependent gas properties

**Status: done.** See [Session 4](../sessions/session-04/README.md).

**You will learn:** Why cp and cv grow with temperature and how this lowers the real efficiency.

**You will build:** The Otto cycle with cv(T) from a simple polynomial instead of a constant gamma.

**Checkpoint (met by the shipped code):** An ideal Otto efficiency at r = 9 and q_in = 1100 kJ/kg below 0.56 (the shipped constant-gamma model gives 0.585).

**Difficulty:** intermediate

## Session 5: The dual (Seiliger) cycle

**Status: done.** See [Session 5](../sessions/session-05/README.md).

**You will learn:** Real diesels add heat partly at constant volume and partly at constant pressure.

**You will build:** A function that splits the heat and returns efficiency and a P-V path.

**Checkpoint (met by the shipped code):** At r = 18 and 1100 kJ/kg a half-and-half split gives an efficiency strictly between the shipped Diesel (0.625) and Otto (0.685) values.

**Difficulty:** intermediate

## Session 6: T-S diagram from the simulation

**You will learn:** Entropy of an ideal gas and why the T-S area is heat.

**You will build:** Compute entropy along the simulated cycle and draw the T-S loop with the Carnot rectangle.

**Checkpoint (not met by the shipped code):** The enclosed T-S area equals the P-V net work within 0.5 percent for the Otto and Diesel cycles (the shipped code has no entropy).

**Difficulty:** intermediate

## Session 7: A knock model with engine speed

**You will learn:** Autoignition delay of the end gas and how it competes with the flame arrival.

**You will build:** An induction-time integral on the end-gas temperature history.

**Checkpoint (not met by the shipped code):** The knock-limited compression ratio is larger at 3000 rpm than at 1500 rpm (the shipped temperature rule gives the same value at both speeds).

**Difficulty:** advanced

## Session 8: Four strokes with a pumping loop

**You will learn:** Intake and exhaust strokes and the pumping work at part load.

**You will build:** Add gas exchange to the crank-angle model with a throttled intake.

**Checkpoint (not met by the shipped code):** At an intake pressure of 40 kPa the pumping mean effective pressure is at least 50 kPa (the shipped model has none).

**Difficulty:** advanced

## The final step

Combine the milestones: three cycles with temperature-dependent gas, T-S loops and a knock-limited compression ratio, animated side by side with live efficiency. If your result looks like the Target animation, open a pull request and tell us how you did it.

A first reproduction of the three ideal cycles, with its method, is in [target/README.md](../target/README.md); it reaches 0.585, 0.624 and 0.867. Making it use the milestones above (variable cp, the simulated cycle, a knock-limited r) is still open.
