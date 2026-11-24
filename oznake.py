import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


PROJEKAT = Path(__file__).resolve().parent
PODACI = PROJEKAT / "Car-Hacking Dataset"

DATOTEKE = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]


def format_broja(broj):
    return f"{broj:,}".replace(",", ".")


def format_procenta(procenat):
    return f"{procenat:.2f}".replace(".", ",") + " %"


def main():
    broj_poruka = Counter()

    for naziv in DATOTEKE:
        print(f"Čitam {naziv}...", flush=True)

        with (PODACI / naziv).open(encoding="utf-8-sig", newline="") as datoteka:
            for broj_reda, red in enumerate(csv.reader(datoteka), start=1):
                if not red or red[-1] not in ("R", "T"):
                    raise ValueError(
                        f"{naziv}, red {broj_reda}: očekivana je oznaka R ili T."
                    )

                broj_poruka[red[-1]] += 1

    ukupno = sum(broj_poruka.values())
    if ukupno != 16_569_475:
        raise ValueError(
            f"Pročitano je {format_broja(ukupno)} zapisa, "
            "a u prethodnoj analizi bilo ih je 16.569.475."
        )

    oznake = ["R", "T"]
    procenti = [100 * broj_poruka[oznaka] / ukupno for oznaka in oznake]

    print("\nTabela 9. Zastupljenost redovnih i ubačenih CAN poruka")
    print("Oznaka\tBroj poruka\tUdio")
    for oznaka, procenat in zip(oznake, procenti):
        print(f"{oznaka}\t{format_broja(broj_poruka[oznaka])}\t{format_procenta(procenat)}")
    print(f"Ukupno\t{format_broja(ukupno)}\t100,00 %")
    print(f"Broj različitih kategorija: {len(broj_poruka)}")

    fig, ax = plt.subplots(figsize=(6, 4))
    stubovi = ax.bar(
        ["Redovne (R)", "Ubačene (T)"],
        procenti,
        color=["#38658A", "#B46130"],
        width=0.55,
    )

    ax.set_ylabel("Udio poruka (%)")
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 20))
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=0.2)
    ax.bar_label(
        stubovi,
        labels=[format_procenta(p) for p in procenti],
        padding=4,
    )

    fig.tight_layout()
    putanja = PROJEKAT / "grafikon_1_flag.png"
    fig.savefig(putanja, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"\nGrafikon je sačuvan: {putanja.name}")


if __name__ == "__main__":
    main()