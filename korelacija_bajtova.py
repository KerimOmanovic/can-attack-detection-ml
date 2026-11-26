import csv
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]

nazivi = [f"DATA[{i}]" for i in range(8)]
parovi = list(combinations(range(8), 2))

# Za svaki par pozicija brojim pojavljivanja parova vrijednosti od 0 do 255.
zajednicke_frekvencije = {
    par: np.zeros((256, 256), dtype=np.int64) for par in parovi
}


def obradi_blok(sadrzaj, dlc):
    # Sve poruke u bloku imaju isti DLC i sadrže samo prisutne bajtove.
    podaci = np.frombuffer(sadrzaj, dtype=np.uint8).reshape(-1, dlc)
    podaci = podaci.astype(np.int32)

    for i, j in combinations(range(dlc), 2):
        kodovi = podaci[:, i] * 256 + podaci[:, j]
        brojanja = np.bincount(kodovi, minlength=256 * 256)
        zajednicke_frekvencije[i, j] += brojanja.reshape(256, 256)


for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)
    blokovi = {}

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            dlc = int(red[2])
            bajtovi = bytes.fromhex(" ".join(red[3:-1]))

            if not 0 <= dlc <= 8 or len(bajtovi) != dlc:
                raise ValueError(f"{naziv}, red {broj_reda}: provjeri DLC i sadržaj.")

            if dlc < 2:
                continue

            if dlc not in blokovi:
                blokovi[dlc] = bytearray()

            blok = blokovi[dlc]
            blok.extend(bajtovi)

            if len(blok) >= 100_000 * dlc:
                obradi_blok(blok, dlc)
                blok.clear()

    for dlc, blok in blokovi.items():
        if blok:
            obradi_blok(blok, dlc)


def centrirani_rangovi(frekvencije):
    # Jednake vrijednosti dobijaju prosjek rangova koje zauzimaju.
    zadnji_rang = np.cumsum(frekvencije)
    prosjecni_rang = zadnji_rang - (frekvencije - 1) / 2
    sredina_rangova = (frekvencije.sum() + 1) / 2
    return prosjecni_rang - sredina_rangova


def spearman_iz_frekvencija(tabela):
    frekvencije_x = tabela.sum(axis=1)
    frekvencije_y = tabela.sum(axis=0)

    rang_x = centrirani_rangovi(frekvencije_x)
    rang_y = centrirani_rangovi(frekvencije_y)

    brojnik = rang_x @ tabela @ rang_y
    zbir_x = np.sum(frekvencije_x * rang_x ** 2)
    zbir_y = np.sum(frekvencije_y * rang_y ** 2)

    if zbir_x == 0 or zbir_y == 0:
        raise ValueError("Jedna pozicija ima konstantnu vrijednost u ovom paru.")

    return brojnik / np.sqrt(zbir_x * zbir_y)


# Provjera prema broju prisutnih vrijednosti iz Tabele 14.
# Ako postoje obje pozicije, broj parova odgovara kasnijoj poziciji.
broj_prisutnih = [
    16_569_475, 16_569_475, 16_422_264, 16_422_264,
    16_422_264, 16_368_813, 16_368_810, 16_368_810,
]

matrica = np.eye(8)
rezultati = []

for i, j in parovi:
    tabela = zajednicke_frekvencije[i, j]
    n = int(tabela.sum())

    if n != broj_prisutnih[j]:
        raise ValueError(f"Broj parova za {nazivi[i]} i {nazivi[j]} odstupa od Tabele 14.")

    rho = spearman_iz_frekvencija(tabela)
    matrica[i, j] = rho
    matrica[j, i] = rho
    rezultati.append((nazivi[i], nazivi[j], n, rho))

# Sortiram po jačini prije zaokruživanja. Predznak ostaje vidljiv.
rezultati.sort(key=lambda red: abs(red[3]), reverse=True)

putanja_tabele = projekat / "korelacija_bajtova_spearman.csv"
with putanja_tabele.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(["Prva pozicija", "Druga pozicija", "Broj parova", "Spearman ρ"])
    for prva, druga, n, rho in rezultati:
        pisac.writerow([prva, druga, n, f"{rho:.6f}".replace(".", ",")])

print("\nTabela 23. Tri para s najvećom apsolutnom Spearmanovom korelacijom")
print("Prva pozicija\tDruga pozicija\tBroj parova\tSpearman ρ")
for prva, druga, n, rho in rezultati[:3]:
    broj = f"{n:,}".replace(",", ".")
    koeficijent = f"{rho:.4f}".replace(".", ",")
    print(f"{prva}\t{druga}\t{broj}\t{koeficijent}")

print("\nMatrica Spearmanovih korelacija:")
print("\t" + "\t".join(nazivi))
for naziv, red in zip(nazivi, matrica):
    vrijednosti = [f"{r:.2f}".replace(".", ",") for r in red]
    print(naziv + "\t" + "\t".join(vrijednosti))

fig, ax = plt.subplots(figsize=(9, 7))
slika = ax.imshow(matrica, cmap="RdBu_r", vmin=-1, vmax=1)

ax.set_xticks(range(8), nazivi, rotation=45, ha="right")
ax.set_yticks(range(8), nazivi)

for i in range(8):
    for j in range(8):
        rho = matrica[i, j]
        tekst = f"{rho:.2f}".replace(".", ",")
        boja = "white" if abs(rho) >= 0.60 else "black"
        ax.text(j, i, tekst, ha="center", va="center", color=boja)

skala = fig.colorbar(slika, ax=ax, shrink=0.85)
skala.set_label("Spearmanov koeficijent korelacije (ρ)")

fig.tight_layout()
putanja_grafa = projekat / "grafikon_10_heatmapa_bajtovi.png"
fig.savefig(putanja_grafa, dpi=300, bbox_inches="tight")

print(f"\nSačuvana tabela: {putanja_tabele.name}")
print(f"Sačuvan grafikon: {putanja_grafa.name}")
plt.show()