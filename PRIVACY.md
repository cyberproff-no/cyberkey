# Privacy Policy

CyberKey er bygget etter prinsippet Privacy by Design.

## Local-first

CyberKey MVP fungerer lokalt på brukerens Windows-maskin.

## Ingen skytjenester

CyberKey MVP sender ikke telemetri, posisjonsdata eller BLE-data til eksterne servere.

## Ingen sporing

CyberKey er et verktøy for å låse den lokale maskinen. Det er ikke et verktøy for å overvåke ansattes tilstedeværelse, lokasjon eller arbeidstid.

## Minimal logging

Logger brukes kun for lokal testing og kalibrering av maskinvare og signalstyrke.

Loggene kan inneholde timestamp, BLE-adresse, device name, RSSI, manufacturer data, service UUIDs og service data.

Logger lagres lokalt i `agent/windows/logs/` og skal ikke sjekkes inn i Git.
