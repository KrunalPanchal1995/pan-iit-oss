"""Session 1 (Level 1): atoms are conserved, so balancing is bookkeeping.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: atoms are conserved, balancing is bookkeeping
# **A. Real-world problem.** A recipe says 2 slices of bread + 1 slice of cheese make 1
# sandwich. If you only have the right counts, nothing is wasted. A chemical reaction is a
# recipe whose ingredients are atoms: atoms are never created or destroyed, they are only
# regrouped. So the number of atoms of each element must be the same on both sides.
#
# **Plan.** (1) read a formula and count atoms, (2) count atoms on each side of an equation,
# (3) test whether it is balanced, (4) find the coefficients by trying small whole numbers.

# %%
import itertools
import pathlib
import re

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"


# %% [markdown]
# ## Step 1: count the atoms in a formula
# In H2O the small number after a symbol says how many atoms: 2 H and 1 O (no number means 1).
# Brackets multiply what is inside: Ca(OH)2 has 1 Ca, 2 O and 2 H.

# %%
def parse_formula(formula):
    """Return {element: atom count} for a formula such as 'H2O' or 'Ca(OH)2'."""
    tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)", formula)
    if not formula or "".join(tokens) != formula or tokens[0].isdigit():
        raise ValueError(f"cannot read formula {formula!r}")
    stack = [{}]
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "(":
            stack.append({})
        elif t == ")":
            if len(stack) == 1:
                raise ValueError(f"unbalanced bracket in {formula!r}")
            group = stack.pop()
            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 1
            for el, n in group.items():
                stack[-1][el] = stack[-1].get(el, 0) + n * mult
        elif t.isdigit():
            raise ValueError(f"misplaced number in {formula!r}")
        else:
            n = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                n = int(tokens[i + 1])
                i += 1
            stack[-1][t] = stack[-1].get(t, 0) + n
        i += 1
    if len(stack) != 1:
        raise ValueError(f"unbalanced bracket in {formula!r}")
    return stack[0]


# %% [markdown]
# ## Step 2: count atoms on one side
# A side is a list of (coefficient, formula) pairs, for example 2 H2 + O2 is
# [(2, "H2"), (1, "O2")]. The coefficient multiplies every atom of that formula.

# %%
def side_counts(side):
    """Total atoms of each element on one side of an equation."""
    total = {}
    for coef, formula in side:
        for el, n in parse_formula(formula).items():
            total[el] = total.get(el, 0) + coef * n
    return total


def imbalance(reactants, products):
    """{element: atoms on the left minus atoms on the right}; all zeros means balanced."""
    left, right = side_counts(reactants), side_counts(products)
    return {el: left.get(el, 0) - right.get(el, 0) for el in sorted(set(left) | set(right))}


def is_balanced(reactants, products):
    return all(v == 0 for v in imbalance(reactants, products).values())


# %% [markdown]
# ## Step 3: balancing by trying small numbers
# For a small equation we can simply try every set of whole-number coefficients from 1 to a
# limit and keep the one with the smallest total. That is slow for big equations (Session 3
# replaces it with linear algebra) but it shows what balancing means.

# %%
def balance_search(reactant_formulas, product_formulas, max_coef=6):
    """Smallest whole-number coefficients that balance, or None. Returns (reactant coefs, product coefs)."""
    n_r = len(reactant_formulas)
    best = None
    for combo in itertools.product(range(1, max_coef + 1), repeat=n_r + len(product_formulas)):
        if best is not None and sum(combo) >= sum(best):
            continue
        reactants = list(zip(combo[:n_r], reactant_formulas))
        products = list(zip(combo[n_r:], product_formulas))
        if is_balanced(reactants, products):
            best = combo
    if best is None:
        return None
    return best[:n_r], best[n_r:]


def format_equation(reactants, products):
    def one(side):
        return " + ".join((f"{c} " if c != 1 else "") + f for c, f in side)
    return one(reactants) + " -> " + one(products)


def scale(coefs, factor):
    """A recipe made `factor` times over: every coefficient is multiplied."""
    return tuple(c * factor for c in coefs)


# %% [markdown]
# ## Step 4: see it
# Left: atom counts for the unbalanced H2 + O2 -> H2O and for the balanced recipe.
# Right: how the right-hand atom counts change as the coefficient of H2O grows, with the
# left side fixed at 2 H2 + O2.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    cases = [("H2 + O2 -> H2O (not balanced)", [(1, "H2"), (1, "O2")], [(1, "H2O")]),
             ("2 H2 + O2 -> 2 H2O (balanced)", [(2, "H2"), (1, "O2")], [(2, "H2O")])]
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.6), sharey=True)
    for ax, (title, r, p) in zip(axs, cases):
        left, right = side_counts(r), side_counts(p)
        els = ["H", "O"]
        xs = range(len(els))
        ax.bar([x - 0.2 for x in xs], [left[e] for e in els], 0.4, label="left side")
        ax.bar([x + 0.2 for x in xs], [right[e] for e in els], 0.4, label="right side")
        ax.set_xticks(list(xs))
        ax.set_xticklabels(els)
        ax.set_xlabel("element")
        ax.set_title(title, fontsize=9)
        ax.grid(alpha=0.3, axis="y")
        print(title, "-> imbalance", imbalance(r, p))
    axs[0].set_ylabel("number of atoms")
    axs[0].legend()
    fig.tight_layout()
    fig.savefig(OUT / "atom_counts.png", dpi=120)

    c = list(range(0, 7))
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(c, [2 * k for k in c], "o-", label="H atoms on the right (2 per H2O)")
    ax2.plot(c, [k for k in c], "s-", label="O atoms on the right (1 per H2O)")
    ax2.axhline(4, color="C0", ls=":", label="H atoms on the left (2 H2)")
    ax2.axhline(2, color="C1", ls=":", label="O atoms on the left (1 O2)")
    ax2.set_xlabel("coefficient of H2O")
    ax2.set_ylabel("number of atoms")
    ax2.set_title("Balanced only where both pairs of lines meet (at 2)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "atoms_vs_coefficient.png", dpi=120)
    sol = balance_search(["H2", "O2"], ["H2O"])
    print("search:", format_equation(list(zip(sol[0], ["H2", "O2"])), list(zip(sol[1], ["H2O"]))))
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
