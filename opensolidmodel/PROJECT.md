# Project form (Hello FOSS)

**Project name:** opensolidmodel

**Short description:** Learn how a parametric CAD program works: a recipe of parameters and equations, the stiffness of an outline and a sketch constraint solver, in 3 sessions.

**Full description:** opensolidmodel is a beginner-friendly learning repo about what is inside a parametric CAD program. In three short sessions you go from a part stored as named parameters, equations and a rebuild (with a safe evaluator that never runs arbitrary code), to the area, centroid and second moment of area of any flat outline made of straight edges and round holes, validated against a second independent method, to a sketch constraint solver that finds the corner points from dimensions with Newton's method, counts the degrees of freedom and reports contradictions, ending in the mass and stiffness of an L-shaped shelf bracket. The models are deliberately small (flat outlines, straight lines, one extrusion) so the numbers are illustrative, not a design tool. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment) and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as arcs in the sketch, a feature tree with a revolve and a fillet, and the volume and centre of mass of a solid.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/opensolidmodel
