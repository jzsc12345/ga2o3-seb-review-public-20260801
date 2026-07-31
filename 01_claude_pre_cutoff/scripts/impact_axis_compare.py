# -*- coding: utf-8 -*-
"""beta-Ga2O3 Chynoweth impact-ionisation coefficients, per crystal axis.

Source: 表2.3 Chynoweth 模型中碰撞电离率的参数值
    axis      a [cm^-1]     b [V/cm]
      x        7.90e5        2.92e7
      y        2.16e6        1.77e7
      z        7.06e5        2.10e7

Chynoweth:  alpha(E) = a * exp(-b/E)
ATLAS SELB (Selberherr) reduces to Chynoweth when BETAN=BETAP=1:
    alpha_n = AN1 * exp(-(BN1/E)^BETAN)
"""
import math

AX = {"x": (7.90e5, 2.92e7),
      "y": (2.16e6, 1.77e7),
      "z": (7.06e5, 2.10e7)}
# what the two decks in play actually use
OTHER = {"Wang2026 paper (=z)": (7.06e5, 2.10e7),
         "current deck (an1/bn1)": (2.5e6, 3.96e7)}

def alpha(a, b, E):
    return a * math.exp(-b / E)

fields = [2e6, 3e6, 4e6, 5e6, 6e6, 8e6]
print("alpha [cm^-1] vs field")
print(f"{'E [MV/cm]':>10} " + " ".join(f"{k:>12}" for k in AX))
for E in fields:
    row = " ".join(f"{alpha(*AX[k], E):12.3e}" for k in AX)
    print(f"{E/1e6:10.1f} {row}")

print("\nratio to the z-axis set the paper used:")
for E in fields:
    az = alpha(*AX['z'], E)
    print(f"  E={E/1e6:3.0f} MV/cm   x/z={alpha(*AX['x'],E)/az:8.3e}   "
          f"y/z={alpha(*AX['y'],E)/az:8.3e}")

print("\nwhat the current deck's coefficients give (an1=2.5e6, bn1=3.96e7):")
for E in fields:
    a_cur = alpha(*OTHER['current deck (an1/bn1)'], E)
    az = alpha(*AX['z'], E)
    print(f"  E={E/1e6:3.0f} MV/cm   alpha={a_cur:10.3e}   vs z-axis: {a_cur/az:8.3e}x")

print("\n=> y-axis has BOTH the largest prefactor and the smallest b,")
print("   so it gives the strongest multiplication at every field, i.e.")
print("   the highest current gain and the highest lattice temperature.")
