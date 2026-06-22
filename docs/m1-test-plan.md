# M1 Hardware Validation Plan

## Purpose
Validate whether the M1 Coin Beacon can provide a sufficiently stable local BLE proximity signal for CyberKey Slim.

This phase is for data collection and analysis only.

It must not:

- Trigger Windows locking.
- Import or call `locker.py`.
- Connect the BLE scanner to `DryRunAgent`.
- Use BLE for unlocking, authentication, identity verification, or access control.
- Send telemetry or data to cloud services.

BLE remains a weak signal that may only contribute to a future restrictive lock decision.

## Scope
This plan validates:

- Whether the M1 is visible to the local Bluetooth adapter.
- Which advertisement fields are exposed by the beacon.
- Whether a practical local identifier can be observed consistently.
- RSSI stability at realistic workstation distances.
- Packet-loss and disappearance behavior.
- Effects of body attenuation, orientation, obstacles, and normal movement.
- Whether collected evidence is sufficient to propose later calibration values.

This plan does not define production thresholds. Thresholds must be derived from collected local measurements.

## Required Tools
Use the existing local scanner only:

```
agent/windows/src/cyberkey_scan.py
```
The scanner may collect local observations such as:

- Timestamp
- Bluetooth address
- Local name
- RSSI
- Manufacturer data
- Service UUIDs
- Service data

Use the existing local analysis tool after each scenario:

```
agent/windows/src/analyze_rssi.py
```
Store generated logs locally under:

```
agent/windows/logs/
```
Do not commit raw RSSI logs, captured identifiers, or environment-specific measurements to the repository.

## Preconditions
Before testing:

1. Confirm the working tree is clean.
2. Confirm `config.json` remains local and is not committed.
3. Confirm scanner configuration uses:
```
{
	"discovery_mode": true,
	"test_mode": true
}
```
4. Confirm no runtime component imports `locker.py`.
5. Confirm no process is configured to call `LockWorkStation()`.
6. Record the test environment in `docs/m1-test-results.md`.

Record at minimum:

- PC model
- Windows version
- Bluetooth adapter model
- Bluetooth driver version
- M1 firmware or configuration version, if available
- Advertising format, if known
- Advertising interval, if known
- Tx Power, if known
- Room type and major nearby obstructions

## Phase 1: Discovery and Advertisement Inventory
Run the scanner in discovery mode before attempting any target filtering.

For each visible candidate that may be the M1, record:

- Displayed name
- Reported Bluetooth address
- Manufacturer data structure
- Service UUIDs
- Service data
- RSSI range during a short stationary observation
- Whether the same fields remain stable across repeated scans

Perform at least three short discovery runs with the beacon:

1. At the workstation.
2. Outside the immediate workstation area.
3. After power-cycling or restarting the beacon, when possible.

### Discovery Questions
Answer these questions before moving on:

- Does the M1 advertise consistently?
- Is a local name present and stable?
- Does the reported address remain stable or rotate?
- Is manufacturer data present?
- Are service UUIDs or service data present?
- Is there a reproducible combination of fields that distinguishes the intended beacon from nearby devices?
- Could the selected filter accidentally match unrelated nearby devices?

Do not treat a display name alone as a trusted identifier.

## Phase 2: Candidate Identifier Stability
Select one or more candidate fields for later local filtering.

Examples may include:

- A stable local name combined with other advertisement metadata.
- A manufacturer-data prefix and length.
- A specific service UUID combined with expected service data.
- A stable address only when repeated testing confirms that it does not rotate.

Document the candidate rule in `docs/m1-test-results.md` without publishing sensitive raw identifiers.

Use a redacted form where necessary, for example:

```
manufacturer_data_prefix=0x1234****
service_uuid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
address_suffix=**:**
```

### Acceptance Condition
A candidate identifier is suitable for later adapter design only when it is:

- Observed repeatedly across multiple scans.
- Specific enough to avoid broad matching.
- Explainable and testable.
- Compatible with local-only processing.

A candidate identifier does not create trust or authentication. It only narrows which RSSI samples may be considered by a future local adapter.

