import csv
from collections import Counter
from decimal import Decimal
from pathlib import Path

import numpy as np


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = {
    "DoS": "DoS_dataset.csv",
    "Fuzzy": "Fuzzy_dataset.csv",
    "Gear": "gear_dataset.csv",
    "RPM": "RPM_dataset.csv",
}


def izracunaj_pokazatelje(frekvencije):
    # Svaki različit razmak čuvam jednom, zajedno s brojem pojavljivanja.
    razmaci_us = sorted(frekvencije)
    vrijednosti = np.asarray(razmaci_us, dtype=float) / 1000
    brojevi = np.array([frekvencije[r] for r in razmaci_us], dtype=np.int64)
    kumulativno = np.cumsum(brojevi)
    n = int(kumulativno[-1])

    def vrijednost_na_rangu(rang):
        indeks = np.searchsorted(kumulativno, rang, side="left")
        return vrijednosti[indeks]

    q1 = vrijednost_na_rangu((n + 3) // 4)
    q3 = vrijednost_na_rangu((3 * n + 3) // 4)
    medijan = (
                      vrijednost_na_rangu((n + 1) // 2)
                      + vrijednost_na_rangu((n + 2) // 2)
              ) / 2

    sredina = np.average(vrijednosti, weights=brojevi)
    odstupanja = vrijednosti - sredina
    sd = np.sqrt(np.average(odstupanja ** 2, weights=brojevi))

    # Iz obračuna skraćene sredine izostavljam po 5 % razmaka sa svakog kraja.
    odbaceno = n // 20
    poceci_grupa = kumulativno - brojevi
    zadrzano = np.maximum(
        0,
        np.minimum(kumulativno, n - odbaceno)
        - np.maximum(poceci_grupa, odbaceno),
        )
    skracena = np.average(vrijednosti, weights=zadrzano)

    return {
        "N": n,
        "Broj nula": frekvencije[0],
        "Min (ms)": vrijednosti[0],
        "Q1 (ms)": q1,
        "Medijan (ms)": medijan,
        "Q3 (ms)": q3,
        "Maks (ms)": vrijednosti[-1],
        "IQR (ms)": q3 - q1,
        "Sredina (ms)": sredina,
        "Skraćena sredina (ms)": skracena,
        "SD (ms)": sd,
        "CV (%)": 100 * sd / sredina if sredina else None,
        "Asimetričnost": np.average((odstupanja / sd) ** 3, weights=brojevi)
        if sd else None,
        "Eksces": np.average((odstupanja / sd) ** 4, weights=brojevi) - 3
        if sd else None,
    }


def formatiraj(vrijednost):
    if vrijednost is None:
        return "N/P"
    if isinstance(vrijednost, int):
        return str(vrijednost)
    return f"{vrijednost:.4f}".replace(".", ",")


rezultati = []

for snimak, naziv in datoteke.items():
    print(f"Čitam {naziv}...", flush=True)
    frekvencije = Counter()
    prethodno_us = None

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            vrijeme = Decimal(red[0]) * 1_000_000
            vrijeme_us = int(vrijeme)
            if vrijeme_us != vrijeme:
                raise ValueError(f"{naziv}, red {broj_reda}: vrijeme ima preciznost ispod 1 µs.")

            if prethodno_us is not None:
                razmak = vrijeme_us - prethodno_us
                if razmak < 0:
                    raise ValueError(f"{naziv}, red {broj_reda}: vrijeme ide unazad.")
                frekvencije[razmak] += 1

            prethodno_us = vrijeme_us

    rezultati.append({"Snimak": snimak, **izracunaj_pokazatelje(frekvencije)})

ukupno = sum(red["N"] for red in rezultati)
if ukupno != 16_569_471:
    raise ValueError(f"Dobijeno je {ukupno} razmaka, a očekivano je 16.569.471.")

zaglavlje = list(rezultati[0])
putanja = projekat / "vremenski_razmaci_po_snimku.csv"

with putanja.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)

    print("\nVremenski razmaci između uzastopnih CAN poruka")
    print("\t".join(zaglavlje))

    for rezultat in rezultati:
        red = [rezultat["Snimak"]]
        red.extend(formatiraj(rezultat[kolona]) for kolona in zaglavlje[1:])
        pisac.writerow(red)
        print("\t".join(red))

print(f"\nUkupno razmaka: {ukupno:,}".replace(",", "."))
print(f"Sačuvana tabela: {putanja.name}")