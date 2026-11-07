# Roadmap: the path to the openprocesssim Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Equation-oriented solving with Newton

**You will learn:** Treat the tear stream as unknowns and solve the loop with Newton's method and a numerical Jacobian instead of iterating.

**You will build:** A Newton solver for the tear stream of the mini-project loop, with a damped step.

**Checkpoint (not met by the shipped code):** Starting after one substitution pass, the tear change falls below 1e-10 in at most 3 Newton steps (the shipped code needs 18 substitution iterations and 7 Wegstein iterations); a plain Newton start from a zero guess does not converge, so add damping or a safe start.

**Difficulty:** intermediate

## Session 5: Non-ideal activity models

**You will learn:** Activity coefficients, and why Raoult's law fails for ethanol and benzene.

**You will build:** Replace K = P_sat / P with K = gamma P_sat / P using a simple two-parameter model.

**Checkpoint (not met by the shipped code):** A minimum-boiling azeotrope between 340 and 342 K at an ethanol mole fraction between 0.40 and 0.55 at 1 atm (the shipped Raoult model never goes below 351.5 K).

**Difficulty:** advanced

## Session 6: A rigorous distillation column

**You will learn:** Stage-by-stage balances with reflux, the step beyond a single flash.

**You will build:** A column block with N stages, reflux ratio and a feed stage.

**Checkpoint (not met by the shipped code):** With 10 stages, reflux ratio 3 and a saturated equimolar benzene-toluene feed of 100 mol/s, a distillate of 50 mol/s with at least 0.95 benzene (the best single flash gives at most 0.714).

**Difficulty:** advanced

## Session 7: A graphical flowsheet editor

**You will learn:** A file format for flowsheets and a browser editor that draws boxes and pipes.

**You will build:** Save a flowsheet as JSON from a drawing, load it into the engine and solve it.

**Checkpoint (not met by the shipped code):** The mini-project drawn in the editor loads and gives a recycle flow of 146.66 mol/s, and a drawing with a missing flash temperature is refused with the same under-specified message as the shipped engine (the shipped code has no file format).

**Difficulty:** intermediate

## Session 8: A property package

**You will learn:** Keep component data (Antoine constants, heat capacity, heat of vaporisation) in a table instead of in the code.

**You will build:** A data file and loader, with water added as a fourth component.

**Checkpoint (not met by the shipped code):** The loader reproduces the shipped boiling points of benzene, toluene and ethanol (353.2, 383.8 and 351.5 K), and pure water boils within 0.3 K of 373.15 K at 1 atm (the shipped code has three hard-wired components).

**Difficulty:** intermediate

## The final step

Combine the milestones: a small open process simulator that loads a drawn flowsheet, picks a thermodynamic model, solves recycles with Newton, and animates the pipes and convergence. If your result looks like the Target animation, open a pull request and tell us how you did it.
