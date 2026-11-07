# Datenschutz

Der Server läuft lokal über stdio. Es gibt keinen eigenen flin-Cloud-Dienst,
keine Telemetrie und keine lokale Speicherung abgerufener Berichte durch den Server.

- Claude übergibt die eingetragenen API-Keys als Prozessumgebung. Bei einer
  optionalen JSON-Datei liest der Server stattdessen die dort angegebenen Keys bzw.
  Umgebungsvariablen. Die Datei ist Klartext; Dateirechte `600` verwenden.
- Bei ausdrücklich angeforderten Datentools gehen der ausgewählte Key und die
  Abfrageparameter über HTTPS an `api.ads.openai.com`. Werbedaten und Kontonamen
  gelangen als MCP-Ergebnisse an Claude bzw. den verbundenen Client und unterliegen
  dessen Speicher- und Datenverarbeitungsregeln. Sie können im Chat erhalten bleiben.
- `connection_status` prüft nur die lokale Konfiguration und sendet keine API-Anfrage.
  Ein vorhandener Key ist kein Beleg für eine erfolgreiche Anmeldung oder Freigabe.
- Der Starter kontaktiert PyPI für Paketversionen/Downloads; UV kann zusätzlich
  Python und Abhängigkeiten laden. Der Starter sendet keine Ads-Keys an PyPI.
  Heruntergeladener Servercode erhält zur Laufzeit die konfigurierten Keys.

Die UI-Felder sind als sensibel markiert. Speicherung und Schutz werden durch den
jeweiligen Claude-Host bestimmt; dieses Projekt garantiert keine bestimmte
Verschlüsselung oder Schlüsselbundnutzung. Keys liegen im laufenden Prozess vor.

Widerruf: Den Advertiser API-Key im Ads Manager bzw. durch den zuständigen
Administrator sperren/ersetzen. Nur das Entfernen der Erweiterung widerruft keinen
Key. Zur lokalen Bereinigung Erweiterungseinstellungen entfernen, eine verwendete
JSON-Datei und selbst angelegte Key-Umgebungsvariablen löschen sowie bei Bedarf
Chats/Exporte und Paketcache bereinigen. Einzelheiten: [SUPPORT.md](SUPPORT.md).
