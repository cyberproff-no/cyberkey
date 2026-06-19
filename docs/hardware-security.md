# Hardware Security Considerations

Første versjon av CyberKey Slim benytter M1 Coin Beacon.

## BLE as a weak signal

M1 støtter åpne annonseringsformater som Apple iBeacon og Google Eddystone. Slike BLE beacon-signaler kan observeres av andre enheter i nærheten og kan i enkelte tilfeller klones eller spoofes.

CyberKey behandler derfor BLE-nærhet som et svakt signal som kun kan brukes til restriktive handlinger, som å låse PC-en.

CyberKey skal ikke bruke BLE-nærhet til automatisk opplåsing eller sterk autentisering.

## Range and signal exposure

M1 har lang nok rekkevidde til at signalet kan fanges opp utenfor brukerens umiddelbare arbeidsområde, særlig ved høy Tx Power og åpne omgivelser.

For testing og senere bruk bør Tx Power reduseres til laveste nivå som fortsatt gir stabil deteksjon ved arbeidsplassen.

Standardprofilen bør først testes som levert, før Tx Power og advertising interval justeres.

## Core rule

BLE proximity is a weak signal suitable for triggering lock actions only.
