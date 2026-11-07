# Roadmap: the path to the openclimate Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A two-box ocean

**You will learn:** Why the deep ocean slows the surface warming for decades and makes part of the warming arrive only after centuries.

**You will build:** A second, deep ocean box (heat capacity about 100 W yr/(m2 K)) linked to the surface layer by an exchange coefficient gamma (about 0.7 W/(m2 K)), stepped forward together.

**Checkpoint (not met by the shipped code):** With ECS = 3 K and CO2 rising 1 percent a year, the warming at doubling (year 70) is below 2.2 K (the shipped one-box model gives 2.68 K), and the equilibrium is still 3.0 K.

**Difficulty:** intermediate

## Session 5: Feedbacks one by one

**You will learn:** The Planck, water-vapour, lapse-rate, ice-albedo and cloud feedbacks and why their sum sets the climate sensitivity.

**You will build:** A lambda made of named parts (IPCC AR6 central values) and an ice-albedo feedback in which the albedo falls as the planet warms.

**Checkpoint (not met by the shipped code):** With the AR6 central feedback values the model's ECS lies between 2.5 and 4 K, and switching off the water-vapour feedback alone lowers it below 2 K (the shipped code has one lumped lambda).

**Difficulty:** intermediate

## Session 6: Other gases and aerosols

**You will learn:** Why methane and nitrous oxide forcing grow with the square root of concentration, and why pollution aerosols cool.

**You will build:** Forcing functions for CH4 and N2O and a simple aerosol forcing, added to the CO2 forcing.

**Checkpoint (not met by the shipped code):** Total forcing in 2019 from CO2, CH4 and N2O is between 2.9 and 3.4 W/m2, and adding an aerosol forcing of about -1.1 W/m2 brings the net close to the AR6 best estimate of about 2.7 W/m2.

**Difficulty:** intermediate

## Session 7: The historical record, 1850 to today

**You will learn:** How to drive a model with real data, compare it with observations, and estimate climate sensitivity from the fit.

**You will build:** A loader for a published annual forcing series and a global temperature record (both free), and a run of the two-box model from 1850.

**Checkpoint (not met by the shipped code):** The modelled warming for 2011 to 2020 relative to 1850 to 1900 lies within 0.15 K of the observed value of about 1.1 K, with an ECS between 2.5 and 4 K.

**Difficulty:** advanced

## Session 8: Carbon budgets and future paths

**You will learn:** Why warming is roughly proportional to total CO2 emitted, and what a carbon budget is.

**You will build:** A simple carbon cycle that turns emissions (GtC per year) into CO2 concentration, and three future emission paths.

**Checkpoint (not met by the shipped code):** The warming at the end of each path grows close to linearly with cumulative emissions (straight-line fit with r^2 above 0.95), about 0.45 K per 1000 GtCO2.

**Difficulty:** advanced

## The final step

Combine the milestones: a two-box ocean with named feedbacks, driven by the full historical forcing and continued along future paths, with the observed temperature record on the same graph. If your result reproduces the observed warming and you can explain every term in it, open a pull request and tell us how you did it.
