# Hardware Security Considerations

The first version of CyberKey Slim uses the M1 Coin Beacon.

## BLE as a weak signal

M1 supports open advertising formats such as Apple iBeacon and Google Eddystone. Such BLE beacon signals can be observed by other nearby devices and can in some cases be cloned or spoofed.

CyberKey therefore treats BLE proximity as a weak signal that can only be used for restrictive actions, such as locking the PC.

CyberKey must not use BLE proximity for automatic unlocking or strong authentication.

## Range and signal exposure

M1 has enough range that its signal can be captured outside the user's immediate work area, especially with high Tx Power and in open environments.

For testing and later use, Tx Power should be reduced to the lowest level that still provides stable detection at the workstation.

The default profile should first be tested as delivered before adjusting Tx Power and advertising interval.

## Core rule

BLE proximity is a weak signal suitable for triggering lock actions only.
