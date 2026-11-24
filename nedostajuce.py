import csv
from pathlib import Path

folder = Path(__file__).parent / "Car-Hacking Dataset"
datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]

bajtovi = [f"DATA[{i}]" for i in range(8)]
varijable = ["Timestamp", "CAN ID", "DLC", *bajtovi, "Flag"]

nedostaje = dict.fromkeys(varijable, 0)
nije_primjenjivo = dict.fromkeys(varijable, 0)

# Prazno polje ili izričita tekstualna oznaka nedostajanja.
oznake_nedostajanja = {"", "na", "n/a", "nan", "null", "none", "?"}

ukupno = 0
popunjeno_svih_12 = 0
potpuni_prema_dlc = 0

for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            # U prvom poglavlju provjerili smo ovaj raspored na svim redovima.
            dlc = int(red[2])
            if not 0 <= dlc <= 8 or len(red) != dlc + 4:
                raise ValueError(f"Neočekivan raspored: {naziv}, red {broj_reda}")

            ukupno += 1
            nedostaje_u_redu = False

            # Uparujemo samo polja koja ova poruka treba imati.
            nazivi_u_redu = ["Timestamp", "CAN ID", "DLC", *bajtovi[:dlc], "Flag"]
            for varijabla, vrijednost in zip(nazivi_u_redu, red):
                if vrijednost.strip().lower() in oznake_nedostajanja:
                    nedostaje[varijabla] += 1
                    nedostaje_u_redu = True

            for varijabla in bajtovi[dlc:]:
                nije_primjenjivo[varijabla] += 1

            if not nedostaje_u_redu:
                potpuni_prema_dlc += 1
                if dlc == 8:
                    popunjeno_svih_12 += 1

print(f"\nUkupno zapisa: {ukupno}")
print("\nVarijabla | Nedostaje očekivana vrijednost | % svih zapisa | "
      "Nije primjenjivo | % svih zapisa")

for varijabla in varijable:
    broj = nedostaje[varijabla]
    broj_np = nije_primjenjivo[varijabla]
    print(f"{varijabla} | {broj} | {100 * broj / ukupno:.4f}% | "
          f"{broj_np} | {100 * broj_np / ukupno:.4f}%")

print(f"\nSvih 12 polja popunjeno: {popunjeno_svih_12}")
print(f"Barem jedno od 12 polja bez vrijednosti: {ukupno - popunjeno_svih_12}")
print(f"Sve očekivane vrijednosti prisutne prema DLC-u: {potpuni_prema_dlc}")
print(f"Nedostaje barem jedna očekivana vrijednost: {ukupno - potpuni_prema_dlc}")