"""Session 2 (Level 2): energy from nutrients, resting energy, and a daily balance equation.

General education only. Not medical or dietary advice. The people are made up. The formulas
are population estimates; a real person can differ a lot.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: energy from nutrients and the balance equation
# **A. Real-world problem.** A food label lists grams of protein, carbohydrate and fat, and
# also a number of kilocalories. Do they agree? And how many kilocalories does a person need
# per day? This session builds the equations: label energy from grams, a resting-energy
# estimate (Mifflin-St Jeor), activity multipliers, and a daily balance as a difference
# equation. (General education only, not medical or dietary advice.)

# %%
import pathlib

import numpy as np

# where figures are saved (works as a script and in Jupyter/Colab)
OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

KCAL_PER_G = {"protein": 4.0, "carbohydrate": 4.0, "fat": 9.0}   # Atwater general factors
KCAL_PER_KG = 7700.0                                              # rough rule, see Step 4


# %% [markdown]
# ## Step 1: energy from grams
# energy (kcal) = 4 x protein (g) + 4 x carbohydrate (g) + 9 x fat (g).
# Printed labels use more detailed factors and rounding, so a small mismatch is normal.

# %%
def label_kcal(protein_g, carb_g, fat_g):
    """Energy computed from grams (kcal)."""
    return (KCAL_PER_G["protein"] * protein_g + KCAL_PER_G["carbohydrate"] * carb_g
            + KCAL_PER_G["fat"] * fat_g)


def label_check(printed_kcal, protein_g, carb_g, fat_g):
    """Returns (computed kcal, printed - computed, difference as a percentage of printed)."""
    calc = label_kcal(protein_g, carb_g, fat_g)
    diff = printed_kcal - calc
    return calc, diff, 100.0 * diff / printed_kcal


# %% [markdown]
# ## Step 2: resting energy (Mifflin-St Jeor) and activity multipliers
# BMR (basal metabolic rate) is the energy the body uses at complete rest. The Mifflin-St Jeor
# equation is a *population estimate* fitted to many people. For one person the true value can
# be quite different, so treat the result as a starting guess, never a measurement.
#
#     BMR = 10 m + 6.25 h - 5 a + s      (kcal/day)
#     m = mass in kg, h = height in cm, a = age in years, s = +5 (male) or -161 (female)
#
# Total daily energy use (TDEE) is BMR times an activity factor (PAL). These factors are common
# textbook values, rounded.

# %%
PAL = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}


def mifflin(sex, mass_kg, height_cm, age_years):
    if sex not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")
    s = 5.0 if sex == "male" else -161.0
    return 10.0 * mass_kg + 6.25 * height_cm - 5.0 * age_years + s


def tdee(bmr, pal):
    return bmr * pal


# %% [markdown]
# ## Step 3: the balance as a difference equation
# Let M[n] be body mass on day n (kg), I the energy eaten per day and E the energy used per day
# (both kcal/day). A rough short-term rule says about 7700 kcal of surplus adds about 1 kg:
#
#     M[n+1] = M[n] + (I - E) / 7700
#
# Here E is held constant. Step 4 and Session 3 show why that is only a short-term approximation.

# %%
def mass_series(m0, intake, expenditure, days):
    """Mass (kg) on days 0..days with constant intake and expenditure (kcal/day)."""
    m = np.empty(days + 1)
    m[0] = m0
    for n in range(days):
        m[n + 1] = m[n] + (intake - expenditure) / KCAL_PER_KG
    return m


def mass_change_rule(intake, expenditure, days):
    """Closed form of the same rule: (I - E) * days / 7700 (kg)."""
    return (intake - expenditure) * days / KCAL_PER_KG


# %% [markdown]
# ## Step 4: limits (important)
# The body adapts: when mass changes, expenditure changes, hormones and activity change too.
# So 7700 kcal per kg is only a rough short-term approximation, and it gets worse the longer
# you extend it. Session 3 shows this with a dynamic model.

# %% [markdown]
# ## Step 5: a design problem for a made-up person
# Ravi (made up): male, 19 years, 175 cm, 70 kg, moderate activity. Choose servings from a menu
# so that his day's food energy matches his estimated energy use within 50 kcal.

# %%
# (protein g, carbohydrate g, fat g) per serving, rounded and approximate
MENU = {
    "rice (1 cup)": (4, 45, 1),
    "dal (1 bowl)": (12, 30, 4),
    "chapati (1)": (3, 18, 3),
    "paneer (50 g)": (9, 2, 10),
    "milk (1 glass)": (8, 12, 8),
    "banana (1)": (1, 27, 0),
    "peanuts (30 g)": (8, 5, 14),
    "egg (1)": (6, 1, 5),
}
RAVI = dict(sex="male", mass_kg=70.0, height_cm=175.0, age=19, pal="moderate")


def menu_kcal(servings):
    """servings: dict name -> number of servings. Returns total kcal."""
    return float(sum(label_kcal(*MENU[k]) * n for k, n in servings.items()))


def plan_ok(servings, target_kcal, tol=50.0, max_per_item=4):
    """A plan is OK if the total is within tol of the target, uses at least 5 items, max 4 servings each."""
    used = [k for k, n in servings.items() if n > 0]
    return (abs(menu_kcal(servings) - target_kcal) <= tol and len(used) >= 5
            and all(0 <= n <= max_per_item for n in servings.values()))


RAVI_PLAN = {"rice (1 cup)": 2, "dal (1 bowl)": 3, "chapati (1)": 4, "paneer (50 g)": 2,
             "milk (1 glass)": 2, "banana (1)": 2, "peanuts (30 g)": 2, "egg (1)": 0}


# %% [markdown]
# ## Step 6: see it
# Left: mass over 30 days for three intakes with the constant-E rule (straight lines). Right:
# label energy from grams against the printed value for the granola bar example.

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    bmr = mifflin(RAVI["sex"], RAVI["mass_kg"], RAVI["height_cm"], RAVI["age"])
    E = tdee(bmr, PAL[RAVI["pal"]])
    print(f"Ravi: BMR {bmr:.2f} kcal/day, TDEE {E:.1f} kcal/day")
    print(f"Ravi's plan: {menu_kcal(RAVI_PLAN):.0f} kcal, ok = {plan_ok(RAVI_PLAN, E)}")
    print("granola bar:", [round(v, 2) for v in label_check(450, 5, 60, 20)])
    print(f"worked example: +259 kcal/day for 30 days -> {mass_change_rule(2900, E, 30):.2f} kg")

    days = 30
    fig, ax = plt.subplots(figsize=(6, 4))
    for intake in (E - 500, E, E + 500):
        ax.plot(np.arange(days + 1), mass_series(70.0, intake, E, days), label=f"intake {intake:.0f} kcal/day")
    ax.set_xlabel("day")
    ax.set_ylabel("body mass (kg)")
    ax.set_title("Constant-E rule: straight lines (short-term only)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "mass_rule.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(5, 4))
    parts = [4 * 5, 4 * 60, 9 * 20]
    ax2.bar(["protein", "carbohydrate", "fat"], parts, color=["#457b9d", "#e9c46a", "#e76f51"])
    ax2.set_ylabel("energy from this part (kcal)")
    ax2.set_title("Granola bar: 20 + 240 + 180 = 440 kcal (printed 450)")
    ax2.grid(alpha=0.3, axis="y")
    fig2.tight_layout()
    fig2.savefig(OUT / "label_parts.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
