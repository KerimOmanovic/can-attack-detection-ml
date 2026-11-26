import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]


def format_broja(broj):
    return f"{broj:,}".replace(",", ".")


def format_procenta(broj, ukupno, decimale=2):
    return f"{100 * broj / ukupno:.{decimale}f}".replace(".", ",")


ucestalosti = Counter()

for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for red in csv.reader(ulaz):
            if red:
                ucestalosti[red[1]] += 1

ukupno = sum(ucestalosti.values())

if ukupno != 16_569_475:
    raise ValueError(
        f"Pročitano je {format_broja(ukupno)} zapisa, "
        "a u dijelu 1.2 prebrojano je 16.569.475."
    )

# Kod istog broja poruka identifikatore poredam po njihovoj oznaci.
poredani = sorted(ucestalosti.items(), key=lambda par: (-par[1], par[0]))
prvih_deset = poredani[:10]

# Potpuna raspodjela svih identifikatora.
putanja_tabele = projekat / "ucestalost_svih_can_id.csv"

with putanja_tabele.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(["CAN ID", "Broj poruka", "Udio (%)"])

    for can_id, broj in poredani:
        pisac.writerow([can_id, broj, format_procenta(broj, ukupno, 6)])

# Ispis koji ćemo koristiti za Word.
print(f"\nUkupan broj poruka: {format_broja(ukupno)}")
print(f"Broj različitih CAN ID-eva: {format_broja(len(ucestalosti))}")

print("\nTabela 10. Deset najčešćih CAN identifikatora")
print("CAN ID\tBroj poruka\tUdio (%)")

for can_id, broj in prvih_deset:
    print(f"{can_id}\t{format_broja(broj)}\t{format_procenta(broj, ukupno)}")

zbir_prvih_deset = sum(broj for _, broj in prvih_deset)
print(
    f"\nDeset najčešćih zajedno: {format_broja(zbir_prvih_deset)} poruka "
    f"({format_procenta(zbir_prvih_deset, ukupno)} %)"
)

najmanji_broj = poredani[-1][1]
najrjedi = [can_id for can_id, broj in poredani if broj == najmanji_broj]

print(f"\nNajmanji broj poruka za jedan CAN ID: {format_broja(najmanji_broj)}")
print(f"Broj identifikatora s tom učestalošću: {format_broja(len(najrjedi))}")
print("Primjeri najrjeđih CAN ID-eva:", ", ".join(najrjedi[:10]))

# Grafikon 2 prikazuje udjele u odnosu na sve poruke.
identifikatori = [can_id for can_id, _ in prvih_deset]
procenti = [100 * broj / ukupno for _, broj in prvih_deset]

fig, ax = plt.subplots(figsize=(8, 5))
stubovi = ax.barh(identifikatori, procenti, color="#38658A")
ax.invert_yaxis()
ax.set_xlabel("Udio u ukupnom broju poruka (%)")
ax.set_ylabel("CAN ID")
ax.set_xlim(0, max(procenti) * 1.2)
ax.set_axisbelow(True)
ax.grid(axis="x", alpha=0.2)

oznake = [f"{p:.2f}".replace(".", ",") + " %" for p in procenti]
ax.bar_label(stubovi, labels=oznake, padding=4)

fig.tight_layout()
putanja_grafa = projekat / "grafikon_2_can_id.png"
fig.savefig(putanja_grafa, dpi=300, bbox_inches="tight")

print(f"\nSačuvana tabela: {putanja_tabele.name}")
print(f"Sačuvan grafikon: {putanja_grafa.name}")
plt.show()