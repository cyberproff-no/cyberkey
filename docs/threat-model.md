# CyberKey Threat Model

## Goal

CyberKey skal redusere risikoen for ulåste Windows-arbeidsstasjoner når brukeren forlater arbeidsplassen.

## Core Rule

BLE proximity is a weak signal suitable for triggering lock actions only.

## Assets

- Windows session lock state
- lokal CyberKey-konfigurasjon
- valgt BLE beacon-identifikator
- lokale testlogger

## Trust Boundaries

- BLE-radiomiljøet er utrygt
- beacon-identitet kan være spoofbar
- lokal Windows-brukerkontekst er betrodd i MVP
- ingen sky er nødvendig eller betrodd

## Main Risks

### BLE spoofing

En angriper kan forsøke å kopiere eller gjenskape beacon-signalet.

Mitigation:

- lock-only design
- ingen automatisk opplåsing
- ingen hemmeligheter lagret på beacon
- åpen dokumentasjon av begrensningen

### False locking

BLE-signal kan falle ut på grunn av interferens, kroppsdemping eller radioforhold.

Mitigation:

- testmodus først
- RSSI-glatting senere
- timeout-basert logikk senere
- kalibrering
- cooldown etter låsing

### Privacy misuse

Et nærhetssystem kan misbrukes til ansattsporing.

Mitigation:

- ingen sky i MVP
- ingen sentral tracking
- lokale logger
- tydelig personverndokumentasjon
