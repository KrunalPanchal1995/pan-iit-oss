"""Session 1 (Level 1): pull a bar and draw its stress-strain curve.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: pulling a bar
# **A. Real-world problem.** A lift cable, a bicycle spoke and a rubber band all get pulled.
# Some spring back when you let go, some stay stretched. How do engineers describe this with
# two numbers that do not depend on the size of the part?
#
# **Plan.** (1) stress = force / area, (2) strain = extension / original length, (3) draw the
# curve of stress against strain for a simple metal bar, (4) mark the elastic and plastic parts.
#
# *This is a simplified teaching model with an illustrative material. It is not a design tool.*

# %%
import pathlib

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

# Illustrative soft metal (round numbers, NOT data for a real alloy)
E_TOY = 70000.0    # stiffness (Young's modulus), MPa  (1 MPa = 1 N/mm^2)
SY_TOY = 200.0     # yield stress, MPa: where permanent stretching starts
H_TOY = 7000.0     # slope of the curve after yield, MPa
L0 = 500.0         # original bar length, mm


# %% [markdown]
# ## Step 1: stress and strain
# * **Stress** = force / cross-section area. With force in kN and area in mm^2,
#   stress (MPa) = force_kN * 1000 / area_mm2, because 1 N/mm^2 = 1 MPa.
# * **Strain** = extension / original length. It has no unit (0.01 means 1 percent).
#
# Why two numbers? A thick bar and a thin bar of the same metal need very different forces, but
# they break at the same *stress*. Stress and strain remove the size of the sample.

# %%
def area_circle(d_mm):
    """Cross-section area of a round bar (mm^2)."""
    return np.pi * d_mm ** 2 / 4.0


def stress_mpa(force_kn, area_mm2):
    """Stress = F / A, in MPa."""
    return force_kn * 1000.0 / area_mm2


def strain(extension_mm, length_mm=L0):
    """Strain = dL / L0, no unit."""
    return extension_mm / length_mm


# %% [markdown]
# ## Step 2: the curve of the toy metal
# Up to the yield stress the bar is **elastic**: strain = stress / E and everything springs back.
# Past it the bar is **plastic**: it keeps stretching more easily (the slope drops to H) and part
# of the stretch stays when you let go.

# %%
def strain_from_stress(s, e=E_TOY, sy=SY_TOY, h=H_TOY):
    """Strain the bar reaches under stress s (MPa) held on the loading path."""
    s = np.asarray(s, dtype=float)
    return np.where(s <= sy, s / e, sy / e + (s - sy) / h)


def stress_from_strain(eps, e=E_TOY, sy=SY_TOY, h=H_TOY):
    eps = np.asarray(eps, dtype=float)
    ey = sy / e
    return np.where(eps <= ey, e * eps, sy + h * (eps - ey))


def region(s, sy=SY_TOY):
    return "elastic" if s <= sy else "plastic"


def permanent_set(s, e=E_TOY, sy=SY_TOY, h=H_TOY):
    """Strain left after unloading from stress s: total strain minus the elastic part s/E."""
    return float(strain_from_stress(s, e, sy, h) - s / e)


# %% [markdown]
# ## Step 3: pull the bar
# A round bar, diameter 10 mm, length 500 mm. We apply 15 kN, then 20 kN.

# %%
def pull(force_kn, d_mm=10.0):
    a = area_circle(d_mm)
    s = stress_mpa(force_kn, a)
    eps = float(strain_from_stress(s))
    return {"area": a, "stress": s, "strain": eps, "extension": eps * L0,
            "region": region(s), "set": permanent_set(s)}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    for f in (15.0, 20.0):
        r = pull(f)
        print(f"{f:4.1f} kN on d=10 mm: area {r['area']:.2f} mm^2, stress {r['stress']:.1f} MPa, "
              f"strain {r['strain']:.5f}, extension {r['extension']:.2f} mm, {r['region']}, "
              f"permanent set {r['set']:.5f} ({r['set'] * L0:.2f} mm)")

    eps = np.linspace(0.0, 0.04, 401)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.plot(eps * 100, stress_from_strain(eps), color="C0", lw=2)
    ey = SY_TOY / E_TOY
    ax.axvspan(0, ey * 100, color="C2", alpha=0.2, label="elastic: springs back")
    ax.axvspan(ey * 100, 4.0, color="C3", alpha=0.1, label="plastic: stays stretched")
    for f, c in ((15.0, "C2"), (20.0, "C3")):
        r = pull(f)
        ax.plot(r["strain"] * 100, r["stress"], "o", color=c)
        ax.annotate(f"{f:.0f} kN", (r["strain"] * 100, r["stress"]), textcoords="offset points", xytext=(8, -12))
    ax.set_xlabel("strain (percent)")
    ax.set_ylabel("stress (MPa)")
    ax.set_title("Stress-strain curve of an illustrative soft metal")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "stress_strain_toy.png", dpi=120)

    fig2, ax2 = plt.subplots(figsize=(6.4, 4.2))
    forces = np.linspace(0, 20, 81)
    for d in (8.0, 10.0, 14.0):
        s = stress_mpa(forces, area_circle(d))
        ax2.plot(forces, s, label=f"d = {d:.0f} mm")
    ax2.axhline(SY_TOY, color="r", ls="--", label="yield stress 200 MPa")
    ax2.set_xlabel("force (kN)")
    ax2.set_ylabel("stress (MPa)")
    ax2.set_title("Same force, thinner bar: more stress")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "stress_vs_force.png", dpi=120)
    print("saved figures in", OUT)

# %% [markdown]
# ## Try it
# Do the coding tasks, answer the four questions in the README (section F), then run the
# checkpoint.
