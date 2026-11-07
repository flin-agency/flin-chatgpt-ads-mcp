# Sicherheit

Der Server bietet ausschliesslich fest hinterlegte GET-Endpunkte auf
`https://api.ads.openai.com/v1`: keine Schreiboperationen, freien URLs oder Redirects.
Er prüft Eingaben, begrenzt Antwortgrössen und Laufzeiten und maskiert konfigurierte
Keys in Ergebnissen. Fehler geben keine API-Rohantworten aus. Werbeinhalte sind
unvertrauenswürdige Daten; die Hinweise des Servers garantieren keinen Schutz gegen
Prompt Injection im KI-Client.

`connection_status` liefert nur den lokalen Einrichtungszustand und die laufende
Version. Kein Browserstart, kein Live-Test und keine Kosten durch API-Abfragen.
Ungültige Konfigurationen starten mit leeren Konten für die Diagnose; API-Zugriffe
bleiben gesperrt. Eine gewählte JSON-Datei hat Vorrang vor allen UI-Keys.

Der Starter aktualisiert bei Neustart aus PyPI innerhalb `>=0.1.6,<0.2`, ohne
Vorabversionen. Damit werden zukünftige stabile 0.1-Releases und deren Abhängigkeiten
als Code vertraut. Die ausführliche [historische Prüfung von 0.1.5](docs/security-review-0.1.5.md)
garantiert nicht die Sicherheit künftiger Releases. Getestet wird die Schnittstelle
`--desktop`, zehn Kontofelder, Konfigurationspriorität, Tools und Update-Grenze.
Laufende Sitzungen werden nicht ausgetauscht; bestehende Einstellungen bleiben erhalten.

API-Keys nie im Chat, in Issues oder Diagnose-Screenshots teilen. Die UI markiert
Keys als sensibel; deren Speicherung ist Sache des Hosts, keine Zusicherung dieses
Projekts. JSON-Dateien enthalten Klartext. [Datenflüsse und Widerruf](PRIVACY.md).

Pakete sind unsigniert und nicht Apple-notarisiert. SHA256SUMS prüft Integrität,
ist aber keine unabhängige Signatur. Releases verwenden Tests, Manifestprüfung,
Paketstart ausserhalb des Quellverzeichnisses und eine PyPI-Prüfung vor macOS-Upload.
Apple-Silicon-, Linux- und echte Kundentests sind getrennte Nachweise. Es wurden
keine echten Kundenkeys für die Standardisierung verwendet.

Bei einem offengelegten Key zuerst Widerruf beim Provider veranlassen. Für sensible
Sicherheitsmeldungen den zuständigen Administrator kontaktieren und einen privaten
Kontaktweg zum Maintainer vereinbaren. Öffentliche [Issues](https://github.com/flin-agency/flin-chatgpt-ads-mcp/issues)
nur ohne Secrets oder Kundendaten; siehe [SUPPORT.md](SUPPORT.md).
