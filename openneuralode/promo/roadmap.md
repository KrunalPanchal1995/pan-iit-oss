# Roadmap: the path to the openneuralode Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: The adjoint method

**You will learn:** How a second ODE solved backwards gives the same gradient with memory that does not grow with the number of steps.

**You will build:** A gradient routine that integrates the adjoint equations backwards instead of storing the RK4 stages.

**Checkpoint (not met by the shipped code):** Agrees with the shipped backpropagation gradient to a relative gap of 1e-4 on the 62-parameter network while storing only the final state (the shipped code stores every step).

**Difficulty:** advanced

## Session 5: A limit cycle: Van der Pol

**You will learn:** Learning a nonlinear system whose paths settle onto a loop, and why the rollout horizon should grow during training.

**You will build:** A Neural ODE for the Van der Pol oscillator with a curriculum on the rollout length.

**Checkpoint (not met by the shipped code):** RMS state error below 0.1 after 6 s on 20 unseen starts (the shipped small network and recipe are far above this on Van der Pol).

**Difficulty:** intermediate

## Session 6: Stiff dynamics with an implicit solver

**You will learn:** Implicit solvers and step-size control, and why they remove the step limit of explicit RK4.

**You will build:** Backward Euler or an adaptive solver inside the rollout.

**Checkpoint (not met by the shipped code):** Solves x' = -1000 x with h = 0.01 s and ends below 1e-6 at 0.1 s, where the shipped explicit RK4 multiplies the state by 291 per step.

**Difficulty:** advanced

## Session 7: Learning under heavy noise

**You will learn:** Regularisation (weight decay, early stopping) and why eigenvalues of the learned flow are fragile.

**You will build:** A training recipe that stays accurate at noise 0.1 with only 6 runs.

**Checkpoint (not met by the shipped code):** Error after 6 s below 0.1 on the damped oscillator at noise 0.1 with 6 runs, for both data sets of the design check (the shipped recipe fails one of them).

**Difficulty:** intermediate

## Session 8: Hidden velocity: partial observation

**You will learn:** Augmented and latent Neural ODEs: learning a rule when only some state variables are measured.

**You will build:** A model that sees only the position of the oscillator and learns the velocity as a hidden state.

**Checkpoint (not met by the shipped code):** Position error below 0.1 over 6 s from position-only data (the shipped model needs both position and velocity).

**Difficulty:** advanced

## The final step

Combine the milestones: a Neural ODE that learns a nonlinear oscillator from noisy data, predicts it for many seconds, uses a step-size-safe solver and checks its own gradient with the adjoint method. If your result looks like the Target animation, open a pull request and tell us how you did it.
