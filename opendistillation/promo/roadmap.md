# Roadmap: the path to the opendistillation Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Energy balances on every tray

**You will learn:** Why constant molar overflow is only an approximation: the molar latent heats of ethanol (about 38.6 kJ/mol) and water (about 40.7 kJ/mol) differ, and mixing releases heat.

**You will build:** A stage-by-stage calculation with an enthalpy balance on every tray, so L and V change down the column, using liquid and vapour enthalpies from simple heat-capacity and latent-heat data.

**Checkpoint (not met by the shipped code):** For the Session 3 design (zF = 0.10, xD = 0.80, xB = 0.02, R = 1.587) the vapour flow differs by more than 2 percent between the top and the bottom of the rectifying section (the shipped model keeps it exactly constant), and the total energy balance (reboiler + feed = condenser + products) closes within 0.5 percent.

**Difficulty:** intermediate

## Session 5: Tray efficiency and real trays

**You will learn:** Real trays do not reach equilibrium; the Murphree vapour efficiency says how far each step goes towards the curve.

**You will build:** McCabe-Thiele stepping to a "pseudo-equilibrium" curve y = y_op + E_MV (y_eq - y_op), and a comparison with the overall efficiency of Session 3.

**Checkpoint (not met by the shipped code):** With E_MV = 0.6 the Session 3 separation needs between 18 and 24 real trays plus the reboiler, and with E_MV = 1 it gives back exactly the 13 stages of Session 3.

**Difficulty:** intermediate

## Session 6: Breaking the azeotrope

**You will learn:** How fuel-grade ethanol (above 99.5 percent by volume) is made: pressure-swing distillation, an entrainer, or molecular-sieve adsorption after the column.

**You will build:** A material and energy balance for a column making near-azeotrope ethanol followed by a molecular-sieve dryer, and a T-x-y study of how the azeotrope moves with pressure.

**Checkpoint (not met by the shipped code):** The flowsheet turns 100 kmol/h of wash (zF = 0.10) into a product with x of at least 0.99 and an overall ethanol recovery of at least 0.97 (the shipped code stops at the azeotrope).

**Difficulty:** intermediate

## Session 7: A dynamic column

**You will learn:** Every tray holds liquid, so compositions change in time; the column is a set of ordinary differential equations, one per tray.

**You will build:** Tray hold-ups and component balances dM x / dt = in - out on every stage, integrated in time from a cold, uniform start, with a simple liquid-flow (weir) relation.

**Checkpoint (not met by the shipped code):** Run long enough, the dynamic model settles to the Session 3 steady profile (every tray x within 0.005); after a step from zF = 0.10 to 0.12 the top composition settles to a new value with a time constant you report in minutes.

**Difficulty:** advanced

## Session 8: Controlling the column

**You will learn:** Why plants control a tray temperature instead of the product composition, and how a PI controller works.

**You will build:** A PI loop that adjusts the reflux ratio to hold the temperature of a sensitive tray, tested on the dynamic column of Session 7.

**Checkpoint (not met by the shipped code):** After a 20 percent feed-composition step, the controlled column keeps xD within 0.01 of 0.80 at steady state, while the uncontrolled column drifts by more than 0.02.

**Difficulty:** advanced

## The final step

Combine the milestones: a dynamic column with tray energy balances, real-tray efficiency and a temperature controller, animated from a cold start to the designed steady profile, with a dryer that turns its product into fuel-grade ethanol. If your result looks like the Target, open a pull request and tell us how you did it.
