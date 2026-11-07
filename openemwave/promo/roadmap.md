# Roadmap: the path to the openemwave Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: An 8-element steerable array

**You will learn:** How many sources add up to a narrow beam, and how the phase step steers it.

**You will build:** A function that drives N sources with a progressive phase and measures the beam in the simulation.

**Checkpoint (not met by the shipped code):** A half-power beamwidth of at most 15 degrees at broadside and every side lobe at least 12 dB below the main beam, and the measured beam within 2 degrees of the commanded angle for five angles (the shipped two-source pair has a 60 degree beamwidth).

**Difficulty:** intermediate

## Session 5: A better absorbing boundary

**You will learn:** Why the first-order Mur rule echoes at oblique angles, and how a graded absorbing layer avoids it.

**You will build:** A matched absorbing layer around the grid.

**Checkpoint (not met by the shipped code):** The spurious echo in the `boundary_echo` test is below 0.5 percent of the pulse (the shipped Mur boundary gives 2.3 percent).

**Difficulty:** advanced

## Session 6: A dielectric slab

**You will learn:** Refractive index in FDTD: a medium where the wave is slower and the wavelength shorter.

**You will build:** A grid with a permittivity map and a slab of refractive index 2.

**Checkpoint (not met by the shipped code):** The measured wavelength inside the slab is half the vacuum wavelength within 3 percent (the shipped code has only vacuum, n = 1).

**Difficulty:** intermediate

## Session 7: Go 3D: a point source

**You will learn:** The full 3D Yee cell with six field components, and the 1/r law of a real radiating point source.

**You will build:** A 3D FDTD solver with a small radiating source.

**Checkpoint (not met by the shipped code):** A fitted amplitude exponent of -1.00 within 0.05 (the shipped 2D solver gives -0.50).

**Difficulty:** advanced

## Session 8: Animate and share the beam

**You will learn:** Recording frames and exporting an animation with a polar pattern next to the field.

**You will build:** A looping GIF of a steered beam.

**Checkpoint (not met by the shipped code):** A loop of at most 60 frames and 3 MB whose first and last frames look identical (differences below 1 percent of the colour range).

**Difficulty:** beginner

## The final step

Combine the milestones: an 8-element array with a good absorbing boundary that sweeps its beam while you watch the electric field. If your result looks like the Target animation, open a pull request and tell us how you did it.
