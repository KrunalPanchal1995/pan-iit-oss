# Roadmap: the path to the openoscillator Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Chaos in the driven pendulum

**You will learn:** Why a driven, damped, nonlinear pendulum can be unpredictable, and what sensitive dependence on starting conditions means.

**You will build:** A driven version of the RK4 pendulum with phase portrait and a pair of nearby starting angles.

**Checkpoint (not met by the shipped code):** For theta'' = -sin(theta) - 0.5 theta' + 1.2 cos(2t/3), two runs starting at 0.2 rad and 0.2 + 1e-8 rad differ by more than 1 rad before t = 150 s (the shipped pendulum is undriven and can never separate two runs like this).

**Difficulty:** advanced

## Session 5: Fit a phone recording

**You will learn:** How to extract frequency and decay rate from noisy data with a least-squares fit.

**You will build:** A fitting function for a damped cosine and a synthetic 'accelerometer recording' to test it.

**Checkpoint (not met by the shipped code):** On a synthetic 2 Hz recording sampled at 100 Hz with 5 percent noise, recover the frequency within 1 percent and the decay rate within 10 percent (the shipped code measures a period from zero crossings only and has no fit).

**Difficulty:** intermediate

## Session 6: Coupled pendulums and beats

**You will learn:** Normal modes and why two linked oscillators trade energy back and forth.

**You will build:** Two identical pendulums joined by a weak spring, simulated with RK4.

**Checkpoint (not met by the shipped code):** The beat period of the simulation is within 2 percent of 2 pi / (w2 - w1), where w1 = sqrt(g/L) and w2 = sqrt(g/L + 2 kc/m) (the shipped code has a single oscillator).

**Difficulty:** intermediate

## Session 7: Pumping a swing: parametric resonance

**You will learn:** How changing the length at twice the natural frequency makes the amplitude grow, as a child does on a swing.

**You will build:** A small-angle pendulum whose length is modulated in time.

**Checkpoint (not met by the shipped code):** With 5 percent length modulation at twice the natural frequency, the amplitude grows by a factor of at least 3 in 20 periods (the shipped code keeps L constant).

**Difficulty:** advanced

## Session 8: Hardening spring: the resonance curve bends

**You will learn:** How a nonlinear spring makes the resonance peak lean and jump, and why up and down frequency sweeps differ.

**You will build:** A driven oscillator with a cubic spring term, swept up and then down in frequency.

**Checkpoint (not met by the shipped code):** The up-sweep and down-sweep amplitude curves disagree by a visible jump at different driving frequencies; the shipped linear driven oscillator gives identical curves in both directions.

**Difficulty:** advanced

## The final step

Combine the milestones: a driven nonlinear pendulum with phase portrait, energy bars and a resonance curve fitted to a recording you made yourself, tuned to a period you chose. If your result looks like the Target animation, open a pull request and tell us how you did it.
