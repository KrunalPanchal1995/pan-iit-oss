# Roadmap: the path to the opendesalination Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Real seawater osmotic pressure

**You will learn:** Why concentrated salt water pushes less than the ideal van 't Hoff law says (the osmotic coefficient), and how real seawater differs from pure NaCl.

**You will build:** An osmotic pressure function with an osmotic coefficient fitted to published seawater data, used in place of the ideal law in Sessions 1 to 3.

**Checkpoint (not met by the shipped code):** The least work at 50 percent recovery for 35 g/L seawater at 25 degrees C lies between 1.00 and 1.10 kWh/m3 (the shipped ideal law gives 1.143).

**Difficulty:** intermediate

## Session 5: Pressure drop and a two-stage vessel train

**You will learn:** Water flowing along a spiral-wound element loses pressure to friction, and a second stage can treat the first stage's brine.

**You will build:** A pressure drop along the vessel inside `simulate_module`, and a two-stage train whose second stage has a booster pump.

**Checkpoint (not met by the shipped code):** With a 200 kPa drop along the vessel at 6750 kPa, the recovery falls below the shipped 0.453; with a second stage the train reaches at least 50 percent recovery below 6900 kPa.

**Difficulty:** intermediate

## Session 6: Concentration polarisation from mass transfer

**You will learn:** Why salt piles up at the membrane wall, the film model CP = exp(Jw / k), and how the cross-flow velocity sets k.

**You will build:** A local CP computed at every step of the march from the flux and a mass-transfer coefficient.

**Checkpoint (not met by the shipped code):** CP is larger at the inlet (high flux) than at the outlet, and the recovery at 6000 kPa lies between the shipped CP = 1.0 and CP = 1.2 results.

**Difficulty:** intermediate

## Session 7: Second pass and boron

**You will learn:** Seawater holds about 5 mg/L of boron, which passes RO membranes much more easily than salt, and how raising the pH helps.

**You will build:** A boron balance through the first pass and a partial second pass on the permeate, with a pH-dependent boron rejection.

**Checkpoint (not met by the shipped code):** The blended drinking water has less than 1 mg/L of boron and less than 300 mg/L of salt, with the extra energy of the second pass reported in kWh/m3.

**Difficulty:** advanced

## Session 8: The whole plant and the cost of water

**You will learn:** Intake pumping, pretreatment, post-treatment and the electricity price turn kWh/m3 into rupees per m3.

**You will build:** A plant model that adds every block to the energy ladder and computes the energy cost per m3 and the electrical power of a 100 MLD plant.

**Checkpoint (not met by the shipped code):** The whole-plant specific energy lies between 3 and 4 kWh/m3 and the ladder still starts at the Session 4 least work.

**Difficulty:** advanced

## The final step

Combine the milestones: real seawater properties, a two-stage train with pressure drop and mass-transfer polarisation, a second pass for boron and the whole-plant blocks, drawn as one energy ladder. If your result lands in the 3 to 4 kWh/m3 band with every bar explained, open a pull request and tell us how you did it.
