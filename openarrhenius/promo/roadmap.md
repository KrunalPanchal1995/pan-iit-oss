# Roadmap: the path to the openarrhenius Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 5: Design the experiment for the prediction

**You will learn:** Optimal design: choosing temperatures to minimise the error at the target rather than the error of Ea.

**You will build:** A small optimiser over seven temperatures between 700 and 1100 K, requiring at least three distinct temperatures so linearity can be checked.

**Checkpoint (not met by the shipped code):** Expected standard error of ln k(2000 K) at 6 percent error of at most 0.067 (the shipped even spacing gives 0.0866).

**Difficulty:** intermediate

## Session 6: Bootstrap intervals

**You will learn:** Resampling the residuals instead of using the t distribution, and what small samples do to intervals.

**You will build:** A residual bootstrap of the 2000 K prediction.

**Checkpoint (not met by the shipped code):** For the mini-project data the bootstrap upper-to-lower factor is within 20 percent of the shipped formula's 1.78, with a written explanation of the difference.

**Difficulty:** intermediate

## Session 7: Three-parameter fits and their correlations

**You will learn:** The covariance of (ln A, n, Ea) in the modified Arrhenius form and why n and ln A cannot be separated over a limited range.

**You will build:** A fit_modified that also returns the 3 by 3 covariance and a correlation table.

**Checkpoint (not met by the shipped code):** The correlation of ln A and n has magnitude at least 0.999 for 12 temperatures between 500 and 1500 K, and the covariance is reported (the shipped fit returns no uncertainty).

**Difficulty:** intermediate

## Session 8: Animate it yourself

**You will learn:** Turning a fit into a frame-by-frame animation with matplotlib and Pillow.

**You will build:** Your own animation of points arriving, the line and band updating and the ellipse shrinking.

**Checkpoint (not met by the shipped code):** A GIF of at most 3 MB with at least 30 frames whose expected 95 percent factor at 2000 K (using the known sigma) falls at every frame.

**Difficulty:** advanced

## The final step

Combine the milestones: an experiment-design and fitting tool that handles curved plots, reports a joint uncertainty for the parameters and a prediction band at any temperature, and shows it as an animation. If your result looks like the Target animation, open a pull request and tell us how you did it.
