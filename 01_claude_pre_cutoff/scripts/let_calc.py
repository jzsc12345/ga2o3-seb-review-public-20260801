# -*- coding: utf-8 -*-
"""LET unit conversion for beta-Ga2O3, per Wang et al. 2026 Eq. (1)."""
RHO_MG_CM3 = 5.88 * 1000.0   # Table I density 5.88 g/cm3
EI_MEV     = 15.6e-6         # Table I average ionization energy 15.6 eV
Q          = 1.6022e-19

def to_pc_per_um(let_mev_cm2_mg):
    ehp_per_cm = let_mev_cm2_mg * RHO_MG_CM3 / EI_MEV
    ehp_per_um = ehp_per_cm * 1e-4
    return ehp_per_um, ehp_per_um * Q * 1e12

def to_let(pc_per_um):
    return pc_per_um / to_pc_per_um(1.0)[1]

if __name__ == "__main__":
    print(f"{'LET [MeV.cm2/mg]':>18} {'ehp/um':>12} {'pC/um':>10}")
    for L in (10, 59.6, 75, 81.4, 82, 100):
        e, p = to_pc_per_um(L)
        print(f"{L:>18} {e:12.4e} {p:10.4f}")
    print()
    print("Inverse -- what the C-file constants actually mean:")
    for c, tag in ((0.492, "Liu2025 mySEU.c  (VALIDATED vs experiment, dir='Ta82')"),
                   (0.36,  "SEB.in mySEU.c   (CURRENT)"),
                   (0.4529,"Wang2026 target  (LET = 75)")):
        print(f"  LET_const={c:<7.4f} pC/um  ->  {to_let(c):6.2f} MeV.cm2/mg   [{tag}]")
    print()
    print(f"charge deficit of current deck: {0.36/0.4529 - 1:+.1%}")
