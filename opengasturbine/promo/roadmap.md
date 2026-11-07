# Roadmap: the path to the opengasturbine Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Flight speed and ram compression

**You will learn:** How the moving air is slowed in the inlet and is already compressed and heated before the compressor, and why thrust is exit speed minus flight speed.

**You will build:** Add the flight Mach number to the turbojet: total temperature and pressure at the inlet, and thrust per kg of air equal to v_e - v_0.

**Checkpoint (not met by the shipped code):** At Mach 0 the result equals the Session 3 turbojet exactly, and for the same engine the specific thrust falls as the flight speed rises.

**Difficulty:** intermediate

## Session 5: Pressure losses in the inlet, combustor and nozzle

**You will learn:** Why every duct and the flame itself lose a few percent of the total pressure, and how this costs thrust.

**You will build:** Add a total pressure ratio for each of the three parts and carry them through the cycle.

**Checkpoint (not met by the shipped code):** With all pressure ratios set to 1 the Session 3 numbers come back exactly, and with a 5 percent loss in the combustor the specific thrust is lower.

**Difficulty:** intermediate

## Session 6: Variable gas properties

**You will learn:** Why the hot gas behind the combustor has a different cp and gamma from the cold air in front of it.

**You will build:** Use two sets of properties (cold air and hot combustion gas) in the same cycle code.

**Checkpoint (not met by the shipped code):** With the hot-gas values equal to the cold-air values the Session 3 numbers come back, and the energy balance of Session 3 still closes with two different cp values.

**Difficulty:** intermediate

## Session 7: Turbine cooling air

**You will learn:** How blades survive gas hotter than their melting point by bleeding cool compressor air through them, and what that costs in work.

**You will build:** Bleed a fraction of the compressor air past the combustor and mix it back at the turbine.

**Checkpoint (not met by the shipped code):** With no cooling air the earlier results return, and for the same turbine inlet temperature, more cooling air lowers the net work or the thrust.

**Difficulty:** advanced

## Session 8: The turbofan: bypass ratio and propulsive efficiency

**You will learn:** Why moving more air more slowly wastes less kinetic energy, and how propulsive efficiency 2 v_0 / (v_0 + v_e) depends on the exit speed.

**You will build:** Add a bypass duct with its own fan and compute the thrust of the core and of the bypass stream.

**Checkpoint (not met by the shipped code):** With a bypass ratio of 0 the turbojet is recovered, and at a fixed flight speed a higher bypass ratio gives a higher propulsive efficiency.

**Difficulty:** advanced
