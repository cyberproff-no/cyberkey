# Security Policy

CyberKey is designed according to Privacy and Security by Design principles.

## Scope

CyberKey locks a Windows workstation when a configured BLE beacon is no longer nearby.

CyberKey does not provide, and must not provide in the MVP, functionality for unlocking the machine.

## Trust Model

The BLE radio environment is considered untrusted.

BLE beacon signals, including static identifiers, can be observed and in some cases copied or spoofed by an attacker with radio access.

CyberKey therefore treats BLE proximity exclusively as a weak signal suitable for triggering restrictive actions, such as locking the PC.

CyberKey must never treat BLE proximity as strong identity or authentication.

## Non-goals

CyberKey MVP does not protect against:

- malware on the PC
- a physical attacker with control over the machine
- advanced BLE spoofing
- a compromised Windows user account
- beacon theft
- password theft

## Reporting Security Issues

Do not open public GitHub issues for vulnerabilities.

Report security issues privately to:

kontakt-cyberproff@proton.me
