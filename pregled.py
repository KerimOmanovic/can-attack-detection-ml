from pathlib import Path
from itertools import islice

datoteka = Path(__file__).parent / "Car-Hacking Dataset" / "DoS_dataset.csv"

with datoteka.open(encoding="utf-8-sig") as ulaz:
    for red in islice(ulaz, 5):
        print(red.rstrip())

print("\nPrvi zapis sa 6 polja:")

with datoteka.open(encoding="utf-8-sig") as ulaz:
    for broj_reda, red in enumerate(ulaz, start=1):
        polja = red.strip().split(",")
        if len(polja) == 6:
            print(f"Red {broj_reda}: {polja}")
            break