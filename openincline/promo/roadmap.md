# Roadmap: the path to the openincline Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Slide angle on a curved surface

**You will learn:** How the local slope of a bowl or hill, instead of one angle, decides where a block can rest.

**You will build:** A simulation of a block on a hill profile y(x) with friction, finding where it can stay.

**Checkpoint (not met by the shipped code):** On the profile y = 0.3 sin(x) with mu_s = 0.25, the simulated resting region around the peak ends at x = 0.586 and x = 2.556, matching the exact condition |cos x| <= 0.833 to within 0.01 (the shipped code handles only one straight ramp).

**Difficulty:** intermediate

## Session 5: Stick-slip: a block pulled by a spring

**You will learn:** How the drop from static to kinetic friction produces jerky motion and oscillation.

**You will build:** A block on a surface pulled through a spring by a slowly moving end.

**Checkpoint (not met by the shipped code):** Reproduce a stick-slip cycle whose period matches the predicted value to within 5 percent for mu_s = 0.6, mu_k = 0.4 (the shipped simulation has no spring).

**Difficulty:** intermediate

## Session 6: A phase map of stick versus slide

**You will learn:** Mapping behaviour over two parameters at once, and finding the boundary automatically.

**You will build:** A map over (angle, friction coefficient) coloured by the simulated outcome.

**Checkpoint (not met by the shipped code):** A 100 by 100 map whose boundary matches tan t = mu to within one grid cell, computed by the simulation and not by the formula (the shipped code tests single cases only).

**Difficulty:** intermediate

## Session 7: Tip or slide: finite block size

**You will learn:** How the height and width of a block decide whether it tips over before it slides.

**You will build:** A block with a centre of mass height h and base width w on a ramp.

**Checkpoint (not met by the shipped code):** Predict the angle where a block of width 0.2 m and height 0.5 m tips (arctan(w/h) = 21.8 degrees) and show that it is below the slide angle for mu = 0.6.

**Difficulty:** advanced

## Session 8: Rolling with slipping

**You will learn:** What happens when a cylinder rolls and slips at the same time, using kinetic friction and rotation.

**You will build:** A solid cylinder on a steep ramp with low friction.

**Checkpoint (not met by the shipped code):** Show that for mu_k = 0.1 at 50 degrees the cylinder slips, and that its acceleration g (sin t - mu_k cos t) differs from the rolling value by more than 20 percent (the shipped code only checks the no-slip condition).

**Difficulty:** advanced

## The final step

Combine the milestones: an animated ramp with force vectors and a stick-or-slide map computed by your own simulation, including the effect of an uncertain friction coefficient. If your result looks like the Target animation, open a pull request and tell us how you did it.
