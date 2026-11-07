# Roadmap: the path to the openflame Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Glare-corrected height

**You will learn:** How a veiling-glare halo lifts the background and fools a fixed threshold, and how to correct it (Atlas chapter S114).

**You will build:** An extractor that estimates and subtracts the glare field before thresholding.

**Checkpoint (not met by the shipped code):** On the shipped synthetic video with an added halo (peak brightness 0.3, 30 px wide, centred 33 px up the axis) the mean height error is below 0.5 px (the shipped extractor over-reads by about 1.7 px).

**Difficulty:** intermediate

## Session 5: Resolve aliasing with two frame rates

**You will learn:** Why one aliased clip is ambiguous and how a second frame rate picks out the true frequency.

**You will build:** A function that takes two measured apparent frequencies at two frame rates and returns the unique true frequency, or refuses.

**Checkpoint (not met by the shipped code):** A 17 Hz flicker filmed at 30 fps (apparent 13 Hz) and 24 fps (apparent 7 Hz) is recovered as 17.0 +- 0.2 Hz (the shipped single-rate measurement reports 13 Hz).

**Difficulty:** intermediate

## Session 6: The kymograph: convection speed

**You will learn:** How a space-time picture of the flame axis turns the slope of the stripes into the speed of the rising puffs (Atlas chapter S116).

**You will build:** A kymograph builder and a stripe-slope estimator.

**Checkpoint (not met by the shipped code):** The puff speed of a synthetic clip with a known speed is recovered within 10 percent (the shipped code produces no speed at all).

**Difficulty:** advanced

## Session 7: Detect the onset of flicker

**You will learn:** How a steady flame becomes a puffing one, and how to find the time at which the oscillation starts to grow (Atlas chapters S118 and S120).

**You will build:** A sliding-window amplitude estimate with a change-point detector.

**Checkpoint (not met by the shipped code):** On a synthetic clip whose flicker amplitude starts growing at 6 s the onset is located within 0.5 s (the shipped code fits one stationary sinusoid and cannot give a time).

**Difficulty:** advanced

## Session 8: A pipeline that refuses to guess

**You will learn:** How real footage differs from the test video (variable frame rate, auto-exposure, compression) and why a program should refuse a number it cannot support.

**You will build:** A measurement wrapper that reads timestamps, calibrates the scale from a ruler frame and refuses a frequency near the Nyquist limit.

**Checkpoint (not met by the shipped code):** A 9 Hz flicker filmed at 15 fps (above its Nyquist limit) produces a refusal instead of the number the shipped code reports, 6 Hz.

**Difficulty:** advanced

## The final step

Combine the milestones: a program that reads a real phone clip, corrects the glare, measures the height with an honest uncertainty, resolves or refuses the flicker frequency and reports when the oscillation began. If your result looks like the Target animation, open a pull request and tell us how you did it.
