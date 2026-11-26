import csv
from collections import Counter, defaultdict
from pathlib import Path


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]


def format_broja(broj):
    return f"{broj:,}".replace(",", ".")


def udio(broj, ukupno):
    return f"{100 * broj / ukupno:.2f}".replace(".", ",")


# Za svaki CAN ID odvojeno brojim oznake R i T.
oznake_po_id = defaultdict(Counter)

for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            can_id = red[1]
            oznaka = red[-1]

            if oznaka not in ("R", "T"):
                raise ValueError(f"Nepoznata oznaka u {naziv}, red {broj_reda}.")

            oznake_po_id[can_id][oznaka] += 1

# Poredak je isti kao u dijelu 4.2.
poredani_id = sorted(
    oznake_po_id,
    key=lambda can_id: (-oznake_po_id[can_id].total(), can_id),
)

sve_oznake = Counter()
for brojac in oznake_po_id.values():
    sve_oznake.update(brojac)

# Provjera prema rezultatima iz Tabele 9.
if sve_oznake["R"] != 14_237_958 or sve_oznake["T"] != 2_331_517:
    raise ValueError(f"Zbir oznaka se razlikuje od Tabele 9: {sve_oznake}")


def red_tabele(naziv, brojac):
    r = brojac["R"]
    t = brojac["T"]
    ukupno = r + t
    return [naziv, r, t, ukupno, udio(r, ukupno), udio(t, ukupno)]


zaglavlje = ["CAN ID", "Broj R", "Broj T", "Ukupno", "R (%)", "T (%)"]

# Potpuna tabela za sve identifikatore.
putanja = projekat / "kontingencija_can_id_flag.csv"

with putanja.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)
    for can_id in poredani_id:
        pisac.writerow(red_tabele(can_id, oznake_po_id[can_id]))

# Skraćena tabela za Word.
redovi = [
    red_tabele(can_id, oznake_po_id[can_id])
    for can_id in poredani_id[:10]
]

ostali = Counter()
for can_id in poredani_id[10:]:
    ostali.update(oznake_po_id[can_id])

redovi.append(red_tabele("Ostali", ostali))
redovi.append(red_tabele("Ukupno", sve_oznake))

print("\nTabela 11. Redovne i ubačene poruke prema CAN identifikatoru")
print("\t".join(zaglavlje))
for naziv, r, t, ukupno, r_udio, t_udio in redovi:
    print(
        f"{naziv}\t{format_broja(r)}\t{format_broja(t)}\t"
        f"{format_broja(ukupno)}\t{r_udio}\t{t_udio}"
    )

print(f"\nSačuvana potpuna tabela: {putanja.name}")