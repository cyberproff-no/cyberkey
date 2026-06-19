# CyberKey Windows Agent

Dette er første Windows-baserte testområde for CyberKey.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy src\config.example.json src\config.json
```

## Kjør scanner

```bash
python src\cyberkey_scan.py
```

## Kjør analyse

```bash
python src\analyze_rssi.py
```

## Viktig

Første fase samler kun data. Den låser ikke Windows.