## Phase 3: Baseline RSSI and Packet-Loss Collection
Use the existing scanner in discovery mode or a manually reviewed target mode.

Run each scenario long enough to collect meaningful observations. Keep beacon placement and PC position consistent during each run.

| Scenario | Minimum duration | Repetitions | Purpose |
|---|---:|---:|---|
| Beacon beside PC | 5 minutes | 2 | Establish near baseline |
| Beacon in pocket at desk | 5 minutes | 2 | Measure body attenuation |
| Beacon at 1.5 m | 5 minutes | 2 | Measure practical desk boundary |
| Beacon at 3 m | 5 minutes | 2 | Measure likely away region |
| Body between PC and beacon | 5 minutes | 2 | Measure signal blocking |
| Beacon behind desk or monitor | 5 minutes | 2 | Measure common obstruction effects |
| Normal seated work | 30 minutes | 1 | Observe false dropouts |
| Walk away from PC | 10 repetitions | 1 | Observe RSSI decline and disappearance timing |
| Return to PC | 10 repetitions | 1 | Observe re-detection and RSSI recovery |

For every run, record:

- Start and end time
- Beacon placement
- Orientation, when relevant
- RSSI minimum, maximum, and average
- Approximate packet count
- Longest observed gap between advertisements
- Number of gaps longer than 1 second
- Number of gaps longer than 3 seconds
- Number of gaps longer than 5 seconds
- Unexpected state-affecting observations
- Notes about movement, interference, or physical barriers

## Phase 4: Packet-Loss and Reappearance Behavior
Packet loss is especially important because `ProximityEngine` treats extended absence as a potential `LOST` condition.

For the normal seated-work scenario, determine:

- Whether brief gaps occur while the beacon remains nearby.
- The typical and worst observed gap duration.
- Whether gaps cluster around movement, body position, or other devices.
- Whether a nearby beacon can disappear long enough to resemble a future lost timeout.
- How quickly the beacon is observed again after returning to the workstation.

Do not set `lost_after_seconds` from a single observation.

A later calibration proposal should include margin above normal near-field packet-loss behavior.

## Phase 5: Preliminary Calibration Proposal
Only after data collection, propose local values for review:

- `rssi_near`
- `rssi_away`
- `window_size`
- `min_samples`
- `lost_after_seconds`
- `lock_after_away_seconds`
- `lock_after_lost_seconds`

The proposal must explain:

- Which scenarios informed each value.
- Why NEAR and AWAY thresholds have a sufficient separation margin.
- Why normal packet loss should not cause a false LOST state.
- Why a temporary weak signal should not immediately produce a departure decision.
- Which environmental limitations remain unresolved.

Do not modify `proximity.py` or production configuration during this documentation phase.

## Phase 6: Evidence Review Gate
The M1 is ready for a future live-adapter design discussion only when all of the following are true:

- The beacon is consistently discoverable in the intended workstation environment.
- A practical local filtering rule has been documented.
- Near-field behavior has been measured over normal work periods.
- Packet-loss behavior has been measured and reviewed.
- Return and departure behavior has been measured repeatedly.
- Candidate calibration values are justified by local data.
- No evidence suggests that BLE alone would be used for authentication or unlocking.
- The planned next integration remains `test_mode=True`.
- The planned next output remains `WOULD_LOCK` only.

Passing this gate does not authorize Windows locking.

## Result Recording
Record results in:

```
docs/m1-test-results.md
```
Use summary values and redacted identifier descriptions only.

Do not store:

- Raw address values in repository documentation.
- Raw manufacturer data that could identify a personal device.
- Full local RSSI log files.
- Personal location, movement history, or employee-monitoring data.

## Future Direction After Hardware Validation
A future live adapter may be considered only after this plan is completed and reviewed.

The intended direction remains:

```
validated local M1 advertisement
		-> accepted RSSI sample
		-> DryRunAgent.process_rssi(...)
		-> WOULD_LOCK logging only
```
The adapter must not modify `ProximityEngine` or `PolicyEngine` state directly.

Windows locking remains out of scope until a separate, explicit safety review.
