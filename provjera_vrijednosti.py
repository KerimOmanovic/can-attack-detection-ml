import csv
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

folder = Path(__file__).parent / "Car-Hacking Dataset"
datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]

format_vremena = re.compile(r"[0-9]+(?:\.[0-9]+)?")
format_id = re.compile(r"[0-9a-fA-F]+")
format_bajta = re.compile(r"[0-9a-fA-F]{2}")

for naziv in datoteke:
    print(f"\nProvjeravam {naziv}...", flush=True)

    broj_zapisa = 0
    neispravno_vrijeme = 0
    vrijeme_unazad = 0
    neispravan_id = 0
    broj_bajtova = 0
    neispravni_bajtovi = 0
    neocekivana_oznaka = 0

    prethodno_vrijeme = None
    najmanje_vrijeme = None
    najvece_vrijeme = None
    duzine_id = Counter()
    primjeri = {}

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            broj_zapisa += 1
            vrijeme, can_id = red[0], red[1]
            oznaka = red[-1]

            if format_vremena.fullmatch(vrijeme):
                trenutno = Decimal(vrijeme)

                if prethodno_vrijeme is not None and trenutno < prethodno_vrijeme:
                    vrijeme_unazad += 1
                    primjeri.setdefault(
                        "Vrijeme ide unazad",
                        (broj_reda, f"{prethodno_vrijeme} -> {trenutno}"),
                    )

                prethodno_vrijeme = trenutno

                if najmanje_vrijeme is None or trenutno < najmanje_vrijeme:
                    najmanje_vrijeme = trenutno
                if najvece_vrijeme is None or trenutno > najvece_vrijeme:
                    najvece_vrijeme = trenutno
            else:
                neispravno_vrijeme += 1
                primjeri.setdefault("Format vremena", (broj_reda, vrijeme))
                prethodno_vrijeme = None

            if format_id.fullmatch(can_id):
                duzine_id[len(can_id)] += 1
            else:
                neispravan_id += 1
                primjeri.setdefault("Format CAN ID-a", (broj_reda, can_id))

            for pozicija, bajt in enumerate(red[3:-1]):
                broj_bajtova += 1
                if not format_bajta.fullmatch(bajt):
                    neispravni_bajtovi += 1
                    primjeri.setdefault(
                        "Format bajta",
                        (broj_reda, f"DATA[{pozicija}] = {bajt!r}"),
                    )

            if oznaka not in {"R", "T"}:
                neocekivana_oznaka += 1
                primjeri.setdefault("Oznaka poruke", (broj_reda, oznaka))

    print(f"Pregledano zapisa: {broj_zapisa}")
    print(f"Neispravan format vremena: {neispravno_vrijeme}")
    print(f"Vrijeme ide unazad: {vrijeme_unazad}")
    if najmanje_vrijeme is not None:
        print(f"Vremenski raspon snimka (s): {najvece_vrijeme - najmanje_vrijeme}")

    print(f"CAN ID s neheksadecimalnim zapisom: {neispravan_id}")
    print(f"Dužina CAN ID-a (broj znakova: broj zapisa): {dict(duzine_id)}")
    print(f"Pregledano prisutnih bajtova: {broj_bajtova}")
    print(f"Bajtova s neispravnim zapisom: {neispravni_bajtovi}")
    print(f"Oznaka izvan R/T: {neocekivana_oznaka}")

    for provjera, (broj_reda, vrijednost) in primjeri.items():
        print(f"Prvi primjer – {provjera}, red {broj_reda}: {vrijednost}")