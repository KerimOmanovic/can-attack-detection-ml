import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]

parovi = Counter()

for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for red in csv.reader(ulaz):
            if not red:
                continue

            dlc = int(red[2])
            if dlc < 7:
                continue

            # Sadržaj počinje na poziciji 3 u CSV redu.
            data_3 = int(red[3 + 3], 16)
            data_6 = int(red[3 + 6], 16)
            parovi[data_3, data_6] += 1

ukupno = sum(parovi.values())

if ukupno != 16_368_810:
    raise ValueError(
        f"Pronađeno je {ukupno} parova. Prema Tabeli 14 očekuje se 16.368.810."
    )


def format_broja(broj):
    return f"{broj:,}".replace(",", ".")


def format_udjela(broj, ukupno_u_grupi):
    return f"{100 * broj / ukupno_u_grupi:.2f}".replace(".", ",")


# Za svaku grupu računam koliko poruka ima DATA[6] = 0.
broj_data3_nula = sum(
    broj for (data_3, data_6), broj in parovi.items() if data_3 == 0
)
broj_data6_nula = sum(
    broj for (data_3, data_6), broj in parovi.items() if data_6 == 0
)
obje_nule = parovi[0, 0]

grupe = [
    ("DATA[3] = 0", broj_data3_nula, obje_nule),
    ("DATA[3] > 0", ukupno - broj_data3_nula, broj_data6_nula - obje_nule),
    ("Ukupno", ukupno, broj_data6_nula),
]

zaglavlje = [
    "Grupa poruka",
    "Broj parova",
    "Broj s DATA[6] = 0",
    "Udio s DATA[6] = 0 (%)",
]

putanja_tabele = projekat / "odnos_bajtova_data3_data6.csv"

print("\nTabela 21. Udio nula na poziciji DATA[6] prema vrijednosti DATA[3]")
print("\t".join(zaglavlje))

with putanja_tabele.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)

    for grupa, broj_parova, broj_nula in grupe:
        udio = format_udjela(broj_nula, broj_parova)
        pisac.writerow([grupa, broj_parova, broj_nula, udio])
        print(
            f"{grupa}\t{format_broja(broj_parova)}\t"
            f"{format_broja(broj_nula)}\t{udio}"
        )

print(f"\nBroj različitih parova: {format_broja(len(parovi))}")
print("Pet najčešćih parova (DATA[3], DATA[6]):")

for (data_3, data_6), broj in parovi.most_common(5):
    print(
        f"({data_3}, {data_6})\t{format_broja(broj)} poruka\t"
        f"{format_udjela(broj, ukupno)} % svih parova"
    )

# Rjeđe parove crtam prve kako bi česti parovi ostali vidljivi.
poredani = sorted(parovi.items(), key=lambda stavka: stavka[1])
x = [par[0] for par, broj in poredani]
y = [par[1] for par, broj in poredani]
ucestalosti = [broj for par, broj in poredani]

fig, ax = plt.subplots(figsize=(8, 6))

tacke = ax.scatter(
    x, y,
    c=ucestalosti,
    norm=LogNorm(),
    cmap="viridis",
    s=7,
    linewidths=0,
)

ax.set_xlabel("DATA[3] – vrijednost četvrtog bajta")
ax.set_ylabel("DATA[6] – vrijednost sedmog bajta")
ax.set_xlim(-3, 258)
ax.set_ylim(-3, 258)
ax.set_aspect("equal")
ax.set_xticks([0, 32, 64, 96, 128, 160, 192, 224, 255])
ax.set_yticks([0, 32, 64, 96, 128, 160, 192, 224, 255])

skala = fig.colorbar(tacke, ax=ax)
skala.set_label("Broj pojavljivanja para (logaritamska skala)")

fig.tight_layout()
putanja_grafa = projekat / "grafikon_8_odnos_data3_data6.png"
fig.savefig(putanja_grafa, dpi=300, bbox_inches="tight")

print(f"\nSačuvana tabela: {putanja_tabele.name}")
print(f"Sačuvan grafikon: {putanja_grafa.name}")
plt.show()