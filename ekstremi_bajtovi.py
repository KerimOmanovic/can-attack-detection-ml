import csv
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

# Za svaku poziciju brojim koliko se puta javila svaka vrijednost od 0 do 255.
frekvencije = [[0] * 256 for _ in range(8)]

for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            dlc = int(red[2])
            bajtovi = red[3:-1]

            if not 0 <= dlc <= 8 or len(bajtovi) != dlc:
                raise ValueError(f"{naziv}, red {broj_reda}: broj bajtova odstupa od DLC-a.")

            for pozicija, bajt in enumerate(bajtovi):
                frekvencije[pozicija][int(bajt, 16)] += 1


def vrijednost_na_rangu(brojevi, rang):
    zbir = 0
    for vrijednost, broj in enumerate(brojevi):
        zbir += broj
        if zbir >= rang:
            return vrijednost


def decimalni_zapis(broj, decimale):
    return f"{broj:.{decimale}f}".replace(".", ",")


# Broj prisutnih vrijednosti iz Tabele 14 služi kao provjera.
ocekivani_n = [
    16_569_475, 16_569_475, 16_422_264, 16_422_264,
    16_422_264, 16_368_813, 16_368_810, 16_368_810,
]

redovi = []
dijagrami = []

for pozicija, brojevi in enumerate(frekvencije):
    naziv = f"DATA[{pozicija}]"
    n = sum(brojevi)

    if n != ocekivani_n[pozicija]:
        raise ValueError(f"Broj prisutnih vrijednosti za {naziv} odstupa od Tabele 14.")

    # Isti način određivanja kvartila i medijana kao u dijelu 5.2.
    q1 = vrijednost_na_rangu(brojevi, (n + 3) // 4)
    q3 = vrijednost_na_rangu(brojevi, (3 * n + 3) // 4)
    medijan = (
                      vrijednost_na_rangu(brojevi, (n + 1) // 2)
                      + vrijednost_na_rangu(brojevi, (n + 2) // 2)
              ) / 2

    iqr = q3 - q1
    donja = q1 - 1.5 * iqr
    gornja = q3 + 1.5 * iqr

    prisutne = [v for v, broj in enumerate(brojevi) if broj > 0]
    ispod = sum(brojevi[v] for v in prisutne if v < donja)
    iznad = sum(brojevi[v] for v in prisutne if v > gornja)
    oznaceno = ispod + iznad

    redovi.append([
        naziv, n, q1, q3, iqr,
        decimalni_zapis(donja, 1), decimalni_zapis(gornja, 1),
        ispod, iznad, oznaceno, decimalni_zapis(100 * oznaceno / n, 4),
    ])

    # Brkovi završavaju na krajnjim opaženim vrijednostima unutar granica.
    unutar = [v for v in prisutne if donja <= v <= gornja]
    izvan = [v for v in prisutne if v < donja or v > gornja]

    dijagrami.append({
        "label": naziv,
        "q1": q1,
        "med": medijan,
        "q3": q3,
        "whislo": min(unutar),
        "whishi": max(unutar),
        "fliers": izvan,
    })

zaglavlje = [
    "Varijabla", "N", "Q1", "Q3", "IQR", "Donja granica", "Gornja granica",
    "Ispod", "Iznad", "Ukupno označeno", "Udio (%)",
]

putanja_tabele = projekat / "ekstremi_bajtovi_iqr.csv"

with putanja_tabele.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)
    pisac.writerows(redovi)

print("\nTabela 19. Vrijednosti bajtova označene IQR pravilom")
print("\t".join(zaglavlje))
for red in redovi:
    print("\t".join(str(vrijednost) for vrijednost in red))

fig, ax = plt.subplots(figsize=(10, 5.5))

ax.bxp(
    dijagrami,
    orientation="horizontal",
    patch_artist=True,
    widths=0.55,
    boxprops={"facecolor": "#D5E5EF", "edgecolor": "#38658A"},
    medianprops={"color": "#213E54", "linewidth": 2},
    flierprops={
        "marker": ".",
        "markersize": 3,
        "markeredgecolor": "#B46130",
    },
)

ax.invert_yaxis()
ax.set_xlabel("Vrijednost bajta")
ax.set_xticks([0, 32, 64, 96, 128, 160, 192, 224, 255])
ax.set_xlim(-5, 260)
ax.set_axisbelow(True)
ax.grid(axis="x", alpha=0.2)

fig.tight_layout()
putanja_grafa = projekat / "grafikon_6_boxplot_bajtovi.png"
fig.savefig(putanja_grafa, dpi=300, bbox_inches="tight")

print(f"\nSačuvana tabela: {putanja_tabele.name}")
print(f"Sačuvan grafikon: {putanja_grafa.name}")
plt.show()