import csv
from pathlib import Path

datoteka = Path(__file__).parent / "Car-Hacking Dataset" / "DoS_dataset.csv"

with datoteka.open(encoding="utf-8-sig", newline="") as ulaz:
    prvi_red = next(csv.reader(ulaz))

nazivi = ["Timestamp", "CAN ID", "DLC"]
nazivi.extend(f"DATA[{i}]" for i in range(len(prvi_red[3:-1])))
nazivi.append("Flag")

for naziv, vrijednost in zip(nazivi, prvi_red):
    print(f"{naziv:10} | {vrijednost!r:20} | {type(vrijednost).__name__}")