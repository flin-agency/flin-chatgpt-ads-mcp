# Sicherheitsprüfung 0.1.5

Geprüft am 6. November 2026: Servercode, Kontokonfiguration, Claude-Desktop-Starter,
Paketinhalt, Installationsskripte, GitHub-Workflows und Laufzeitabhängigkeiten des geprüften Entwicklungsstands.
Dies ist eine Quellcode- und automatisierte Prüfung, kein unabhängiger Penetrationstest
und keine Garantie für die Abwesenheit aller Schwachstellen.

## Schutzmassnahmen

- Ausschliesslich fest hinterlegte GET-Endpunkte auf `https://api.ads.openai.com/v1`;
  keine frei wählbaren URLs, Schreiboperationen oder Weiterleitungen.
- HTTP-Client mit TLS-Prüfung, ohne Übernahme von Proxy-Einstellungen aus der Umgebung.
  Antwortlimit 10 MiB, höchstens drei Versuche, begrenzte Wartezeiten und eine
  Gesamtdauer von höchstens 100 Sekunden pro Aufruf.
- Konten wählen getrennte API-Keys. Bei mehreren Konten ohne Standard ist eine
  ausdrückliche Auswahl erforderlich. Eine ausgewählte Datei hat Vorrang;
  fehlerhafte Dateien führen nicht zum Wechsel auf ein anderes Konto.
- Zehn sensible Key-Felder in der Claude-Oberfläche. Keine Keys in Werkzeugparametern,
  Befehlszeilenargumenten oder Paketdateien. Header-Steuerzeichen werden abgelehnt.
  Fehler enthalten keine Rohantworten oder Eingabewerte; zurückgegebene konfigurierte
  Keys werden auch in verschachtelten JSON-Antworten und Objektschlüsseln maskiert.
- Kontonamen dürfen keine konfigurierten Keys enthalten. `list_configured_accounts`
  liefert nur Namen und Standardkonto. Der Server schreibt keine Zugangsdaten-Dateien.
- Auf ausdrücklichen Wunsch aktualisiert der MCPB-Starter ab 0.1.5 bei jedem
  MCP-Start auf die neueste kompatible stabile PyPI-Serverversion (`@latest`).
  Der Servercode und seine Laufzeitabhängigkeiten sind im MCPB nicht festgelegt.
  Vorabversionen werden ausgeschlossen, die Server-Metadaten bei jedem Start
  aktualisiert und bereits separat installierte Tools ignoriert. `.env`-Dateien
  und lokale UV-Konfigurationsdateien werden nicht geladen.
- Kontoeinstellungen werden unverändert als Prozessumgebung weitergegeben;
  der Starter verwendet keine Shell und schreibt keine Konfiguration.
- Die Release-Pipeline veröffentlicht zuerst auf PyPI und prüft den Start der
  veröffentlichten Version. Erst danach wird das macOS-Paket gebaut und hochgeladen;
  auf macOS wird der PyPI-Starter nochmals geprüft.
- Explizite Dateiliste für das MCPB: keine lokalen Umgebungen oder Kontodateien.
  GitHub-Actions sind auf Commit-IDs festgelegt; Tests müssen vor Paketbau und
  Veröffentlichung erfolgreich sein. Veröffentlichte Assets werden nicht automatisch
  mit `--clobber` überschrieben.

## Nachweise

- 98 automatisierte Tests: unter anderem alle registrierten GET-Operationen,
  Pfadmanipulation, Redirects, Eingabeprüfung, Antwortlimits, Zeitlimit, sichere
  Fehlermeldungen, Key-Maskierung, zehn UI-Konten und echte MCP-stdio-Verbindungen.
- Starttest des Release-Kandidaten als lokal gebautes Wheel durch den UV-Starter,
  mit mehreren Konten und absichtlich vorhandener `.env`. Vor Veröffentlichung
  wird nur die Paketquelle durch das lokale Wheel ersetzt.
- Update-Test mit gemeinsamem Cache: neuer stabiler Release wird beim nächsten Start
  gewählt, eine neuere Vorabversion nicht. Fallback-Starter bewahrt die Umgebung.
- Die nachfolgenden Abhängigkeits- und Schlüssel-Scans wurden für 0.1.4 durchgeführt;
  0.1.5 ändert keine Laufzeitabhängigkeiten. Sie prüfen keine künftigen PyPI-Versionen.
- Manifest mit dem offiziellen Werkzeug `@anthropic-ai/mcpb` 2.1.2 validiert.
- `pip-audit` auf den aus `uv.lock` exportierten Laufzeitabhängigkeiten:
  keine bekannten Schwachstellen zum Prüfzeitpunkt (lokale macOS/Python-Auswahl).
- `detect-secrets` 1.5.0 auf den versionierten Dateien, ohne Lockfile und statischen
  API-Katalog: Treffer ausschliesslich in Beispiel- und Testdaten. Kein kompletter
  Scan der historischen Git-Objekte.

## Grenzen und Betrieb

Die Claude-Oberfläche und ihre Schlüsselbundspeicherung werden vom Host bereitgestellt.
Das Manifest markiert Keys als sensibel; siehe [Claudes Dokumentation](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop).
Im laufenden Prozess sind Keys notwendigerweise im Speicher und in der von Claude
übergebenen Umgebung vorhanden. Wer Zugriff auf den lokalen Benutzeraccount oder
dessen Debugging-Werkzeuge hat, kann diese möglicherweise auslesen. Schlüssel nicht
in Screenshots oder kopierten Umgebungsdiagnosen weitergeben.

Wer JSON-Konfiguration nutzt, verwaltet eine lokale Klartextdatei; Dateirechte `600`
verwenden. Kontonamen und abgerufene Werbedaten gehen als MCP-Ergebnisse an den
verbundenen KI-Client. Werbeinhalte sind nicht vertrauenswürdig und dürfen nicht als
Handlungsanweisungen interpretiert werden. Die Kennzeichnung im Server ist keine
Garantie gegen Prompt Injection im Client.

Das Paket ist nicht signiert oder Apple-notarisiert. `SHA256SUMS` prüft die
Dateiintegrität, stellt aber keine unabhängige Herausgeber-Signatur dar. Installation
aus dem offiziellen Repository beziehen. Jeder Start benötigt eine erreichbare PyPI-Quelle. Laufende Sitzungen werden nicht
automatisch neu gestartet. Das einmalige Starter-Update von 0.1.4 muss importiert
werden. Künftige stabile PyPI-Releases werden ohne erneuten MCPB-Import ausgeführt;
diese Prüfung kann deren Sicherheit nicht vorwegnehmen. UV/Python, Build-Werkzeuge, Paketquellen, Claude und
die OpenAI Ads API bleiben externe Vertrauensgrenzen.

Es wurden keine echten Werbekonten abgefragt und keine Keys in Claude hinterlegt.
Der echte UI-Installationsdialog und Live-API-Zugriffe sind daher nicht durch diese
Prüfung abgedeckt. Der Paketstart und das MCP-Protokoll sind automatisiert getestet.

Sicherheitsprobleme ohne Zugangsdaten melden. Bei einem tatsächlich offengelegten
Key diesen im Ads Manager widerrufen und ersetzen; nicht in ein öffentliches Issue
kopieren.
