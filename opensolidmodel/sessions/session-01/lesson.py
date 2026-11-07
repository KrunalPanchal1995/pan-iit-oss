"""Session 1 (Level 2): a part is a recipe: named parameters, equations and a rebuild.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: a part is a recipe, not a shape
# **A. Real-world problem.** A customer asks for the same mounting plate with 6 holes instead of 4,
# 20 mm wider. In a drawing you would redraw it. A CAD program stores a *recipe* instead: a few named
# numbers (parameters), a list of features that use them, and equations that link them. Change one
# number and the whole part is rebuilt. How is such a recipe stored, and how do we get the volume and the
# mass of the rebuilt part?
#
# Educational model: a rectangular plate with a row of round through-holes. Not a CAD program, and the
# mass is not a design value.

# %%
import ast
import math
import operator
import pathlib

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
RHO = 7850.0   # density of steel (kg/m^3)


# %% [markdown]
# ## Step 1: equations between parameters
# Some dimensions should follow others: the hole spacing is "width / (number of holes + 1)", the
# hole diameter is "40 percent of the spacing". We store such a dimension as text and evaluate it with the
# current parameter values. The evaluator below accepts only numbers, names, + - * / **, brackets and a few
# functions; it never runs arbitrary code.

# %%
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow}
_FUNCS = {"sqrt": math.sqrt, "min": min, "max": max}


def evaluate(expr, params):
    """Evaluate an equation such as 'w / (n + 1)' with the values in the dictionary params."""
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in params:
                raise ValueError(f"unknown parameter '{node.id}'")
            return params[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("an exponent above 100 is not allowed")        # 9 ** 9 ** 9 would hang the program
            return _BIN[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS and not node.keywords:
            return _FUNCS[node.func.id](*[walk(a) for a in node.args])
        raise ValueError("this expression is not allowed")
    try:
        return walk(ast.parse(str(expr), mode="eval"))
    except (SyntaxError, ZeroDivisionError, OverflowError) as err:
        raise ValueError(f"cannot evaluate '{expr}': {err}") from None


def resolve(params, equations):
    """Return a copy of params with every equation evaluated (equations may use earlier ones, in order)."""
    out = dict(params)
    for name, expr in equations:
        out[name] = evaluate(expr, out)
    return out


# %% [markdown]
# ## Step 2: the feature list and the rebuild
# The recipe is a list of features applied in order: first a block w x d x h, then n round through-holes
# of diameter `dia` in a row along the width, spaced `s = w / (n + 1)` apart. The rebuild checks that the
# recipe still makes sense (the holes must not touch each other or the edges) and then returns the
# volume, the mass and the bounding box.
#
#     V = w d h - n (pi / 4) dia^2 h        mass = rho V

# %%
PLATE = {"params": {"w": 120.0, "d": 40.0, "h": 8.0, "n": 4, "ratio": 0.4},
         "equations": [("s", "w / (n + 1)"), ("dia", "ratio * s")]}


def rebuild(part, **change):
    """Rebuild a part after changing some parameters. Lengths are in mm. Returns a dictionary."""
    unknown = set(change) - set(part["params"])
    if unknown:
        raise ValueError(f"unknown parameter(s): {', '.join(sorted(unknown))}")
    p = resolve({**part["params"], **change}, part["equations"])
    w, d, h, n, dia, s = p["w"], p["d"], p["h"], p["n"], p["dia"], p["s"]
    if min(w, d, h) <= 0 or n < 0 or int(n) != n:
        raise ValueError("w, d and h must be positive and n must be a whole number of at least 0")
    if n > 0 and not 0 < dia < min(s, d):
        raise ValueError("the holes must have a positive diameter smaller than their spacing and than the depth")
    v_block = w * d * h
    v_holes = n * math.pi / 4 * dia ** 2 * h
    volume = v_block - v_holes
    return {"params": p, "v_block": v_block, "v_holes": v_holes, "volume": volume,
            "mass": RHO * volume * 1e-9, "bbox": (w, d, h), "faces": 6 + int(n)}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    r = rebuild(PLATE)
    print(f"plate: s = {r['params']['s']:.1f} mm, dia = {r['params']['dia']:.1f} mm, volume = {r['volume'] / 1000:.2f} cm3, mass = {r['mass']:.3f} kg, faces = {r['faces']}")
    r6 = rebuild(PLATE, n=6, w=140.0)
    print(f"customer change n = 6, w = 140: s = {r6['params']['s']:.1f} mm, dia = {r6['params']['dia']:.1f} mm, mass = {r6['mass']:.3f} kg")

    ns = list(range(0, 13))
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for ratio, col in ((0.25, "tab:green"), (0.4, "tab:blue"), (0.6, "tab:red")):
        ax.plot(ns, [rebuild(PLATE, n=k, ratio=ratio)["mass"] for k in ns], "o-", color=col, label=f"hole diameter = {ratio} x spacing")
    ax.set_xlabel("number of holes n")
    ax.set_ylabel("mass of the plate (kg)")
    ax.set_title("Mass of a 120 x 40 x 8 mm steel plate against the number of holes")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "mass_vs_holes.png", dpi=120)

    ws = [60 + 10 * i for i in range(0, 15)]
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax2.plot(ws, [rebuild(PLATE, w=x)["volume"] / 1000 for x in ws], "o-", color="tab:blue", label="plate with holes (dia follows the width)")
    ax2.plot(ws, [rebuild(PLATE, w=x)["v_block"] / 1000 for x in ws], "--", color="tab:gray", label="solid block")
    ax2.set_xlabel("plate width w (mm)")
    ax2.set_ylabel("volume (cm^3)")
    ax2.set_title("Change one parameter and the whole recipe rebuilds")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "volume_vs_width.png", dpi=120)

# %% [markdown]
# ## Where this stops
# A real CAD kernel stores the actual surfaces and edges (a boundary representation) and can combine
# any shapes. Session 2 moves from a block to any flat outline and finds its area, centre and stiffness.
