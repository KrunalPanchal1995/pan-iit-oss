# Roadmap: the path to the openpinn Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Fourier features for fast-varying solutions

**You will learn:** Why small tanh networks learn smooth patterns first (spectral bias) and how sine and cosine input features fix it.

**You will build:** The heat-equation network with sine and cosine features of x added to its input.

**Checkpoint (not met by the shipped code):** A relative L2 error below 0.05 for the start sin(3 pi x) with at most 40 hidden units (the shipped network gives above 0.3).

**Difficulty:** intermediate

## Session 5: Exact boundary and initial conditions

**You will learn:** Building the conditions into the network so they hold exactly instead of being penalised.

**You will build:** An ansatz such as u = sin(pi x) + t x (1 - x) N(x, t) with derivatives worked out by hand.

**Checkpoint (not met by the shipped code):** The largest |u| at the two ends is exactly 0 (the shipped network gives above 0.01) with a relative L2 error below 0.02.

**Difficulty:** intermediate

## Session 6: A trustworthy inverse estimate

**You will learn:** Why the estimate of alpha wanders during training and how to decide when to stop.

**You will build:** An inverse run with a stopping rule and an error bar from several seeds.

**Checkpoint (not met by the shipped code):** On the default readings the recovered alpha is within 2 percent of 0.1 (the shipped run misses by more than 2 percent).

**Difficulty:** advanced

## Session 7: Two space dimensions

**You will learn:** The heat equation u_t = alpha (u_xx + u_yy) on a square and how derivatives in two directions are computed.

**You will build:** A network u(x, y, t) with a second derivative in each direction, checked against finite differences.

**Checkpoint (not met by the shipped code):** A relative L2 error below 0.05 against sin(pi x) sin(pi y) exp(-2 alpha pi^2 t), with the formulas verified by finite differences.

**Difficulty:** advanced

## The final step

Combine the milestones: a network with Fourier features and exact boundary conditions that solves a 2D heat problem and recovers its diffusivity from sparse noisy readings, with an animation of the training. If your result looks like the Target animation, open a pull request and tell us how you did it.
