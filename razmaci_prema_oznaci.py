import csv
from collections import Counter
from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = {
    "DoS": "DoS_dataset.csv",
    "Fuzzy": "Fuzzy_dataset.csv",
    "Gear": "gear_dataset.csv",
    "RPM": "RPM_dataset.csv",
}

# Broj razmaka po snimku iz Tabele 16.
ocekivani_broj = {
    "DoS": 3_665_770,
    "Fuzzy": 3_838_859,
    "Gear": 4_443_141,
    "RPM": 4_621_701,
}


def izracunaj_pokazatelje(frekvencije):
    """Iz frekvencija razmaka u mikrosekundama računam pokazatelje u ms."""
    poredani = sorted(frekvencije.items())
    n = sum(frekvencije.values())

    def vrijednost_na_rangu(rang):
        zbir = 0
        for razmak_us, broj in poredani:
            zbir += broj
            if zbir >= rang:
                return razmak_us

    q1 = vrijednost_na_rangu((n + 3) // 4)
    q3 = vrijednost_na_rangu((3 * n + 3) // 4)
    medijan = (
                      vrijednost_na_rangu((n + 1) // 2)
                      + vrijednost_na_rangu((n + 2) // 2)
              ) / 2

    iqr = q3 - q1
    donja = q1 - 1.5 * iqr
    gornja = q3 + 1.5 * iqr

    prvi_brk = next(v for v, _ in poredani if v >= donja)
    zadnji_brk = next(v for v, _ in reversed(poredani) if v <= gornja)

    return n, {
        "q1": q1 / 1000,
        "med": medijan / 1000,
        "q3": q3 / 1000,
        "whislo": prvi_brk / 1000,
        "whishi": zadnji_brk / 1000,
    }


def format_ms(vrijednost):
    return f"{vrijednost:.4f}".replace(".", ",")


redovi = []
dijagrami = []
pozicije = []
boje = {"R": "#38658A", "T": "#B46130"}

for indeks, (snimak, naziv) in enumerate(datoteke.items()):
    print(f"Čitam {naziv}...", flush=True)
    po_oznaci = {"R": Counter(), "T": Counter()}
    prethodno_us = None

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            oznaka = red[-1]
            if oznaka not in po_oznaci:
                raise ValueError(f"{naziv}, red {broj_reda}: nepoznata oznaka.")

            vrijeme = Decimal(red[0]) * 1_000_000
            vrijeme_us = int(vrijeme)
            if vrijeme_us != vrijeme:
                raise ValueError(f"{naziv}, red {broj_reda}: preciznost ispod 1 µs.")

            if prethodno_us is not None:
                razmak_us = vrijeme_us - prethodno_us
                if razmak_us < 0:
                    raise ValueError(f"{naziv}, red {broj_reda}: vrijeme ide unazad.")

                # Razmak pripada poruci koja je upravo stigla.
                po_oznaci[oznaka][razmak_us] += 1

            prethodno_us = vrijeme_us

    broj_u_snimku = sum(brojac.total() for brojac in po_oznaci.values())
    if broj_u_snimku != ocekivani_broj[snimak]:
        raise ValueError(f"Broj razmaka za {snimak} odstupa od Tabele 16.")

    for oznaka, pomak in [("R", -0.19), ("T", 0.19)]:
        n, statistika = izracunaj_pokazatelje(po_oznaci[oznaka])
        iqr = statistika["q3"] - statistika["q1"]

        redovi.append([
            snimak, oznaka, n,
            format_ms(statistika["q1"]),
            format_ms(statistika["med"]),
            format_ms(statistika["q3"]),
            format_ms(iqr),
        ])
        dijagrami.append(statistika)
        pozicije.append(indeks + pomak)

zaglavlje = ["Snimak", "Oznaka", "N", "Q1 (ms)", "Medijan (ms)", "Q3 (ms)", "IQR (ms)"]
putanja_tabele = projekat / "razmaci_prema_oznaci.csv"

with putanja_tabele.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)
    pisac.writerows(redovi)

print("\nTabela 22. Vremenski razmak prije redovnih i ubačenih poruka po snimku")
print("\t".join(zaglavlje))
for red in redovi:
    print("\t".join(str(vrijednost) for vrijednost in red))

fig, ax = plt.subplots(figsize=(9, 5))
prikaz = ax.bxp(
    dijagrami,
    positions=pozicije,
    widths=0.32,
    patch_artist=True,
    showfliers=False,
    manage_ticks=False,
    medianprops={"color": "black", "linewidth": 1.8},
)

for kutija, red in zip(prikaz["boxes"], redovi):
    kutija.set_facecolor(boje[red[1]])
    kutija.set_alpha(0.75)

ax.set_xticks(range(len(datoteke)), list(datoteke))
ax.set_ylabel("Razmak od prethodne poruke (ms)")
ax.set_ylim(bottom=0)
ax.set_axisbelow(True)
ax.grid(axis="y", alpha=0.2)
ax.legend(handles=[
    Patch(facecolor=boje["R"], label="Redovna (R)"),
    Patch(facecolor=boje["T"], label="Ubačena (T)"),
])

fig.tight_layout()
putanja_grafa = projekat / "grafikon_9_razmaci_prema_oznaci.png"
fig.savefig(putanja_grafa, dpi=300, bbox_inches="tight")

print(f"\nSačuvana tabela: {putanja_tabele.name}")
print(f"Sačuvan grafikon: {putanja_grafa.name}")
plt.show()