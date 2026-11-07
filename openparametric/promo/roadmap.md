# Roadmap: the path to the openparametric Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Units that the rules check

**You will learn:** Why a rule that adds millimetres to kilograms is a mistake, and how a quantity can carry its unit through every equation.

**You will build:** Give every input and rule a unit (mass, length, force, stress as powers of kg, m and s) and make the engine refuse an equation whose units do not match.

**Checkpoint (not met by the shipped code):** Adding a length to a mass is refused, the stress rule 6 F L / (b t^2) comes out in MPa when F is in N and the lengths are in mm, and the flange rules pass the check.

**Difficulty:** intermediate

## Session 5: Tables of standard sizes inside the rules

**You will learn:** How real catalogues give pipe sizes, bolt sizes and plate thicknesses as tables, and why a rule must look a value up instead of computing it.

**You will build:** Add a lookup function to the engine for tables such as DN to outside diameter, and an interpolation function for a table of stress against temperature.

**Checkpoint (not met by the shipped code):** DN100 gives 114.3 mm, a value halfway between two table rows is interpolated linearly, and a value outside the table is refused.

**Difficulty:** beginner

## Session 6: Conditional rules and two rings of bolts

**You will learn:** How a rule can apply only above a limit, for example a second ring of bolts when one ring would be too crowded.

**You will build:** Add a conditional form to the engine and a second ring to the flange when the bolts of one ring would be closer than 2.5 M.

**Checkpoint (not met by the shipped code):** Below the limit the flange equals the Session 3 flange, above it the two rings together carry the load and no two holes touch.

**Difficulty:** intermediate

## Session 7: Explaining a result: why is n = 8?

**You will learn:** How an engineer asks which input and which rule made a number come out as it did.

**You will build:** Record which values every rule read and print the chain of rules that led to a chosen value, with their equations.

**Checkpoint (not met by the shipped code):** The explanation of the mass includes n, fod and t and not the hole rule of an unrelated part, and changing an input that is not in the chain does not change the value.

**Difficulty:** intermediate

## Session 8: Searching for the lightest design

**You will learn:** How a program tries many inputs, such as the bolt size and the material, runs the rules for each and keeps the best that meets every requirement.

**You will build:** A search over the bolt size and the bracket material that returns the lightest design that passes all checks.

**Checkpoint (not met by the shipped code):** The answer meets every requirement and no other combination on the grid is both valid and lighter, which a brute-force loop confirms.

**Difficulty:** advanced
