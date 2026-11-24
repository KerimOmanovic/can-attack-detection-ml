import csv
import json
import sqlite3
from itertools import groupby
from pathlib import Path
from tempfile import TemporaryDirectory

projekat = Path(__file__).parent
folder = projekat / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]


def procitaj_zapise(putanja, broj_datoteke):
    with putanja.open(encoding="utf-8-sig", newline="") as ulaz:
        for red in csv.reader(ulaz):
            if red:
                # Čuvamo svako polje tačno kako je učitano, uključujući početne nule.
                zapis = json.dumps(red, separators=(",", ":"))
                yield zapis, broj_datoteke


ponavljanja_unutar = [0] * len(datoteke)
ponavljanja_izmedju = 0
broj_razlicitih_zapisa = 0
broj_zapisa_koji_se_ponavljaju = 0
ukupno_redova = 0
primjer = None

with TemporaryDirectory(dir=projekat) as privremeni_folder:
    baza = sqlite3.connect(Path(privremeni_folder) / "provjera.db")

    try:
        baza.execute("PRAGMA temp_store = FILE")
        baza.execute("CREATE TABLE poruke (zapis TEXT, datoteka INTEGER)")

        for broj, naziv in enumerate(datoteke):
            print(f"Učitavam {naziv}...", flush=True)
            prije = baza.total_changes

            with baza:
                baza.executemany(
                    "INSERT INTO poruke VALUES (?, ?)",
                    procitaj_zapise(folder / naziv, broj),
                )

            ukupno_redova += baza.total_changes - prije

        print("Poredim zapise iz sve četiri datoteke...", flush=True)

        # Za svaki zapis dobijamo koliko se puta pojavio u svakoj datoteci.
        rezultat = baza.execute("""
                                SELECT zapis, datoteka, COUNT(*)
                                FROM poruke
                                GROUP BY zapis, datoteka
                                ORDER BY zapis, datoteka
                                """)

        for zapis, grupa in groupby(rezultat, key=lambda red: red[0]):
            pojave = [(broj, kolicina) for _, broj, kolicina in grupa]
            broj_razlicitih_zapisa += 1

            for broj, kolicina in pojave:
                ponavljanja_unutar[broj] += kolicina - 1

            ponavljanja_izmedju += len(pojave) - 1

            if sum(kolicina for _, kolicina in pojave) > 1:
                broj_zapisa_koji_se_ponavljaju += 1
                if primjer is None:
                    primjer = (json.loads(zapis), pojave)
    finally:
        baza.close()

print("\nPonavljanja unutar pojedinačnih datoteka:")
for naziv, broj in zip(datoteke, ponavljanja_unutar):
    print(f"{naziv}: {broj}")

print(f"\nUkupno pregledanih redova: {ukupno_redova}")
print(f"Različitih potpunih zapisa: {broj_razlicitih_zapisa}")
print(f"Različitih zapisa koji se pojavljuju više puta: "
      f"{broj_zapisa_koji_se_ponavljaju}")
print(f"Dodatnih pojavljivanja unutar datoteka: {sum(ponavljanja_unutar)}")
print(f"Dodatnih pojavljivanja između datoteka: {ponavljanja_izmedju}")
print(f"Ukupno dodatnih pojavljivanja: "
      f"{ukupno_redova - broj_razlicitih_zapisa}")

if primjer:
    zapis, pojave = primjer
    print("\nPrimjer potpuno jednakog zapisa:")
    print(",".join(zapis))
    for broj, kolicina in pojave:
        print(f"  {datoteke[broj]}: {kolicina} puta")