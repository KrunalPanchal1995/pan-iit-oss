# Roadmap: the path to the openrcfilter Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A notch that nulls 50 Hz

**You will learn:** Moving-average and notch filters, and why a zero placed exactly on the hum beats a slow low-pass.

**You will build:** A filter for the temperature sensor with a null at 50 Hz that is still fast.

**Checkpoint (not met by the shipped code):** At most 0.001 C of hum left and 90 percent of the step reached within 0.05 s (the best shipped filter with that little hum needs 0.19 s).

**Difficulty:** intermediate

## Session 5: Zero-phase filtering for recordings

**You will learn:** Running a filter forwards and backwards so that the delay cancels, and what it cannot do in real time.

**You will build:** An offline filter that smooths a recorded trace without shifting it.

**Checkpoint (not met by the shipped code):** A 1 Hz test wave shifted by at most 2 ms while the hum limit of 0.02 C is met (the best shipped filter that meets it shifts it by 22 ms).

**Difficulty:** intermediate

## Session 6: Anti-alias filter and decimation

**You will learn:** Filtering before throwing samples away, and choosing the filter order for a given alias rejection.

**You will build:** A pipeline that samples at 2000 Hz, filters, and keeps every tenth sample.

**Checkpoint (not met by the shipped code):** A 180 Hz tone leaves at most 0.003 of its amplitude at the 20 Hz alias after decimation to 200 Hz (the shipped 20 Hz biquad leaves 0.012).

**Difficulty:** intermediate

## Session 7: Measure a real Bode plot

**You will learn:** Driving a real RC filter with a sound card or microcontroller and extracting gain and phase.

**You will build:** A measurement script and a breadboard filter that produce a measured Bode plot.

**Checkpoint (not met by the shipped code):** Measured gain within 1 dB of the prediction from the component values at five frequencies from f_c / 10 to 10 f_c.

**Difficulty:** advanced

## Session 8: Reproduce the Target animation

**You will learn:** Animating a Bode curve and a filtered trace from the same cutoff, with the delay marked.

**You will build:** A looping animation of a cutoff sweep with the gain curve on one side and the noisy and filtered signals on the other.

**Checkpoint (not met by the shipped code):** A loop of at least 40 frames whose first and last frames differ by less than 1e-6 and that shows the measured delay in milliseconds for every frame.

**Difficulty:** advanced

## The final step

Combine the milestones: a complete sensor front end with an analog anti-alias filter, a sampler, a fast notch-based digital filter and a measured Bode plot of the real circuit, shown with an animation like the Target. If your result looks like the Target animation, open a pull request and tell us how you did it.
