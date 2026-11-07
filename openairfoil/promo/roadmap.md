# Roadmap: the path to the openairfoil Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A laminar boundary layer (Thwaites)

**You will learn:** How the panel-method surface speed drives the growth of the boundary layer, and what the momentum thickness means.

**You will build:** Thwaites' integral method marching along each surface from the stagnation point, using the panel Vt.

**Checkpoint (not met by the shipped code):** On a flat plate (Vt = 1) the momentum thickness matches Blasius, 0.664 x / sqrt(Re_x), within 2 percent (the shipped code has no boundary layer).

**Difficulty:** intermediate

## Session 5: Transition and a turbulent boundary layer

**You will learn:** Why the boundary layer turns turbulent and why turbulent layers rub harder but resist separation.

**You will build:** Michel's transition criterion and Head's entrainment method, with the drag from the Squire-Young formula at the trailing edge.

**Checkpoint (not met by the shipped code):** NACA 0012 at 0 degrees and Re = 6 million gives cd between 0.005 and 0.0065, close to the smooth wind-tunnel value of about 0.0055 (the shipped flat-plate estimate gives 0.0085).

**Difficulty:** advanced

## Session 6: The drag polar of an airfoil

**You will learn:** How drag grows with angle as the upper-surface layer thickens.

**You will build:** cd from Session 5 for a sweep of angles, plotted as cl against cd, with the best section L/D marked.

**Checkpoint (not met by the shipped code):** For NACA 2412 at Re = 3 million cd at 6 degrees is larger than at 0 degrees, and the best section L/D occurs at a positive angle (the shipped estimate has the same cd at every angle).

**Difficulty:** intermediate

## Session 7: Separation and an estimate of stall

**You will learn:** Why the flow leaves the surface in a strong adverse pressure gradient and how CL_max follows.

**You will build:** Detect separation from the shape factor H of the turbulent layer and reduce the effective lift as the separated part grows.

**Checkpoint (not met by the shipped code):** NACA 0012 at Re = 6 million gives a CL_max between 1.3 and 1.7 at an angle between 12 and 18 degrees (the shipped panel CL grows without limit).

**Difficulty:** advanced

## Session 8: From airfoil to wing (Prandtl lifting line)

**You will learn:** How a finite wing's lift slope and induced drag follow from its span loading.

**You will build:** A lifting-line solver with a Fourier series for the circulation along the span, fed with the section lift slope from Session 3.

**Checkpoint (not met by the shipped code):** An elliptical wing gives e = 1 within 1 percent and a lift slope a0 / (1 + a0 / (pi AR)) within 1 percent (the shipped polar takes e as a given number).

**Difficulty:** advanced

## The final step

Combine the milestones: the panel method with a laminar and turbulent boundary layer, transition, separation and a lifting-line wing, drawn as pressure, streamlines, boundary-layer thickness and a drag polar with stall. If your NACA 0012 and 2412 results land near the wind-tunnel values quoted in the Target, open a pull request and tell us how you did it.
