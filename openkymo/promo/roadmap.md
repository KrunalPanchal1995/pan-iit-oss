# Roadmap: the path to the openkymo Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Moving versus static stripes

**You will learn:** How to remove a stationary background (a fixed edge or reflection) so that it does not bias the slope.

**You will build:** A function that separates the moving stripes from the static ones before measuring.

**Checkpoint (not met by the shipped code):** On a kymograph with stripes (10, 0.7, amplitude 1), (40, 0.0, amplitude 1.5) and (70, 0.7, amplitude 0.8), 60 frames by 96 pixels, report 0.7 within 0.03 (the shipped gradient_speed gives 0.253).

**Difficulty:** intermediate

## Session 5: Stripes in both directions

**You will learn:** Velocity scanning: testing many candidate slopes and looking for peaks instead of one fit.

**You will build:** An estimator that returns every dominant velocity, not only one.

**Checkpoint (not met by the shipped code):** On two crossing stripes with +0.7 and -0.7 px/frame, return both within 0.05 (the shipped estimators return a single value near 0.000).

**Difficulty:** intermediate

## Session 6: Beat the noise

**You will learn:** Why combining all rows along candidate lines averages the noise down better than gradients.

**You will build:** A line-integral (Radon or shear-sum) speed estimator and its Monte Carlo study.

**Checkpoint (not met by the shipped code):** At noise 0.8 and true speed 0.7, the standard deviation over 30 noise seeds is below 5 percent of the speed (the shipped TLS gives a standard deviation of 0.278 over 60 seeds, about 40 percent).

**Difficulty:** advanced

## Session 7: Unwrap an aliased speed

**You will learn:** How two frame rates, or prior knowledge about the flow, resolve the ambiguity of aliasing.

**You will build:** A routine that uses two sub-sampled versions of the same data to find the true shift.

**Checkpoint (not met by the shipped code):** For a cosine of wavelength 8 px moving 5 px/frame, return 5 within 0.3 (the shipped estimator returns -2.94).

**Difficulty:** advanced

## Session 8: A falling drop: speed along a curved stripe

**You will learn:** Local slope along a stripe that bends because the object accelerates.

**You will build:** A function that returns the local speed at every frame without hand-picked windows.

**Checkpoint (not met by the shipped code):** For a drop with x = 5 + 0.01 t^2 over 80 frames, report v(t) with a root-mean-square error below 0.05 px/frame (one global value from the shipped gradient_speed gives 0.46).

**Difficulty:** advanced

## The final step

Combine the milestones: a program that reads a short video, builds the kymograph, separates static from moving stripes, finds every velocity with its uncertainty and prints the flow speed in metres per second. If your result looks like the Target animation, open a pull request and tell us how you did it.
