# Roadmap: the path to the openmechanism Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Choose experiments well

**You will learn:** Optimal experiment design: which temperatures and fuel amounts shrink the uncertainty ellipse fastest.

**You will build:** A small design tool that, for a budget of 12 experiments, picks conditions that minimise the one-sigma uncertainty of both scale factors.

**Checkpoint (not met by the shipped code):** One-sigma uncertainty of ln s1 below 0.30 for 12 experiments with noise 0.05 (the shipped campaign gives 0.57).

**Difficulty:** intermediate

## Session 5: Fit an activation energy too

**You will learn:** Calibrating the slope of the Arrhenius line, not only a scale factor, and why temperature range matters.

**You will build:** A calibration with a parameter that shifts Ea of k2, plus its uncertainty.

**Checkpoint (not met by the shipped code):** The activation energy of k2 (60 kJ/mol in the toy truth) recovered to within 3 kJ/mol from 12 noisy experiments, with k1 held fixed (the shipped code fits scale factors only and reports no Ea).

**Difficulty:** intermediate

## Session 6: Survive a biased dataset

**You will learn:** Systematic errors, nuisance parameters and robust objectives.

**You will build:** A calibration in which one dataset carries an unknown offset, handled by an extra fitted offset or a robust objective.

**Checkpoint (not met by the shipped code):** With dataset 1 shifted by +0.2 in ln tau, the error of ln s1 below 0.3 (the shipped fit gives an error of 0.92).

**Difficulty:** advanced

## Session 7: Propagate the uncertainty into predictions

**You will learn:** Forward uncertainty: from a parameter ellipse to a prediction band at conditions with no data.

**You will build:** Sampling parameter sets from the ellipse and simulating the ignition delay at a new temperature.

**Checkpoint (not met by the shipped code):** The one-sigma band of ln tau at 850 K from 2000 samples within 15 percent of the linear prediction of about 0.10 (the shipped code makes no predictions with uncertainty).

**Difficulty:** advanced

## Session 8: Reproduce the Target

**You will learn:** Sequential assimilation: updating the estimate and its ellipse as each experiment arrives.

**You will build:** An animation of the curves converging onto the data while the ellipse shrinks.

**Checkpoint (not met by the shipped code):** After every added experiment the one-sigma uncertainty of ln s2 does not increase, and after 12 experiments it is below 0.06.

**Difficulty:** advanced

## The final step

Combine the milestones: a calibration that picks its own experiments, fits Arrhenius parameters with honest uncertainty, survives a biased dataset, predicts with a band and shows it as an animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
