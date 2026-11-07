"""Session 3 (Level 3): a rule engine: rules stored as text, put in the right order, checked for loops, and used to generate a bolted flange.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: rules as data: sorting them, checking them and drawing the part they make
# **A. Real-world problem.** A pipe flange joins two pipes with a ring of bolts. How many bolts it needs depends on the load and the bolt size, the
# size of the bolt circle depends on the number of bolts and on the pipe, the outside diameter depends on the bolt circle, and so on. A designer
# keeps all this in a list of rules. If the load doubles, the whole flange should be regenerated. Which rule has to be evaluated first, how do we notice a
# rule that depends on itself, and how do we know that the drawing agrees with the numbers?
#
# Educational model: a flat circular flange with a bore, one ring of equal bolts and rules of thumb for the geometry. Not a flange standard: do not use it for real pipework.

# %%
import ast
import math
import pathlib
import re

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
PITCH = {8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0, 18: 2.5, 20: 2.5, 22: 2.5, 24: 3.0}   # coarse thread pitch of metric bolts (mm)


# %% [markdown]
# ## Step 1: a rule is a name and an equation in text
# A rule is a pair ('n', 'max(4, 2 * ceil(n_min / 2))'): the value of n is computed from other names, which are either inputs
# (load, bolt size, pipe diameter) or other rules. The evaluator accepts only numbers, names, + - * / **, brackets and a short list of functions, so rules can come from any file
# without running arbitrary code. The names a rule uses are its **dependencies**.

# %%
def _functions():
    return {"sqrt": math.sqrt, "ceil": math.ceil, "max": max, "min": min, "pitch": lambda m: PITCH[int(m)]}


CONSTANTS = {"pi": math.pi}
_BIN = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b, ast.Pow: lambda a, b: a ** b}


def evaluate(expr, scope):
    """Evaluate the text of a rule with the values in scope (a dictionary of names)."""
    funcs = _functions()

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in scope:
                return scope[node.id]
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise ValueError(f"unknown name '{node.id}'")
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            a, b = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(b) > 100:
                raise ValueError("an exponent above 100 is not allowed")
            return _BIN[type(node.op)](a, b)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in funcs and not node.keywords:
            return funcs[node.func.id](*[walk(a) for a in node.args])
        raise ValueError("this expression is not allowed")
    try:
        return walk(ast.parse(str(expr), mode="eval"))
    except (SyntaxError, ZeroDivisionError, OverflowError, KeyError) as err:
        raise ValueError(f"cannot evaluate '{expr}': {err!r}") from None


def dependencies(expr):
    """The set of names a rule uses (not counting functions and constants)."""
    try:
        tree = ast.parse(str(expr), mode="eval")
    except SyntaxError as err:
        raise ValueError(f"cannot read '{expr}': {err}") from None
    called = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id not in called and n.id not in CONSTANTS}


# %% [markdown]
# ## Step 2: finding the order, and catching loops
# The rules may be written in any order. A rule can be evaluated only after all the rules it depends on. This is a **topological sort**: repeat
# 'take the first rule whose dependencies are all available' until none is left. If rules are left but none can be taken, they depend on each other in a circle, and no order exists:
# the engine must say so and show the circle, instead of looping for ever. It must also reject names that nobody defines and two rules with the same name.

# %%
def order(rules, inputs):
    """Return the names of the rules in an order in which they can be evaluated. Raises ValueError for loops, unknown or repeated names."""
    names = [n for n, _ in rules]
    if len(set(names)) != len(names):
        raise ValueError("two rules have the same name")
    if set(names) & set(inputs):
        raise ValueError("a rule has the name of an input: " + ", ".join(sorted(set(names) & set(inputs))))
    deps = {n: dependencies(e) for n, e in rules}
    for n, d in deps.items():
        unknown = d - set(inputs) - set(names)
        if unknown:
            raise ValueError(f"rule '{n}' uses unknown name(s): {', '.join(sorted(unknown))}")
    done, out = set(inputs), []
    left = list(names)
    while left:
        ready = next((n for n in left if all(d in done for d in deps[n])), None)
        if ready is None:
            raise ValueError("circular rules: " + _find_cycle(left, deps))
        out.append(ready)
        done.add(ready)
        left.remove(ready)
    return out


def _find_cycle(left, deps):
    """Follow dependencies among the rules that could not be placed until a name repeats."""
    node, seen = left[0], []
    while node not in seen:
        seen.append(node)
        node = next(d for d in sorted(deps[node]) if d in left)
    return " -> ".join(seen[seen.index(node):] + [node])


def run_rules(rules, inputs):
    """Evaluate all rules in a valid order. Returns (values, order): values holds the inputs and every rule."""
    seq = order(rules, inputs)
    expr = dict(rules)
    values = dict(inputs)
    for n in seq:
        values[n] = evaluate(expr[n], values)
    return values, seq


# %% [markdown]
# ## Step 3: the flange rules
# The rules below are written in the order a person thinks of them, not in the order they must be evaluated. The engine sorts them. In words:
# the hole is 2 mm wider than the bolt; the thread's tensile stress area is pi / 4 (M - 0.9382 pitch)^2; one bolt carries area x allowable stress;
# the number of bolts is the load divided by that, rounded up to an even number and at least 4; the bolt circle diameter is the larger of 'pipe + 4 M' (room for the pipe and the nut)
# and the value that keeps the bolts 2.5 M apart (wrench room); the flange is 3 M wider than the bolt circle; the thickness is a rule of thumb that grows with the bolt size, the pipe and the load; the mass is density x area x thickness.

# %%
FLANGE_RULES = [
    ("mass", "rho * (pi / 4 * (fod ** 2 - od ** 2) - n * pi / 4 * hole ** 2) * t * 1e-9"),
    ("fod", "pcd + 3 * M"),
    ("t", "ceil(0.8 * M + 0.02 * od + 0.04 * load)"),
    ("pcd", "max(od + 4 * M, n * 2.5 * M / pi)"),
    ("n", "max(4, 2 * ceil(n_min / 2))"),
    ("n_min", "ceil(load / f_bolt)"),
    ("f_bolt", "area_b * sigma_b / 1000"),
    ("area_b", "pi / 4 * (M - 0.9382 * pitch(M)) ** 2"),
    ("hole", "M + 2"),
]
FLANGE_INPUTS = {"load": 60.0, "M": 12, "od": 114.3, "sigma_b": 320.0, "rho": 7850.0}      # kN, mm, mm, MPa, kg/m^3


def flange(**change):
    """Generate a flange: apply the rules to the inputs (changed as given). Returns the dictionary of all values."""
    unknown = set(change) - set(FLANGE_INPUTS)
    if unknown:
        raise ValueError(f"unknown input(s): {', '.join(sorted(unknown))}")
    inputs = {**FLANGE_INPUTS, **change}
    if inputs["load"] <= 0 or inputs["od"] <= 0 or inputs["sigma_b"] <= 0 or inputs["rho"] <= 0:
        raise ValueError("load, pipe diameter, bolt stress and density must be positive")
    if int(inputs["M"]) != inputs["M"] or int(inputs["M"]) not in PITCH:
        raise ValueError("the bolt size must be one of M" + ", M".join(str(m) for m in sorted(PITCH)))
    values, seq = run_rules(FLANGE_RULES, inputs)
    values["order"] = seq
    return values


def check_flange(v):
    """Return a list of geometric problems (empty when the flange is sound): holes outside the ring, holes touching, bolts too close."""
    problems = []
    r_in, r_out, rp, rh = v["od"] / 2, v["fod"] / 2, v["pcd"] / 2, v["hole"] / 2
    if rp - rh < r_in or rp + rh > r_out:
        problems.append("a bolt hole reaches the bore or the rim")
    chord = 2 * rp * math.sin(math.pi / v["n"])
    if chord < v["hole"]:
        problems.append("neighbouring bolt holes touch")
    if math.pi * v["pcd"] / v["n"] < 2.5 * v["M"] - 1e-9:                       # the spacing along the bolt circle
        problems.append("the bolts are closer than 2.5 M: no room for a wrench")
    return problems


# %% [markdown]
# ## Step 4: draw it, and check the drawing against the numbers
# The part is drawn as an SVG picture: the outer circle, the bore, and n bolt circles on the bolt circle. The mass rule uses a formula for the area. To check that the
# drawing and the formula describe the same part, we **measure the area from the drawing**: lay a fine grid over the picture and count the grid points that are
# inside the flange ring and outside every bolt hole. The count times the area of a cell must agree with the formula.

# %%
def flange_svg(v, size=400):
    sc = (size - 20) / v["fod"]
    c = size / 2
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" data-px-per-mm="{sc:.8f}">',
             f'<circle class="flange" cx="{c}" cy="{c}" r="{v["fod"] / 2 * sc:.4f}" fill="#9db4d8" stroke="#1f3a68"/>',
             f'<circle class="bore" cx="{c}" cy="{c}" r="{v["od"] / 2 * sc:.4f}" fill="#ffffff" stroke="#1f3a68"/>']
    for k in range(int(v["n"])):
        a = 2 * math.pi * k / v["n"]
        parts.append(f'<circle class="hole" cx="{c + v["pcd"] / 2 * sc * math.cos(a):.4f}" cy="{c + v["pcd"] / 2 * sc * math.sin(a):.4f}" r="{v["hole"] / 2 * sc:.4f}" fill="#ffffff" stroke="#1f3a68"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def circles_from_svg(svg):
    """Read back (class, cx, cy, r) of every circle and the pixels per millimetre from the SVG text."""
    sc = float(re.search(r'data-px-per-mm="([0-9.eE+-]+)"', svg).group(1))
    cs = [(m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)))
          for m in re.finditer(r'<circle class="(\w+)" cx="([0-9.eE+-]+)" cy="([0-9.eE+-]+)" r="([0-9.eE+-]+)"', svg)]
    return cs, sc


def area_from_drawing(svg, cells=700):
    """Area (mm^2) of the material, measured by counting grid points in the picture."""
    cs, sc = circles_from_svg(svg)
    outer = next(c for c in cs if c[0] == "flange")
    r = outer[3]
    xs = outer[1] + (np.arange(cells) + 0.5) / cells * 2 * r - r
    ys = outer[2] + (np.arange(cells) + 0.5) / cells * 2 * r - r
    gx, gy = np.meshgrid(xs, ys)
    inside = np.zeros(gx.shape, dtype=bool)
    for cls, cx, cy, rr in cs:
        d2 = (gx - cx) ** 2 + (gy - cy) ** 2 <= rr ** 2
        inside = d2 if cls == "flange" else inside & ~d2          # the ring first, then remove the bore and the holes
    return float(inside.sum() * (2 * r / cells) ** 2 / sc ** 2)


def area_formula(v):
    return math.pi / 4 * (v["fod"] ** 2 - v["od"] ** 2) - v["n"] * math.pi / 4 * v["hole"] ** 2


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    OUT.mkdir(exist_ok=True)
    v = flange()
    print("order of evaluation:", " -> ".join(v["order"]))
    print(f"load 60 kN, M12, pipe 114.3 mm: n = {v['n']}, pcd = {v['pcd']:.1f} mm, outside diameter {v['fod']:.1f} mm, t = {v['t']} mm, mass {v['mass']:.3f} kg")
    print("problems:", check_flange(v) or "none")
    print(f"area from the drawing {area_from_drawing(flange_svg(v)):.0f} mm2, from the formula {area_formula(v):.0f} mm2")
    try:
        run_rules([("a", "b + 1"), ("b", "c * 2"), ("c", "a - 3")], {})
    except ValueError as e:
        print("loop:", e)
    for load in (30, 90, 180, 300):
        w = flange(load=load)
        print(f"load {load:3d} kN: n = {w['n']:2d}, pcd {w['pcd']:.0f}, mass {w['mass']:.2f} kg")

    fig, axs = plt.subplots(1, 4, figsize=(9, 2.6))
    for ax, load in zip(axs, (30, 90, 180, 300)):
        w = flange(load=load)
        ax.add_patch(Circle((0, 0), w["fod"] / 2, fc="#9db4d8", ec="#1f3a68"))
        ax.add_patch(Circle((0, 0), w["od"] / 2, fc="white", ec="#1f3a68"))
        for k in range(w["n"]):
            a = 2 * math.pi * k / w["n"]
            ax.add_patch(Circle((w["pcd"] / 2 * math.cos(a), w["pcd"] / 2 * math.sin(a)), w["hole"] / 2, fc="white", ec="#1f3a68"))
        ax.set_xlim(-170, 170)
        ax.set_ylim(-170, 170)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{load} kN: {w['n']} bolts", fontsize=9)
    fig.suptitle("One set of rules, four loads (M12 bolts, 114.3 mm pipe)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "flange_family.png", dpi=120)

    loads = np.arange(10, 301, 5)
    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    ax3 = ax2.twinx()
    for M, col in ((10, "tab:green"), (12, "tab:blue"), (16, "tab:red")):
        ax2.step(loads, [flange(load=float(x), M=M)["n"] for x in loads], where="post", color=col, label=f"bolts, M{M}")
        ax3.plot(loads, [flange(load=float(x), M=M)["mass"] for x in loads], "--", color=col, lw=1)
    ax2.set_xlabel("load (kN)")
    ax2.set_ylabel("number of bolts (solid)")
    ax3.set_ylabel("mass of the flange (kg, dashed)")
    ax2.set_title("The flange regenerates as the load grows")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8, loc="upper left")
    fig2.tight_layout()
    fig2.savefig(OUT / "bolts_vs_load.png", dpi=120)

# %% [markdown]
# ## Where this stops
# The rules are rules of thumb, the flange is one flat ring, and the engine has no units, no tables of standard sizes and no way to say 'this rule applies only above 100 kN'.
# Real systems add all of these, and also keep a record of which rule produced which number so that a change can be explained. The roadmap lists them.
