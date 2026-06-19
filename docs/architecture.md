# CyberKey Architecture

CyberKey MVP består av en enkel lokal Windows-agent.

```text
M1 Coin Beacon
    ↓
BLE scanner
    ↓
RSSI logging
    ↓
Analysis
    ↓
Proximity engine later
    ↓
Windows lock later
```

## Første fase

Første fase implementerer kun BLE discovery, rå logging og enkel RSSI-analyse.

Ingen låselogikk skal aktiveres før det finnes nok testdata.
