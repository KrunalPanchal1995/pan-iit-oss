# Roadmap: the path to the openphasediagram Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Homogenising anneal

**You will learn:** How solid-state diffusion at high temperature removes coring, and how the time scales with the arm spacing.

**You will build:** A solid-state diffusion model across one dendrite arm with a heat treatment time.

**Checkpoint (not met by the shipped code):** Rim to core Sn ratio of a 10 wt% Sn Scheil casting reduced below 1.1 by the anneal (the shipped code gives 6.2 and has no anneal).

**Difficulty:** intermediate

## Session 5: Fit a diagram from cooling curves

**You will learn:** Thermal analysis: how metallurgists find liquidus and eutectic temperatures from arrests.

**You will build:** An inverse tool that reads simulated noisy cooling curves of several alloys and rebuilds the diagram.

**Checkpoint (not met by the shipped code):** Liquidus and eutectic temperatures recovered within 2 C and the eutectic composition within 2 wt% Sn from curves with 1 C noise (the shipped code only runs the forward problem).

**Difficulty:** intermediate

## Session 6: Peritectic and intermetallic diagrams

**You will learn:** Three-phase reactions beyond the eutectic and how the lever rule applies on each side.

**You will build:** A second diagram type with a peritectic and a compound, with phase fractions on both sides of the line.

**Checkpoint (not met by the shipped code):** Phase fractions in a peritectic alloy within 1 percent of a hand lever-rule calculation (the shipped code covers isomorphous and eutectic only).

**Difficulty:** advanced

## Session 7: A moving freezing front

**You will learn:** Why real castings freeze from the wall inward and how the solid shell grows with the square root of time.

**You will build:** A one-dimensional ingot with a heat-flow solver and the lever-rule enthalpy.

**Checkpoint (not met by the shipped code):** Solid thickness within 5 percent of the Stefan (square-root of time) solution for a pure metal (the shipped lumped model has no thickness at all).

**Difficulty:** advanced

## Session 8: Quench and age: a heat treatment

**You will learn:** Supersaturated solid solutions, a sloping solvus line, and precipitation hardening as a heat treatment.

**You will build:** A quench-then-age calculation using a solvus line that falls with temperature.

**Checkpoint (not met by the shipped code):** Equilibrium precipitate fraction at 100 C for a 15 wt% Sn alloy within 1 percent of a hand lever-rule value, using a solvus that falls from 19 wt% at 183 C to 2 wt% at 20 C (the shipped diagram stops the solvus at 183 C).

**Difficulty:** advanced

## The final step

Combine the milestones: a diagram tool that reads a cooling curve, predicts phase fractions at any temperature, shows coring for fast cooling and recommends an anneal. If your result looks like the Target animation, open a pull request and tell us how you did it.
