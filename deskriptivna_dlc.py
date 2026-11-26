from math import ceil, sqrt

# Broj poruka za svaku dužinu iz Tabele 7.
broj_po_dlc = {
    2: 147_211,
    5: 53_451,
    6: 3,
    8: 16_368_810,
}

duzine = sorted(broj_po_dlc)
n = sum(broj_po_dlc.values())
sredina = sum(dlc * broj_po_dlc[dlc] for dlc in duzine) / n


def centralni_moment(red):
    return sum(
        broj_po_dlc[dlc] * (dlc - sredina) ** red
        for dlc in duzine
    ) / n


def kvartil(udio):
    # Tražim prvu dužinu na kojoj zbir frekvencija dostigne traženi rang.
    rang = ceil(udio * n)
    do_sada = 0
    for dlc in duzine:
        do_sada += broj_po_dlc[dlc]
        if do_sada >= rang:
            return dlc


# Skraćena sredina računa se na srednjih 90 % sortiranih opažanja.
odbaceno_po_kraju = n // 20
pocetak = odbaceno_po_kraju
kraj = n - odbaceno_po_kraju
pocetak_grupe = 0
zbir_zadrzanih = 0

for dlc in duzine:
    kraj_grupe = pocetak_grupe + broj_po_dlc[dlc]
    broj_zadrzanih = max(0, min(kraj_grupe, kraj) - max(pocetak_grupe, pocetak))
    zbir_zadrzanih += dlc * broj_zadrzanih
    pocetak_grupe = kraj_grupe

skracena_sredina = zbir_zadrzanih / (kraj - pocetak)
standardna_devijacija = sqrt(centralni_moment(2))
koeficijent_varijacije = 100 * standardna_devijacija / sredina
asimetricnost = centralni_moment(3) / standardna_devijacija ** 3
eksces = centralni_moment(4) / standardna_devijacija ** 4 - 3

q1 = kvartil(0.25)
medijan = kvartil(0.50)
q3 = kvartil(0.75)

print("Tabela 13. Deskriptivni pokazatelji za DLC")
print("Broj valjanih opažanja:", f"{n:,}".replace(",", "."))
print("Minimum:", duzine[0])
print("Q1:", q1)
print("Medijan:", medijan)
print("Q3:", q3)
print("Maksimum:", duzine[-1])
print("IQR:", q3 - q1)
print(f"Aritmetička sredina: {sredina:.3f}")
print(f"Skraćena sredina (5 % sa svakog kraja): {skracena_sredina:.3f}")
print(f"Standardna devijacija: {standardna_devijacija:.3f}")
print(f"Koeficijent varijacije: {koeficijent_varijacije:.2f} %")
print(f"Asimetričnost: {asimetricnost:.2f}")
print(f"Zaobljenost (eksces): {eksces:.2f}")