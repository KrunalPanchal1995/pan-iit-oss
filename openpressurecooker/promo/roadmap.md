# Roadmap: the path to the openpressurecooker Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Real steam properties

**You will learn:** Why a constant latent heat is only approximate, and how real steam tables or a fitted equation do better.

**You will build:** A saturation-pressure function with a temperature-dependent latent heat or a fitted equation, compared with tabulated data.

**Checkpoint (not met by the shipped code):** Boiling point at 1000 kPa absolute within 0.3 degrees C of 179.9 degrees C (the shipped constant-latent-heat model gives 178.9, an error of 1.0).

**Difficulty:** intermediate

## Session 5: Heat loss and natural release

**You will learn:** A cooling model after the heat is turned off, and how food keeps cooking while the pressure falls.

**You will build:** A simulation extended with a heat-loss term and a cool-down phase after the heat is off.

**Checkpoint (not met by the shipped code):** With a cooling time constant of 20 minutes starting from the plateau, the extra doneness gained during cool-down is reported and lies between 12 and 18 equivalent boil minutes (the shipped model gives 0 because it stops at heat-off).

**Difficulty:** intermediate

## Session 6: Food with an inside

**You will learn:** Heat diffusion into a lentil, bean or potato, and why the centre lags the surface.

**You will build:** A radial diffusion solver coupled to the cooking rate.

**Checkpoint (not met by the shipped code):** The numerical decay of the lowest mode in a sphere matches exp(-pi^2 alpha t / R^2) within 2 percent; the shipped lumped model cannot report a centre-to-surface gap at all.

**Difficulty:** advanced

## Session 7: Altitude and the open pot

**You will learn:** Lower air pressure on a mountain, and how it changes the open-pot boiling point and cooking time.

**You will build:** The open-pot model with atmospheric pressure as an input, and a cooker setting that restores the sea-level time.

**Checkpoint (not met by the shipped code):** At 70 kPa (about 3000 m) the open-pot simmer takes between 2.0 and 2.3 times the sea-level time (the shipped model is fixed at sea-level pressure).

**Difficulty:** intermediate

## Session 8: Relief devices in the model

**You will learn:** Why there are several independent relief paths and how a second valve limits the worst case.

**You will build:** A second relief valve set above the regulator that opens in the blocked case, with the pressure traced over time.

**Checkpoint (not met by the shipped code):** In the blocked case the absolute pressure never exceeds 260 kPa (the shipped model reaches 300 kPa after 83 s past the regulator pressure and keeps rising); concepts only, with no instructions for real equipment.

**Difficulty:** advanced

## The final step

Combine the milestones: an animated cooker with gauge and temperature that includes heat loss, a natural release and food with an inside, racing against an open pot. If your result looks like the Target animation, open a pull request and tell us how you did it.
