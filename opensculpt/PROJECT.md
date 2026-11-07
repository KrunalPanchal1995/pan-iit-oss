# Project form (Hello FOSS)

**Project name:** opensculpt

**Short description:** Learn how CAD parts are built from signed distance functions: union, subtraction, blends, volumes and a parametric mug.

**Full description:** opensculpt is a beginner-friendly learning repo about a different way to do CAD: instead of storing a part as a list of faces, store it as a function that gives, for every point in space, the signed distance to the surface (negative inside). In three short sessions you go from circles and boxes drawn as pictures, to the CAD operations (union as min, intersection as max, subtraction, smooth blends, shells) and a parametric mug cross-section sized for 300 mL, to a 3D mug sampled on a voxel grid, whose volume you measure and validate against exact formulas. You also write a marching-squares contour extractor, use the gradient as a surface normal, render a cut-away by ray marching and study how thin walls and over-large blends fail. Each session has a lesson script, a Colab notebook, a slider app and a checkpoint that prints PASS or FAIL. The repo stops on purpose: a Target animation and a roadmap point to 3D meshes, assemblies and optimisation.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/opensculpt
