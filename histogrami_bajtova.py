import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]

# DATA[3] je četvrti, a DATA[6] sedmi bajt poruke.
pozicije = [3, 6]
frekvencije = {pozicija: [0] * 256 for pozicija in pozicije}

for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for red in csv.reader(ulaz):
            if not red:
                continue

            dlc = int(red[2])
            for pozicija in pozicije:
                if pozicija < dlc:
                    vrijednost = int(red[3 + pozicija], 16)
                    frekvencije[pozicija][vrijednost] += 1

# Provjera prema broju prisutnih bajtova iz Tabele 14.
ocekivani_n = {3: 16_422_264, 6: 16_368_810}

vrijednosti = np.arange(256)
# Granice -0,5 i 7,5 smještaju cijele brojeve 0–7 u prvi interval.
granice = np.arange(-0.5, 256, 8)
x = np.linspace(0, 255, 1000)

fig, ose = plt.subplots(1, 2, figsize=(11, 4.5), sharex=True, sharey=True)

for osa, pozicija in zip(ose, pozicije):
    brojevi = np.array(frekvencije[pozicija])
    n = int(brojevi.sum())

    if n != ocekivani_n[pozicija]:
        raise ValueError(f"Broj opažanja za DATA[{pozicija}] odstupa od Tabele 14.")

    sredina = np.average(vrijednosti, weights=brojevi)
    varijansa = np.average((vrijednosti - sredina) ** 2, weights=brojevi)
    sd = np.sqrt(varijansa)

    osa.hist(
        vrijednosti,
        bins=granice,
        weights=brojevi,
        density=True,
        color="#38658A",
        edgecolor="white",
        linewidth=0.6,
        label="Prisutni bajtovi",
    )

    normalna_kriva = np.exp(-0.5 * ((x - sredina) / sd) ** 2)
    normalna_kriva /= sd * np.sqrt(2 * np.pi)
    osa.plot(x, normalna_kriva, color="#B44D20", linewidth=2,
             label="Normalna kriva")

    osa.set_title(f"DATA[{pozicija}]")
    osa.set_xlabel("Vrijednost bajta")
    osa.set_xlim(-0.5, 255.5)
    osa.set_xticks([0, 32, 64, 96, 128, 160, 192, 224, 255])
    osa.set_axisbelow(True)
    osa.grid(axis="y", alpha=0.2)

    # Isti intervali koje prikazuje histogram.
    po_intervalima = brojevi.reshape(32, 8).sum(axis=1)
    najcesci = int(po_intervalima.argmax())
    donja = najcesci * 8

    print(f"\nDATA[{pozicija}]")
    print(f"Broj prisutnih vrijednosti: {n:,}".replace(",", "."))
    print(f"Udio vrijednosti 0: {100 * brojevi[0] / n:.2f} %")
    print(f"Udio u intervalu 0–7: {100 * po_intervalima[0] / n:.2f} %")
    print(f"Udio u intervalu 248–255: {100 * po_intervalima[-1] / n:.2f} %")
    print(f"Najčešći interval: {donja}–{donja + 7}")

ose[0].set_ylabel("Gustina")
ose[1].legend()
fig.tight_layout()

putanja = projekat / "grafikon_4_histogrami_bajtova.png"
fig.savefig(putanja, dpi=300, bbox_inches="tight")
print(f"\nSačuvan grafikon: {putanja.name}")
plt.show()