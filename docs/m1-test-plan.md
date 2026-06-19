# M1 Test Plan

## Formål

Finne ut om M1 Coin Beacon kan brukes som stabil nærhetsindikator for CyberKey Slim.

## Første testscenarioer

| Test | Varighet | Formål |
|---|---:|---|
| M1 ved PC | 5 min | Normal near-RSSI |
| M1 i lomme ved pult | 5 min | Kroppsdemping |
| M1 1,5 m unna | 5 min | Praktisk grense |
| M1 3 m unna | 5 min | Away-nivå |
| Kropp mellom PC og M1 | 5 min | Signalblokkering |
| Normal arbeidssituasjon | 30 min | Falske bortfall |
| Gå bort fra PC | 10 repetisjoner | Tid til bortfall |
| Komme tilbake | 10 repetisjoner | Tid til re-detection |

## Notater

Første fase skal ikke låse PC-en. Den skal kun logge data.
