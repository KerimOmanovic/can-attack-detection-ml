import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = {
    "DoS": "DoS_dataset.csv",
    "Fuzzy": "Fuzzy_dataset.csv",
    "Gear": "gear_dataset.csv",
    "RPM": "RPM_dataset.csv",
}
odabrani_id = ["0316", "043f"]


def format_broja(broj):
    return f"{broj:,}".replace(",", ".")


def format_procenta(procenat):
    return f"{procenat:.2f}".replace(".", ",")


# Za svaki snimak odvojeno brojim R i T za dva odabrana identifikatora.
rezultati = {}

for snimak, naziv in datoteke.items():
    print(f"Čitam {naziv}...", flush=True)
    brojevi = {can_id: Counter() for can_id in odabrani_id}

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            can_id = red[1]
            if can_id in brojevi:
                oznaka = red[-1]
                if oznaka not in ("R", "T"):
                    raise ValueError(f"Nepoznata oznaka u {naziv}, red {broj_reda}.")
                brojevi[can_id][oznaka] += 1

    rezultati[snimak] = brojevi

# Zbir četiri snimka za svaki ID treba odgovarati njegovom redu iz Tabele 11.
tabela_11 = {
    "0316": {"R": 776_188, "T": 655_120},
    "043f": {"R": 766_956, "T": 597_502},
}

for can_id in odabrani_id:
    for oznaka in ("R", "T"):
        zbir = sum(rezultati[snimak][can_id][oznaka] for snimak in datoteke)
        if zbir != tabela_11[can_id][oznaka]:
            raise ValueError(f"Zbir za {can_id}, oznaka {oznaka}, odstupa od Tabele 11.")

zaglavlje = ["Snimak", "CAN ID", "Broj R", "Broj T", "Ukupno", "T (%)"]
putanja_tabele = projekat / "can_id_flag_po_datoteci.csv"

print("\nTabela 12. Udio ubačenih poruka po identifikatoru i snimku")
print("\t".join(zaglavlje))

with putanja_tabele.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)

    for snimak, brojevi in rezultati.items():
        for can_id in odabrani_id:
            r = brojevi[can_id]["R"]
            t = brojevi[can_id]["T"]
            ukupno = r + t
            udio = format_procenta(100 * t / ukupno) if ukupno else "N/P"

            pisac.writerow([snimak, can_id, r, t, ukupno, udio])
            print(
                f"{snimak}\t{can_id}\t{format_broja(r)}\t{format_broja(t)}\t"
                f"{format_broja(ukupno)}\t{udio}"
            )

# U svakom paru prvi stubac predstavlja 0316, a drugi 043f.
fig, ax = plt.subplots(figsize=(9, 5))
snimci = list(datoteke)
sirina = 0.34
boje = ["#38658A", "#B46130"]

for i, can_id in enumerate(odabrani_id):
    for j, snimak in enumerate(snimci):
        x = j + (i - 0.5) * sirina
        brojac = rezultati[snimak][can_id]
        ukupno = brojac.total()
        procenat = 100 * brojac["T"] / ukupno if ukupno else 0
        oznaka = format_procenta(procenat) + " %" if ukupno else "N/P"

        ax.bar(
            x, procenat, width=sirina, color=boje[i],
            label=can_id if j == 0 else None,
        )
        ax.text(x, procenat + 1, oznaka, ha="center", va="bottom", fontsize=9)

ax.set_xticks(range(len(snimci)), snimci)
ax.set_xlabel("Snimak")
ax.set_ylabel("Udio ubačenih poruka unutar CAN ID-a (%)")
ax.set_ylim(0, 108)
ax.set_yticks(range(0, 101, 20))
ax.set_axisbelow(True)
ax.grid(axis="y", alpha=0.2)
ax.legend(title="CAN ID")

fig.tight_layout()
putanja_grafa = projekat / "grafikon_3_can_id_po_datoteci.png"
fig.savefig(putanja_grafa, dpi=300, bbox_inches="tight")

print("\nZbirovi za oba identifikatora odgovaraju Tabeli 11.")
print(f"Sačuvana tabela: {putanja_tabele.name}")
print(f"Sačuvan grafikon: {putanja_grafa.name}")
plt.show()