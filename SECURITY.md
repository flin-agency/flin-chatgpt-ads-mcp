# Sicherheitsprüfung 0.1.4

Geprüft am 6. November 2026: Servercode, Kontokonfiguration, Claude-Desktop-Starter,
Paketinhalt, Installationsskripte, GitHub-Workflows und festgelegte Laufzeitabhängigkeiten.
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
- MCPB enthält den geprüften Servercode und `uv.lock`. Keine automatische Ausführung
  einer künftig veröffentlichten Serverversion über `@latest`. Das Laden einer
  benachbarten `.env`-Datei ist im Starter deaktiviert.
- Explizite Dateiliste für das MCPB: keine lokalen Umgebungen oder Kontodateien.
  GitHub-Actions sind auf Commit-IDs festgelegt; Tests müssen vor Paketbau und
  Veröffentlichung erfolgreich sein. Veröffentlichte Assets werden nicht automatisch
  mit `--clobber` überschrieben.

## Nachweise

- 96 automatisierte Tests: unter anderem alle registrierten GET-Operationen,
  Pfadmanipulation, Redirects, Eingabeprüfung, Antwortlimits, Zeitlimit, sichere
  Fehlermeldungen, Key-Maskierung, zehn UI-Konten und echte MCP-stdio-Verbindungen.
- Starttest aus dem entpackten MCPB mit dem tatsächlichen Manifest-Befehl in einem
  Pfad mit Leerzeichen, mehreren Konten und einer absichtlich vorhandenen `.env`.
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
aus dem offiziellen Repository beziehen. Die erste Einrichtung benötigt Internet
für Python bzw. Abhängigkeiten. UV/Python, Build-Werkzeuge, Paketquellen, Claude und
die OpenAI Ads API bleiben externe Vertrauensgrenzen.

Es wurden keine echten Werbekonten abgefragt und keine Keys in Claude hinterlegt.
Der echte UI-Installationsdialog und Live-API-Zugriffe sind daher nicht durch diese
Prüfung abgedeckt. Der Paketstart und das MCP-Protokoll sind automatisiert getestet.

Sicherheitsprobleme ohne Zugangsdaten melden. Bei einem tatsächlich offengelegten
Key diesen im Ads Manager widerrufen und ersetzen; nicht in ein öffentliches Issue
kopieren.
