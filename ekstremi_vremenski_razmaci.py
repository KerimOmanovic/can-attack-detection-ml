import csv
from decimal import Decimal
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


def procitaj_decimalni_broj(tekst):
    return Decimal(tekst.replace(",", "."))


def format_ms(vrijednost):
    return f"{vrijednost:.4f}".replace(".", ",")


# Kvartili i broj razmaka već su izračunati u dijelu 5.4.
putanja_pokazatelja = projekat / "vremenski_razmaci_po_snimku.csv"

with putanja_pokazatelja.open(encoding="utf-8-sig", newline="") as ulaz:
    pokazatelji = {
        red["Snimak"]: red
        for red in csv.DictReader(ulaz, delimiter=";")
    }

redovi_tabele = []
dijagrami = []

for snimak, naziv in datoteke.items():
    print(f"Čitam {naziv}...", flush=True)

    podaci = pokazatelji[snimak]
    q1 = procitaj_decimalni_broj(podaci["Q1 (ms)"])
    medijan = procitaj_decimalni_broj(podaci["Medijan (ms)"])
    q3 = procitaj_decimalni_broj(podaci["Q3 (ms)"])
    iqr = q3 - q1

    donja = q1 - Decimal("1.5") * iqr
    gornja = q3 + Decimal("1.5") * iqr

    n = 0
    ispod = 0
    iznad = 0
    prvi_brk = None
    zadnji_brk = None
    prethodno_vrijeme = None

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            vrijeme = Decimal(red[0])

            if prethodno_vrijeme is not None:
                razmak_ms = (vrijeme - prethodno_vrijeme) * 1000

                if razmak_ms < 0:
                    raise ValueError(f"{naziv}, red {broj_reda}: vrijeme ide unazad.")

                n += 1

                if razmak_ms < donja:
                    ispod += 1
                elif razmak_ms > gornja:
                    iznad += 1
                else:
                    # Brkovi završavaju na krajnjim opaženim vrijednostima
                    # koje su još uvijek unutar IQR granica.
                    if prvi_brk is None or razmak_ms < prvi_brk:
                        prvi_brk = razmak_ms
                    if zadnji_brk is None or razmak_ms > zadnji_brk:
                        zadnji_brk = razmak_ms

            prethodno_vrijeme = vrijeme

    if n != int(podaci["N"]):
        raise ValueError(f"Broj razmaka za {snimak} odstupa od Tabele 16.")

    oznaceno = ispod + iznad
    udio = f"{100 * oznaceno / n:.4f}".replace(".", ",")

    redovi_tabele.append([
        snimak, n, format_ms(donja), format_ms(gornja),
        ispod, iznad, oznaceno, udio,
    ])

    dijagrami.append({
        "label": snimak,
        "q1": float(q1),
        "med": float(medijan),
        "q3": float(q3),
        "whislo": float(prvi_brk),
        "whishi": float(zadnji_brk),
    })

zaglavlje = [
    "Snimak", "N", "Donja granica (ms)", "Gornja granica (ms)",
    "Ispod", "Iznad", "Ukupno označeno", "Udio (%)",
]

putanja_tabele = projekat / "ekstremi_vremenski_razmaci.csv"

with putanja_tabele.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)
    pisac.writerows(redovi_tabele)

print("\nTabela 20. Vremenski razmaci označeni IQR pravilom po snimku")
print("\t".join(zaglavlje))
for red in redovi_tabele:
    print("\t".join(str(vrijednost) for vrijednost in red))

fig, ax = plt.subplots(figsize=(9, 4))
ax.bxp(
    dijagrami,
    orientation="horizontal",
    showfliers=False,
    patch_artist=True,
    widths=0.5,
    boxprops={"facecolor": "#D5E5EF", "edgecolor": "#38658A"},
    medianprops={"color": "#213E54", "linewidth": 2},
)

ax.invert_yaxis()
ax.set_xlim(left=0)
ax.set_xlabel("Vremenski razmak između uzastopnih poruka (ms)")
ax.set_title("Kutije i brkovi po snimku")
ax.set_axisbelow(True)
ax.grid(axis="x", alpha=0.2)

fig.tight_layout()
putanja_grafa = projekat / "grafikon_7_boxplot_vremenski_razmaci.png"
fig.savefig(putanja_grafa, dpi=300, bbox_inches="tight")

print(f"\nSačuvana tabela: {putanja_tabele.name}")
print(f"Sačuvan grafikon: {putanja_grafa.name}")
plt.show()