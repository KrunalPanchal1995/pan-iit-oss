# Roadmap: the path to the openfridge Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Replace the toy fluid by real property data

**You will learn:** How real refrigerant properties are tabulated and interpolated, and how much an ideal-gas model misses.

**You will build:** A property function built from a published table for one real refrigerant, used in the same cycle code.

**Checkpoint (not met by the shipped code):** The cycle COP for evaporator -8 C and condenser 35 C agrees within 5 percent with an independent published reference value (the shipped toy fluid has no real reference at all).

**Difficulty:** intermediate

## Session 5: Superheat and subcooling

**You will learn:** Why real cycles add a few kelvin of subcooling after the condenser and superheat before the compressor.

**You will build:** Extend the cycle with two extra temperature offsets and show the effect on the P-h loop.

**Checkpoint (not met by the shipped code):** With 5 K of subcooling the heat taken per kilogram rises by cp x 5 = 4 kJ/kg, while the shipped cycle has none.

**Difficulty:** intermediate

## Session 6: Size the heat exchangers

**You will learn:** How the evaporator and condenser temperature offsets come from the heat-exchanger area (UA) and the heat flow.

**You will build:** Replace the fixed offsets of 8 K and 10 K by values found from UA values with an iterative solution.

**Checkpoint (not met by the shipped code):** With 150 W of cooling and a heat exchanger of UA = 22 W/K, the evaporator temperature for a 4 C food space converges to -2.8 C (the shipped model fixes it at 8 K below the inside, which is -4 C).

**Difficulty:** advanced

## Session 7: Thermostat cycling over a day

**You will learn:** On-off control, temperature swing and why the average power is less than the running power.

**You will build:** A time-stepping simulation of the inside temperature with a thermostat and a thermal mass.

**Checkpoint (not met by the shipped code):** A 24 hour simulation that keeps the air between 3 and 5 C while the daily energy matches the steady estimate within 15 percent (the shipped model has no time dependence).

**Difficulty:** advanced

## Session 8: Moisture and door openings

**You will learn:** How condensing water vapour adds latent heat to the door load.

**You will build:** An improved door-load model with humid air.

**Checkpoint (not met by the shipped code):** A door load of at least 2.5 W for 30 openings a day at 25 C and 60 percent relative humidity (the shipped sensible-only model gives 1.32 W).

**Difficulty:** advanced

## The final step

Combine the milestones: a full day simulation of a kitchen fridge with a pressure-dependent compressor, heat exchangers sized by area, subcooling and superheat, a thermostat and an animated P-h diagram with live energy flows and COP. If your result looks like the Target animation, open a pull request and tell us how you did it.
