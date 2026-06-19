"""
CyberKey RSSI Analyzer

Hensikt:
- Lese loggfilen generert av cyberkey_scan.py
- Vise statistikk per oppdaget enhet for å hjelpe med kalibrering.
"""

import csv
from collections import defaultdict
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "logs" / "cyberkey_rssi_log.csv"

def analyze():
    if not LOG_FILE.exists():
        print(f"Fant ingen loggfil på: {LOG_FILE.resolve()}")
        print("Kjør cyberkey_scan.py først for å samle data.")
        return

    data = defaultdict(list)
    last_seen = {}

    with open(LOG_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mac = row.get("address", "Unknown MAC")
            name = row.get("name", "Unknown Name")
            try:
                rssi = int(row.get("rssi", 0))
            except ValueError:
                continue

            timestamp = row.get("timestamp", "Unknown Time")

            key = f"{name} ({mac})"
            data[key].append(rssi)
            last_seen[key] = timestamp

    print("==================================================")
    print("CyberKey RSSI Analyse")
    print("==================================================")

    if not data:
        print("Ingen gyldige data funnet i loggfilen.")
        return

    for key, rssi_list in data.items():
        count = len(rssi_list)
        avg = sum(rssi_list) / count
        minimum = min(rssi_list)
        maximum = max(rssi_list)

        print(f"Enhet: {key}")
        print(f"  Antall målinger   : {count}")
        print(f"  RSSI Minimum      : {minimum} dBm")
        print(f"  RSSI Maksimum     : {maximum} dBm")
        print(f"  RSSI Gjennomsnitt : {avg:.1f} dBm")
        print(f"  Sist observert    : {last_seen[key]}")
        print("-" * 50)

if __name__ == "__main__":
    analyze()
