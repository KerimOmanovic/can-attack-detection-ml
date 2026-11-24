import csv
from collections import Counter
from pathlib import Path

folder = Path(__file__).parent / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]

ukupno_zapisa = 0

for naziv in datoteke:
    broj_zapisa = 0
    prazni_redovi = 0
    broj_odstupanja = 0
    raspodjela_polja = Counter()

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for red in csv.reader(ulaz):
            if not red:
                prazni_redovi += 1
                continue

            broj_zapisa += 1
            broj_polja = len(red)
            raspodjela_polja[broj_polja] += 1

            # DLC je treće polje u redu.
            try:
                dlc = int(red[2])
            except (IndexError, ValueError):
                broj_odstupanja += 1
                continue

            # Uz bajtove sadržaja očekujemo vrijeme, CAN ID, DLC i oznaku.
            if not (0 <= dlc <= 8) or broj_polja != dlc + 4:
                broj_odstupanja += 1

    ukupno_zapisa += broj_zapisa

    print(f"\n{naziv}")
    print(f"Broj nepraznih zapisa: {broj_zapisa}")
    print(f"Broj praznih redova: {prazni_redovi}")

    for broj_polja, broj_redova in sorted(raspodjela_polja.items()):
        print(f"  Zapisa sa {broj_polja} polja: {broj_redova}")

    print(f"Odstupanja od očekivane dužine prema DLC-u: {broj_odstupanja}")

print(f"\nUkupno zapisa u četiri datoteke: {ukupno_zapisa}")