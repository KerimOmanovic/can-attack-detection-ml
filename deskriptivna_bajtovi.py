import csv
from math import ceil, sqrt
from pathlib import Path


projekat = Path(__file__).resolve().parent
folder = projekat / "Car-Hacking Dataset"

datoteke = [
    "DoS_dataset.csv",
    "Fuzzy_dataset.csv",
    "gear_dataset.csv",
    "RPM_dataset.csv",
]


def izracunaj_pokazatelje(frekvencije):
    n = sum(frekvencije)
    prisutne = [v for v, broj in enumerate(frekvencije) if broj > 0]

    sredina = sum(v * frekvencije[v] for v in prisutne) / n

    def centralni_moment(red):
        return sum(
            frekvencije[v] * (v - sredina) ** red
            for v in prisutne
        ) / n

    def vrijednost_na_rangu(rang):
        zbir = 0
        for v in prisutne:
            zbir += frekvencije[v]
            if zbir >= rang:
                return v

    # Isti postupak za kvartile kao u dijelu 5.1.
    q1 = vrijednost_na_rangu(ceil(n * 0.25))
    q3 = vrijednost_na_rangu(ceil(n * 0.75))

    # Kod parnog N medijan je prosjek dvije srednje vrijednosti.
    lijeva = vrijednost_na_rangu((n + 1) // 2)
    desna = vrijednost_na_rangu((n + 2) // 2)
    medijan = (lijeva + desna) / 2

    # Izostavljam po 5 % opažanja sa svakog kraja sortirane raspodjele.
    odbaceno = n // 20
    pocetak = odbaceno
    kraj = n - odbaceno
    pocetak_grupe = 0
    zbir_zadrzanih = 0

    for v in prisutne:
        kraj_grupe = pocetak_grupe + frekvencije[v]
        zadrzano = max(0, min(kraj_grupe, kraj) - max(pocetak_grupe, pocetak))
        zbir_zadrzanih += v * zadrzano
        pocetak_grupe = kraj_grupe

    skracena_sredina = zbir_zadrzanih / (kraj - pocetak)
    sd = sqrt(centralni_moment(2))

    return {
        "N": n,
        "Min": prisutne[0],
        "Q1": q1,
        "Medijan": medijan,
        "Q3": q3,
        "Maks": prisutne[-1],
        "IQR": q3 - q1,
        "Sredina": sredina,
        "Skraćena sredina": skracena_sredina,
        "SD": sd,
        "CV (%)": 100 * sd / sredina if sredina else None,
        "Asimetričnost": centralni_moment(3) / sd ** 3 if sd else None,
        "Eksces": centralni_moment(4) / sd ** 4 - 3 if sd else None,
    }


def formatiraj(vrijednost):
    if vrijednost is None:
        return "N/P"
    if isinstance(vrijednost, int):
        return str(vrijednost)
    return f"{vrijednost:.2f}".replace(".", ",")


# Svaka od osam pozicija ima svoj brojač za vrijednosti od 0 do 255.
frekvencije = [[0] * 256 for _ in range(8)]

for naziv in datoteke:
    print(f"Čitam {naziv}...", flush=True)

    with (folder / naziv).open(encoding="utf-8-sig", newline="") as ulaz:
        for broj_reda, red in enumerate(csv.reader(ulaz), start=1):
            if not red:
                continue

            dlc = int(red[2])
            bajtovi = red[3:-1]

            if not 0 <= dlc <= 8 or len(bajtovi) != dlc:
                raise ValueError(f"{naziv}, red {broj_reda}: provjeri DLC i sadržaj.")

            for pozicija, bajt in enumerate(bajtovi):
                vrijednost = int(bajt, 16)
                frekvencije[pozicija][vrijednost] += 1

# Nezavisna provjera broja prisutnih bajtova prema Tabeli 7.
broj_po_dlc = {2: 147_211, 5: 53_451, 6: 3, 8: 16_368_810}
rezultati = []

for pozicija, brojevi in enumerate(frekvencije):
    ocekivani_n = sum(broj for dlc, broj in broj_po_dlc.items() if dlc > pozicija)
    if sum(brojevi) != ocekivani_n:
        raise ValueError(f"Broj opažanja za DATA[{pozicija}] odstupa od Tabele 7.")

    rezultati.append({
        "Varijabla": f"DATA[{pozicija}]",
        **izracunaj_pokazatelje(brojevi),
    })

zaglavlje = list(rezultati[0])
putanja = projekat / "deskriptivna_bajtovi.csv"

with putanja.open("w", encoding="utf-8-sig", newline="") as izlaz:
    pisac = csv.writer(izlaz, delimiter=";")
    pisac.writerow(zaglavlje)

    print("\nDeskriptivni pokazatelji za prisutne bajtove")
    print("\t".join(zaglavlje))

    for rezultat in rezultati:
        red = [rezultat["Varijabla"]]
        red.extend(formatiraj(rezultat[naziv]) for naziv in zaglavlje[1:])
        pisac.writerow(red)
        print("\t".join(red))

print("\nBroj opažanja na svih osam pozicija odgovara Tabeli 7.")
print(f"Sačuvana tabela: {putanja.name}")