# CyberKey Threat Model

## Goal

CyberKey should reduce the risk of unlocked Windows workstations when the user leaves their workstation.

## Core Rule

BLE proximity is a weak signal suitable for triggering lock actions only.

## Assets

- Windows session lock state
- local CyberKey configuration
- selected BLE beacon identifier
- local test logs

## Trust Boundaries

- the BLE radio environment is untrusted
- beacon identity can be spoofed
- the local Windows user context is trusted in the MVP
- no cloud is required or trusted

## Main Risks

### BLE spoofing

An attacker may attempt to copy or recreate the beacon signal.

Mitigation:

- lock-only design
- no automatic unlocking
- no secrets stored on the beacon
- open documentation of the limitation

### False locking

BLE signals can drop due to interference, body attenuation, or radio conditions.

Mitigation:

- test mode first
- RSSI smoothing later
- timeout-based logic later
- calibration
- cooldown after locking

### Privacy misuse

A proximity system can be misused for employee tracking.

Mitigation:

- no cloud in MVP
- no centralized tracking
- local logs
- clear privacy documentation
