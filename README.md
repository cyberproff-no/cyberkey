# CyberKey

CyberKey er et lokalt sikkerhetsverktøy under CyberProff som reduserer risikoen for ulåste Windows-PC-er når brukeren forlater arbeidsplassen.

Første MVP heter **CyberKey Slim** og bruker **M1 Coin Beacon** som personlig BLE-nøkkel.

## Status

Tidlig MVP / testfase.

Første versjon fokuserer på:

- M1 Coin Beacon
- Lokal BLE-scanning på Windows
- RSSI-logging
- Kalibrering av nærhet
- Automatisk Windows-lås senere i testløpet
- Ingen sky
- Ingen GPS
- Ingen kamera
- Ingen automatisk opplåsing

## Sikkerhetsprinsipp

CyberKey skal kun låse maskinen.

CyberKey skal ikke brukes til automatisk opplåsing, og erstatter ikke passord, Windows Hello eller annen autentisering.

BLE proximity is a weak signal suitable for triggering lock actions only.

## Komme i gang

```bash
git clone https://github.com/cyberproff-no/cyberkey.git
cd cyberkey
cd agent/windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy src\config.example.json src\config.json
python src\cyberkey_scan.py
```

Analyser RSSI-logg:

```bash
python src\analyze_rssi.py
```

## MVP-mål

Første fase skal samle data, ikke ta sikkerhetsbeslutninger.

Målet er å finne ut:

- hvordan M1 oppfører seg på Windows
- hvilke BLE-identifikatorer som er stabile
- hvordan RSSI varierer ved 0,5 m, 1,5 m og 3 m
- hvor ofte signalet faller ut ved normal bruk
- hvilke terskler som kan brukes senere i proximity engine

## Ikke i MVP

- automatisk opplåsing
- sentral administrasjon
- gateway-støtte
- mobilapp
- webdashboard
- ansattsporing
- H1-knappestøtte
- H3 badge-modus

## Lisens

Programkode er lisensiert under GPL-3.0-or-later.

CyberKey- og CyberProff-navn, logoer og merkevare er ikke lisensiert for kommersiell bruk uten skriftlig tillatelse.
