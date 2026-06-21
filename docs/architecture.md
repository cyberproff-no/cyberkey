# CyberKey Architecture

CyberKey MVP consists of a simple local Windows agent.

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

## First phase

The first phase implements only BLE discovery, raw logging, and basic RSSI analysis.

No locking logic should be activated until enough test data exists.
