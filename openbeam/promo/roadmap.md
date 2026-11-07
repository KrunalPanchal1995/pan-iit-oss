# Roadmap: the path to the openbeam Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 5: Lightest I-section by search

**You will learn:** How a free choice of flange width, flange thickness, web thickness and depth lowers the mass, and the limits (slenderness, flange outstand) that stop it going absurd.

**You will build:** A search over I-section dimensions for the footbridge girder, with the proportion limits you choose and state.

**Checkpoint (not met by the shipped code):** A passing section with a mass of at most 22 kg/m (the shipped fixed-flange table gives 31.6 kg/m).

**Difficulty:** intermediate

## Session 6: Shear deformation (Timoshenko element)

**You will learn:** Why deep beams sag more than Euler-Bernoulli theory says, and the shear correction factor.

**You will build:** A beam element that includes shear deformation.

**Checkpoint (not met by the shipped code):** For a centre-loaded rectangular beam with L/h = 5, the mid-span deflection matches P L^3 / (48 E I) + P L / (4 kappa G A) within 1%, where the shipped solver is about 11% too small.

**Difficulty:** advanced

## Session 7: Depth-versus-weight explorer

**You will learn:** Turn a design search into an animated explorer: moving load, linked diagrams and a trade-off chart (Session 4 gives you the envelope to build on).

**You will build:** An animation or app that shows the beam, the shear, moment and deflection diagrams and the lightest passing depth for any span.

**Checkpoint (not met by the shipped code):** For spans of 4 m to 10 m, the lightest passing depth read from your chart is within 5 mm of an exhaustive search.

**Difficulty:** advanced

## The final step

Combine the milestones: a beam explorer where a moving load crosses the span, the shear, moment and deflection diagrams follow it, and a trade-off chart gives the lightest passing section. If your result looks like the Target animation, open a pull request and tell us how you did it.
