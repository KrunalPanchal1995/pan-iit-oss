# Roadmap: the path to the openabel Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 6: Use neighbouring rows

**You will learn:** Smoothing along the flame height before inverting (averaging the left and right halves is already done in Session 5).

**You will build:** A whole-image inversion of all 20 rows with less noise than row-by-row inversion.

**Checkpoint (not met by the shipped code):** RMS error over the full 20-row slice at or below 0.025 of the peak at 3 percent noise (the shipped row-by-row inversion gives 0.039 at lam = 3 with one half of the photo and 0.034 with both halves, as in Session 5).

**Difficulty:** advanced

## Session 7: Keep the hollow base hollow

**You will learn:** Constraints (non-negative emission) and penalties that preserve sharp structure better than a second-difference penalty.

**You will build:** An inversion that keeps the dark core of the candle base without negative values.

**Checkpoint (not met by the shipped code):** At z = 4 mm the recovered axis-to-peak ratio is within 0.03 of the true value 0.60 and no emission is negative (the shipped smoothed row gives 0.66 and small negative values appear for heavy smoothing).

**Difficulty:** advanced

## Session 8: Render it in 3D and animate

**You will learn:** Spinning an axisymmetric slice into a 3D volume and showing a cut-away.

**You will build:** A looping 3D cut-away animation of the recovered flame.

**Checkpoint (not met by the shipped code):** A 48-frame loop of one full turn whose first and last frames differ by less than 1e-6 and whose title shows the RMS error against the true emission.

**Difficulty:** advanced

## The final step

Combine the milestones: from one noisy side-view photo, find the axis, choose the smoothing automatically, invert the whole image and render a rotating 3D cut-away of the flame. If your result looks like the Target animation, open a pull request and tell us how you did it.
