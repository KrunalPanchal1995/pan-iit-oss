# Roadmap: the path to the openbuildingsway Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 5: Rayleigh damping instead of modal damping

**You will learn:** Why real models often use C = a0 M + a1 K, and what it does to the high modes.

**You will build:** A damping matrix built from two coefficients that give 5 percent at modes 1 and 3.

**Checkpoint (not met by the shipped code):** With 5 percent at modes 1 and 3 your damping ratios are 3.9 percent in mode 2 and 11.5 percent in mode 10 (the shipped model has 5 percent in every mode).

**Difficulty:** intermediate

## Session 6: Tune the mass damper

**You will learn:** How a tuned mass damper trades its mass ratio, frequency tuning and damping against sway on a broadband record.

**You will build:** A search over damper tuning and damper damping, averaged over six random records.

**Checkpoint (not met by the shipped code):** A damper of at most 3 percent of the building mass that cuts the peak roof sway to at most 70 percent of the bare frame on average over seeds 1 to 6 (the shipped damper tuned exactly to mode 1 with 3 percent mass gives 79 percent).

**Difficulty:** advanced

## Session 7: A real record and real periods

**You will learn:** How a real accelerogram differs from the synthetic one: duration, non-stationarity and the dominant period.

**You will build:** A loader for a public ground-motion record, with the dominant period found from its Fourier spectrum.

**Checkpoint (not met by the shipped code):** A table for at least three real records with the dominant period and the peak roof sway of the 10-storey frame, plus one paragraph on why the ranking differs from the synthetic case.

**Difficulty:** advanced

## Session 8: Yielding and torsion

**You will learn:** What changes when the columns yield (permanent drift) or when mass and stiffness are not centred (twist).

**You will build:** Elastic-perfectly-plastic storeys in the Newmark solver, and a plan-view model with an eccentric mass.

**Checkpoint (not met by the shipped code):** A residual first-storey drift clearly larger than the 4.4 mm with which the shipped linear model ends, and a symmetric plan that reproduces the planar periods of Session 3 to 1e-9.

**Difficulty:** advanced

## The final step

Combine the milestones: a ten-storey frame with yielding storeys and a tuned mass damper, shaken by real records, that reports mode shapes, drift and base shear in a clean animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
