"""
CyberKey BLE Scanner - Phase 1 Test Tool

Purpose:
- Discovery (Discovery Mode) to find and identify BLE beacons.
- Detailed logging of RSSI, manufacturer data, and service UUIDs for calibration.
- Throttling implemented to prevent log bloat.
"""

import asyncio
import csv
import time
import json
from pathlib import Path
from bleak import BleakScanner

CONFIG_FILE = Path(__file__).parent / "config.json"
EXAMPLE_CONFIG_FILE = Path(__file__).parent / "config.example.json"
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "cyberkey_rssi_log.csv"

LOG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    elif EXAMPLE_CONFIG_FILE.exists():
        with open(EXAMPLE_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "discovery_mode": True,
        "target_name_contains": "M1",
        "target_address": "",
        "test_mode": True,
        "log_interval_seconds": 1
    }

config = load_config()
last_logged = {}

def matches_target(device, advertisement_data) -> bool:
    if config.get("discovery_mode", False):
        return True

    name = device.name or advertisement_data.local_name or ""

    target_addr = config.get("target_address", "").lower()
    if target_addr and device.address.lower() == target_addr:
        return True

    target_name = config.get("target_name_contains", "").lower()
    if target_name and target_name in name.lower():
        return True

    return False

def write_log(row: dict) -> None:
    file_exists = LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp", "address", "name", "rssi",
                "manufacturer_data", "service_uuids", "service_data", "status", "notes"
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def detection_callback(device, advertisement_data):
    if not matches_target(device, advertisement_data):
        return

    now = time.time()
    log_interval = config.get("log_interval_seconds", 1)
    last = last_logged.get(device.address, 0)

    if now - last < log_interval:
        return

    last_logged[device.address] = now

    name = device.name or advertisement_data.local_name or "Unknown"
    rssi = advertisement_data.rssi
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    mf_data = str(advertisement_data.manufacturer_data) if advertisement_data.manufacturer_data else ""
    svc_uuids = str(advertisement_data.service_uuids) if advertisement_data.service_uuids else ""
    svc_data = str(advertisement_data.service_data) if advertisement_data.service_data else ""

    status = "UNCLASSIFIED"

    if config.get("discovery_mode", False):
        print(f"[{timestamp}] [DISCOVERY] {name} ({device.address}) | RSSI: {rssi:3d} dBm | Svc/MFG: {'Yes' if mf_data or svc_data else 'No'}")
    else:
        print(f"[{timestamp}] [TARGET] {name} ({device.address}) | RSSI: {rssi:3d} dBm")

    write_log({
        "timestamp": timestamp,
        "address": device.address,
        "name": name,
        "rssi": rssi,
        "manufacturer_data": mf_data,
        "service_uuids": svc_uuids,
        "service_data": svc_data,
        "status": status,
        "notes": ""
    })

async def main():
    print("==================================================")
    print("CyberKey BLE Scanner (Data Collection) started")
    print("==================================================")

    if config.get("discovery_mode", False):
        print("DISCOVERY MODE IS ACTIVE. Scanning everything nearby.")
    else:
        print(f"Locked to target - Name: '{config.get('target_name_contains')}', MAC: '{config.get('target_address')}'")

    print(f"Logging to: {LOG_FILE.resolve()}")
    print("Press Ctrl+C to exit.\n")

    scanner = BleakScanner(detection_callback)
    await scanner.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping scan...")
    finally:
        await scanner.stop()
        print("Log saved. Ready for next phase: analyze_rssi.py.")

if __name__ == "__main__":
    asyncio.run(main())
