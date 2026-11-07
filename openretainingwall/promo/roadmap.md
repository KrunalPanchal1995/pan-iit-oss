# Roadmap: the path to the openretainingwall Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Cantilever wall with a heel slab

**You will learn:** How a thin stem on a wide base slab uses the soil above the heel as extra weight.

**You will build:** A wall made of a stem and a base slab, with the weight of soil on the heel included.

**Checkpoint (not met by the shipped code):** A 4 m wall that passes FS_slide at least 1.5, FS_ot at least 2.0 and the middle-third rule while using at most 3.0 square metres of concrete per metre run (the shipped rectangular wall needs 8.0).

**Difficulty:** intermediate

## Session 5: Passive resistance and a shear key

**You will learn:** Passive earth pressure Kp and why designers use only part of it.

**You will build:** A passive force at the toe and a key under the base added to the sliding check.

**Checkpoint (not met by the shipped code):** A 4 m wall only 1.5 m wide passes all three checks with a stated embedment (the shipped model gives FS_ot of only 1.69 for 1.5 m).

**Difficulty:** intermediate

## Session 6: A drain that saves the wall

**You will learn:** How a drain lowers the water table and how rain and seepage are modelled in practice.

**You will build:** A drainage model that sets the effective water level behind the wall from rain and drain capacity.

**Checkpoint (not met by the shipped code):** The 2 m wide, 4 m high wall passes all three checks in a storm that gives 3 m of water in the undrained backfill (the shipped model gives FS_slide 1.01 and FS_ot 1.41 there).

**Difficulty:** advanced

## Session 7: Bearing capacity of the ground

**You will learn:** Why the pressure under the toe must stay below what the ground can carry.

**You will build:** A check of the toe pressure against an allowable bearing pressure.

**Checkpoint (not met by the shipped code):** A rectangular 4 m wall with toe pressure of at most 150 kPa that also passes the other checks (the shipped 2 m wall has 192 kPa).

**Difficulty:** advanced

## Session 8: Earthquake loading

**You will learn:** A pseudo-static approach to earthquake pressure on walls (Mononobe-Okabe).

**You will build:** A function Kae for a horizontal acceleration coefficient and a check of the wall under it.

**Checkpoint (not met by the shipped code):** Kae equals the Rankine Ka to 1e-9 when the acceleration coefficient is zero, and the 2 m wall is re-checked for a coefficient of 0.15.

**Difficulty:** advanced

## The final step

Combine the milestones: an animated retaining wall with a drain, a cantilever section and a bearing check, whose safety factors you can read as the water rises. If your result looks like the Target animation, open a pull request and tell us how you did it.
