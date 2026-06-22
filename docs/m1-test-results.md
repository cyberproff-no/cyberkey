# M1 Hardware Validation Results
Use this document after physical M1 Coin Beacon testing begins.

Record summary values and redacted identifier descriptions only.

Do not commit raw RSSI logs, full Bluetooth addresses, full manufacturer data, or personal movement information.

## Test Environment

- Test date:
- Tester:
- PC model:
- Windows version:
- Bluetooth adapter model:
- Bluetooth driver version:
- Room type:
- Nearby obstructions or interference:
- M1 firmware or configuration version:
- Advertising format:
- Advertising interval:
- Tx Power:
- Scanner version or commit:

## Discovery and Advertisement Inventory

### Candidate Beacon Summary

- Displayed local name:
- Address behavior: stable / rotating / unknown
- Address suffix, redacted:
- Manufacturer-data presence: yes / no
- Manufacturer-data summary, redacted:
- Service UUIDs present: yes / no
- Service UUID summary, redacted:
- Service-data presence: yes / no
- Repeatedly visible across scans: yes / no
- Notes:

### Candidate Local Filter Rule

```
Rule description:
```
Example redacted values:

```
manufacturer_data_prefix=0x1234****
service_uuid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
address_suffix=**:**
```

### Identifier Acceptance Review

| Criterion | Result | Notes |
|---|---|---|
| Observed across repeated scans |  |  |
| Specific enough to avoid broad matching |  |  |
| Stable after restart or power cycle |  |  |
| Compatible with local-only processing |  |  |
| Does not rely on name alone |  |  |

## RSSI and Packet-Loss Results

| Scenario | Duration | Repetitions | RSSI min | RSSI max | RSSI avg | Approx. packets | Longest gap | Gaps >1s | Gaps >3s | Gaps >5s | Notes |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---|
| Beacon beside PC |  |  |  |  |  |  |  |  |  |  |  |
| Beacon in pocket at desk |  |  |  |  |  |  |  |  |  |  |  |
| Beacon at 1.5 m |  |  |  |  |  |  |  |  |  |  |  |
| Beacon at 3 m |  |  |  |  |  |  |  |  |  |  |  |
| Body between PC and beacon |  |  |  |  |  |  |  |  |  |  |  |
| Beacon behind desk or monitor |  |  |  |  |  |  |  |  |  |  |  |
| Normal seated work |  |  |  |  |  |  |  |  |  |  |  |
| Walk away from PC |  |  |  |  |  |  |  |  |  |  |  |
| Return to PC |  |  |  |  |  |  |  |  |  |  |  |

## Packet-Loss and Reappearance Review

- Typical near-field advertisement gap:
- Worst near-field advertisement gap:
- Near-field gaps that could resemble `LOST`:
- Conditions associated with packet loss:
- Typical return-to-detection time:
- Worst return-to-detection time:
- False dropout observations:
- Notes:

## Preliminary Calibration Proposal
Do not use these values in runtime configuration until reviewed.

| Setting | Proposed value | Evidence source | Rationale |
|---|---|---|---|
| `rssi_near` |  |  |  |
| `rssi_away` |  |  |  |
| `window_size` |  |  |  |
| `min_samples` |  |  |  |
| `lost_after_seconds` |  |  |  |
| `lock_after_away_seconds` |  |  |  |
| `lock_after_lost_seconds` |  |  |  |

## Environmental Limitations

- Known sources of RSSI variation:
- Body attenuation observations:
- Obstruction observations:
- Bluetooth interference observations:
- Conditions not yet tested:
- Remaining risks:

## Evidence Review Gate

| Requirement | Result | Notes |
|---|---|---|
| Beacon is consistently discoverable |  |  |
| Candidate local filter rule is documented |  |  |
| Near-field behavior measured during normal work |  |  |
| Packet-loss behavior measured and reviewed |  |  |
| Departure behavior measured repeatedly |  |  |
| Return behavior measured repeatedly |  |  |
| Calibration proposal supported by local data |  |  |
| Future path remains `test_mode=True` |  |  |
| Future output remains `WOULD_LOCK` only |  |  |
| No use of BLE for authentication or unlocking |  |  |

## Decision

- Hardware validation status: not started / incomplete / ready for adapter design discussion
- Approved for live adapter design discussion: yes / no
- Approved for Windows locking: no
- Reviewer: Unassigned
- Review date:
- Notes: No M1 hardware validation has been performed. No live adapter or Windows locking approval is granted.
