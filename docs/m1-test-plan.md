# M1 Test Plan

## Purpose

Determine whether the M1 Coin Beacon can be used as a stable proximity indicator for CyberKey Slim.

## Initial test scenarios

| Test | Duration | Purpose |
|---|---:|---|
| M1 at PC | 5 min | Normal near RSSI |
| M1 in pocket at desk | 5 min | Body attenuation |
| M1 1.5 m away | 5 min | Practical boundary |
| M1 3 m away | 5 min | Away level |
| Body between PC and M1 | 5 min | Signal blocking |
| Normal work situation | 30 min | False dropouts |
| Walk away from PC | 10 repetitions | Time to dropout |
| Return to PC | 10 repetitions | Time to re-detection |

## Notes

The first phase must not lock the PC. It should only log data.
