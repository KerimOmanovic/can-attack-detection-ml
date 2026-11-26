from pathlib import Path

import matplotlib.pyplot as plt


projekat = Path(__file__).resolve().parent

# Frekvencije iz Tabele 7.
broj_po_dlc = {2: 147_211, 5: 53_451, 6: 3, 8: 16_368_810}
ukupno = sum(broj_po_dlc.values())


def vrijednost_na_rangu(rang):
    zbir = 0
    for dlc, broj in sorted(broj_po_dlc.items()):
        zbir += broj
        if zbir >= rang:
            return dlc


q1 = vrijednost_na_rangu((ukupno + 3) // 4)
medijan = vrijednost_na_rangu((ukupno + 1) // 2)
q3 = vrijednost_na_rangu((3 * ukupno + 3) // 4)
iqr = q3 - q1

donja = q1 - 1.5 * iqr
gornja = q3 + 1.5 * iqr

oznacene_duzine = [
    dlc for dlc in sorted(broj_po_dlc) if dlc < donja or dlc > gornja
]
unutar_granica = [dlc for dlc in broj_po_dlc if donja <= dlc <= gornja]
broj_oznacenih = sum(broj_po_dlc[dlc] for dlc in oznacene_duzine)


def format_broja(broj):
    return f"{broj:,}".replace(",", ".")


def format_udjela(broj):
    return f"{100 * broj / ukupno:.6f}".replace(".", ",") + " %"


print(f"Q1 = {q1}, medijan = {medijan}, Q3 = {q3}, IQR = {iqr}")
print(f"Donja granica: {donja:g} bajtova")
print(f"Gornja granica: {gornja:g} bajtova")

print("\nTabela 18. Poruke označene IQR pravilom prema dužini")
print("DLC\tBroj označenih poruka\tUdio u svim porukama")

for dlc in oznacene_duzine:
    broj = broj_po_dlc[dlc]
    print(f"{dlc}\t{format_broja(broj)}\t{format_udjela(broj)}")

print(f"Ukupno\t{format_broja(broj_oznacenih)}\t{format_udjela(broj_oznacenih)}")

# Svaka tačka predstavlja jednu različitu označenu dužinu.
# Uz tačku ispisujem koliko poruka ima tu dužinu.
statistika = {
    "med": medijan,
    "q1": q1,
    "q3": q3,
    "whislo": min(unutar_granica),
    "whishi": max(unutar_granica),
    "fliers": oznacene_duzine,
}

fig, ax = plt.subplots(figsize=(8, 3))

ax.bxp(
    [statistika],
    orientation="horizontal",
    widths=0.3,
    medianprops={"color": "#38658A", "linewidth": 3},
    flierprops={
        "marker": "o",
        "markerfacecolor": "#B46130",
        "markeredgecolor": "#B46130",
        "markersize": 7,
    },
)

for dlc in oznacene_duzine:
    ax.annotate(
        f"n = {format_broja(broj_po_dlc[dlc])}",
        xy=(dlc, 1),
        xytext=(0, 13),
        textcoords="offset points",
        ha="center",
        fontsize=9,
    )

ax.set_xlabel("Dužina sadržaja poruke (bajtovi)")
ax.set_yticks([])
ax.set_xticks(range(0, 9))
ax.set_xlim(-0.3, 8.6)
ax.grid(axis="x", alpha=0.2)

fig.tight_layout()
putanja = projekat / "grafikon_5_boxplot_dlc.png"
fig.savefig(putanja, dpi=300, bbox_inches="tight")

print(f"\nSačuvan grafikon: {putanja.name}")
plt.show()