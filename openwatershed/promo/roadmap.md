# Roadmap: the path to the openwatershed Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Design storms from a rainfall curve

**You will learn:** How an intensity-duration curve becomes a storm hyetograph (alternating blocks).

**You will build:** A function that builds a design storm of a chosen duration from an intensity curve and feeds it to the unit hydrograph.

**Checkpoint (not met by the shipped code):** The blocks add up to the curve's depth for the whole duration within 0.1 percent, and the resulting peak is compared with the rational estimate (target: within 15 percent).

**Difficulty:** intermediate

## Session 5: A smoother unit hydrograph

**You will learn:** Gamma (Nash cascade) unit hydrographs and why the triangle is only an approximation.

**You will build:** A second UH function with the same volume and a smooth rising limb.

**Checkpoint (not met by the shipped code):** Volume of exactly 1 mm over the catchment and a peak within 15 percent of the triangular UH peak (1.72 m3/s for the Session 3 catchment, Tc = 2 h).

**Difficulty:** intermediate

## Session 6: Ponds with sloping banks and a spillway

**You will learn:** Stage-storage tables and a weir spillway for storms bigger than the design storm.

**You will build:** A level-pool router with a sloping-bank pond, an orifice and an overflow weir.

**Checkpoint (not met by the shipped code):** The peak outflow stays at or below the pre-development peak for the design storm, and a storm 30 percent larger passes over the spillway without the stage exceeding the embankment height.

**Difficulty:** advanced

## Session 7: Two sub-catchments joined by a river

**You will learn:** Splitting a catchment into parts with different land use and combining them downstream.

**You will build:** A model that computes two sub-catchment hydrographs, routes one through Muskingum and adds them.

**Checkpoint (not met by the shipped code):** Total water equals the sum of the sub-catchment volumes within 0.1 percent, and the combined peak differs from the lumped model by a stated amount that you explain.

**Difficulty:** advanced

## Session 8: Calibrate against an observed flood

**You will learn:** Fitting CN and Tc to a measured hydrograph and judging the fit.

**You will build:** A least-squares fit of CN and Tc to a synthetic observed hydrograph with added noise.

**Checkpoint (not met by the shipped code):** The fit recovers the true CN and Tc within 3 percent from data with 5 percent noise, and reports the error.

**Difficulty:** advanced

## The final step

Combine the milestones: a storm built from a rainfall curve, a smooth unit hydrograph, two sub-catchments, a routed river and a pond with a spillway, calibrated against an observed flood. If your result looks like the Target animation, open a pull request and tell us how you did it.
