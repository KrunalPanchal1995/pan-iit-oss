# Roadmap: the path to the openheartflow Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: A three-element Windkessel

**You will learn:** Why a real aorta shows a sudden pressure jump at the start of ejection, and how a characteristic impedance in series with the two elements explains it.

**You will build:** A model with a resistor in series with the compliance and resistance, solved with your own RK4.

**Checkpoint (not met by the shipped code):** The input pressure rises by at least 5 mmHg within the first 0.02 s of ejection (the shipped two-element model falls by 0.2 mmHg in that time), while the mean pressure still equals R times the mean flow.

**Difficulty:** intermediate

## Session 5: Add a heart valve and let the stroke volume emerge

**You will learn:** How a ventricle with a one-way valve ejects only while its pressure is above the artery, so stroke volume depends on the load.

**You will build:** A ventricle pressure model coupled to the Windkessel through a valve.

**Checkpoint (not met by the shipped code):** The stroke volume falls by at least 5 mL when R rises by 30 percent with the ventricle unchanged (in the shipped model it stays at 70 mL by construction), and no blood flows backwards.

**Difficulty:** advanced

## Session 6: Arteries that stiffen with pressure

**You will learn:** Why compliance is not a constant: arteries are stiffer at high pressure, and what that does to the pulse pressure.

**You will build:** A pressure-dependent compliance C(P) in the same RK4 solver.

**Checkpoint (not met by the shipped code):** The pulse pressure at a mean pressure of 130 mmHg is at least 1.5 times that at a mean pressure of 90 mmHg for the same stroke volume (the shipped constant-C model gives a ratio of 1.00).

**Difficulty:** intermediate

## Session 7: A simple feedback on the resistance

**You will learn:** How the body keeps its mean pressure steady with feedback, and the idea of a control loop.

**You will build:** A controller that adjusts R each beat to hold the mean pressure at a set value.

**Checkpoint (not met by the shipped code):** The mean pressure stays within 2 mmHg of 99 mmHg when the stroke volume varies by plus or minus 20 percent (the shipped model's mean moves by about 20 mmHg).

**Difficulty:** advanced

## Session 8: From a lump to an arterial network

**You will learn:** Pressure waves travel along the arteries and reflect; the pressure changes with the position.

**You will build:** A chain of Windkessel segments or a one-dimensional wave model.

**Checkpoint (not met by the shipped code):** The systolic pressure at a distant point exceeds the systolic pressure near the heart by at least 5 mmHg (the shipped single lump has no position, so the difference is 0).

**Difficulty:** advanced

## The final step

Combine the milestones: an animated circulation with a valve, pressure-dependent arteries and a simple feedback, with a stiffness slider that shows how the pulse pressure changes. If your result looks like the Target animation, open a pull request and tell us how you did it. Remember: it is an educational illustration, not medical advice.
