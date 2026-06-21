# CyberKey Windows Agent

This is the first Windows-based test area for CyberKey.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy src\config.example.json src\config.json
```

## Run scanner

```bash
python src\cyberkey_scan.py
```

## Run analysis

```bash
python src\analyze_rssi.py
```

## Important

The first phase only collects data. It does not lock Windows.
