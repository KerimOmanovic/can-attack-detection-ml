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

nazivi = ["CAN ID", "DLC"]
nazivi.extend(f"DATA[{i}]" for i in range(8))
nazivi.append("Flag")

ucestalosti = {naziv: Counter() for naziv in nazivi}
vremena = set()
ukupno_zapisa = 0

for naziv_datoteke in datoteke:
    print(f"Čitam {naziv_datoteke}...", flush=True)

    with (folder / naziv_datoteke).open(encoding="utf-8-sig", newline="") as ulaz:
        for red in csv.reader(ulaz):
            if not red:
                continue

            ukupno_zapisa += 1
            vremena.add(red[0])
            ucestalosti["CAN ID"][red[1]] += 1
            ucestalosti["DLC"][red[2]] += 1
            ucestalosti["Flag"][red[-1]] += 1

            for i, bajt in enumerate(red[3:-1]):
                ucestalosti[f"DATA[{i}]"][bajt] += 1

print(f"\nUkupno zapisa: {ukupno_zapisa}")
print(f"Timestamp | različitih vrijednosti: {len(vremena)}")

for naziv, brojac in ucestalosti.items():
    broj_prisutnih = sum(brojac.values())
    vrijednost, broj_pojava = brojac.most_common(1)[0]
    udio = 100 * broj_pojava / broj_prisutnih

    print(
        f"{naziv} | različitih: {len(brojac)} | "
        f"najčešća: {vrijednost} | udio među prisutnim: {udio:.2f}%"
    )