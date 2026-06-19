# Security Policy

CyberKey er designet med Privacy and Security by Design.

## Scope

CyberKey låser en Windows-arbeidsstasjon når en konfigurert BLE-beacon ikke lenger er i nærheten.

CyberKey tilbyr ikke, og skal ikke tilby i MVP, funksjonalitet for å låse opp maskinen.

## Trust Model

BLE-radiomiljøet anses som utrygt.

BLE beacon-signaler, inkludert statiske identifikatorer, kan observeres og i enkelte tilfeller kopieres eller spoofes av en angriper med radiotilgang.

CyberKey behandler derfor BLE-nærhet utelukkende som et svakt signal egnet til å trigge restriktive handlinger, som å låse PC-en.

CyberKey skal aldri behandle BLE-nærhet som sterk identitet eller autentisering.

## Non-goals

CyberKey MVP beskytter ikke mot:

- malware på PC-en
- fysisk angriper med kontroll over maskinen
- avansert BLE-spoofing
- kompromittert Windows-bruker
- tyveri av beacon
- passordtyveri

## Reporting Security Issues

Ikke åpne offentlige GitHub issues for sårbarheter.

Rapporter sikkerhetsproblemer privat til:

kontakt-cyberproff@proton.me
