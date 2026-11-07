# Roadmap: the path to the opensolarbattery Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Robust sizing over many weather years

**You will learn:** Why one simulated year is one sample, and how to size for a percentile of years instead of a single lucky year.

**You will build:** A search that evaluates every candidate design over many seeds and keeps a design meeting the target in most of them.

**Checkpoint (not met by the shipped code):** A design that reaches energy reliability of at least 0.90 in at least 95 of 100 random years at cloudiness 0.5 (the shipped single-year optimum 2.5 kW + 7 kWh does it in only 15).

**Difficulty:** intermediate

## Session 5: A smarter search

**You will learn:** How to find a good design without trying every grid point: staged or gradient-free search.

**You will build:** An optimiser that replaces the 500-design grid.

**Checkpoint (not met by the shipped code):** Finds the grid's best design (2.5 kW + 7 kWh for target 0.9) using at most 60 year-simulations (the shipped search uses 500).

**Difficulty:** intermediate

## Session 6: Backup for a power cut

**You will learn:** Sizing for resilience: a battery that must ride through an outage, not only save money.

**You will build:** A critical-load model and an outage scenario in the yearly simulator.

**Checkpoint (not met by the shipped code):** A design that supplies a 1 kW critical load for 24 hours with no unmet energy at round-trip efficiency 0.9 (it needs about 25.3 kWh stored; the shipped cost-optimal design has 7 kWh and runs out after about 6.6 hours).

**Difficulty:** advanced

## Session 7: Real weather and real demand

**You will learn:** How to compare a toy model with measured data and say how far to trust it.

**You will build:** A loader for an hourly irradiance file and a smart-meter file, with the same battery code.

**Checkpoint (not met by the shipped code):** Model monthly solar totals within 10 percent of the measured totals in all 12 months, or a written explanation of the months that miss.

**Difficulty:** advanced

## Session 8: Reproduce the Target animation

**You will learn:** Turning hourly simulation output into an energy-flow animation and a Pareto chart.

**You will build:** A 24-hour animation of one simulated day with flow arrows and a battery level, plus the cost-versus-reliability chart.

**Checkpoint (not met by the shipped code):** A GIF of at most 60 frames under 3 MB whose battery level and grid import in every frame match the simulation to 0.01 kWh.

**Difficulty:** advanced

## The final step

Combine the milestones: a robust, searched design for your own bill, tested on real weather, with a backup check and a clean energy-flow animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
