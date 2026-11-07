# flin ChatGPT Ads MCP

OpenAI-Werbedaten lesend auswerten, mit getrennten API-Keys für bis zu zehn Konten
in Claude Desktop. Eine JSON-Datei ist für diese Konten nicht erforderlich.

## Start auf dem Mac (Apple Silicon: M1 oder neuer)

1. **[Desktop-Paket herunterladen](https://github.com/flin-agency/flin-chatgpt-ads-mcp/releases/latest/download/flin-chatgpt-ads-mcp.mcpb)**.
2. In einer aktuellen Claude-Desktop-Version mit MCPB-0.4-/UV-Unterstützung unter
   **Einstellungen → Erweiterungen → Erweiterung installieren** importieren.
3. Die freigegebenen Werte vom zuständigen Administrator bzw. aus dem Passwortmanager
   holen. Für jedes genutzte Konto **Kontoname** und **OpenAI Ads API-Key** eintragen;
   ungenutzte Kontofelder leer lassen. Ein Standardkonto ist optional.
4. Die Anmeldung erfolgt über den **Advertiser API-Key**, ohne OAuth-Browserdialog.
   Erstellung und Nutzung müssen kundenseitig freigegeben sein. Ein normaler
   OpenAI-Modell-API-Key funktioniert nicht. Dieses Update erteilt keine Freigabe.
5. Claude neu starten und eingeben: **«Rufe nur `connection_status` auf, ohne weitere
   API-Abfragen.»** Erwartet: `configuration_status: configured`,
   `auth_status: unknown`, `live_access: not_checked`. `server_version` zeigt den
   tatsächlich gestarteten Server. Das bestätigt die lokale Einrichtung, keinen
   funktionierenden Kundenzugriff. Bei `incomplete` der ausgegebenen Hilfe folgen.

**JSON-Priorität:** Eine ausgewählte optionale Kontodatei ersetzt **alle** UI-Konten.
Eine fehlerhafte Datei führt zu `incomplete`; es wird nicht auf andere Keys gewechselt.
Dateiauswahl leeren, wenn die UI-Felder genutzt werden sollen. Kontonamen müssen
1–64 Buchstaben, Zahlen, `_` oder `-` enthalten und eindeutig sein. Ohne Namen gelten
`default`, `konto_2` bis `konto_10`. Bei mehreren Konten ohne Standard ist für
API-Aufrufe eine ausdrückliche Kontowahl erforderlich.

Die sensiblen Felder werden vom Claude-Host gespeichert und als Prozessumgebung
übergeben. Die konkrete Schutzwirkung hängt von Host und Betriebssystem ab;
Details und Bereinigung: [Datenschutz](PRIVACY.md), [Sicherheit](SECURITY.md),
[Hilfe](SUPPORT.md). Das Paket ist unsigniert. Intel-Macs und die bisherigen
Python-/stdio-Installationen bleiben unterstützt.

## Updates, Versionen und Fallback

Die **Erweiterungsversion** bezeichnet den Starter mit den UI-Feldern.
**`connection_status.server_version`** bezeichnet den laufenden Python-Server.
Einmalig das aktuelle Paket als Update importieren, auch bei installiertem Starter
0.1.5: Erst dadurch gilt die neue Versionsgrenze. ID und alle zehn Kontofelder
bleiben gleich. Eine zuvor ausgewählte JSON-Datei behält ihren Vorrang.

Bei jedem MCP-Neustart sucht der Starter die neueste stabile PyPI-Version innerhalb
**`>=0.1.6,<0.2`**. Die Grenze entspricht der vorhandenen Schnittstelle: `--desktop`,
zehn unveränderte Umgebungsfeldpaare, JSON-Priorität, bestehende Tools plus der
neue lokale Status. Vorabversionen und 0.2 oder höher werden nicht automatisch
übernommen. Kompatible 0.1-Patches erfordern keinen Paketimport. Änderungen an
Starter/UI oder ein neuer Schnittstellenbereich benötigen einen neuen Import.
Künftige Releases müssen diese Verträge weiterhin prüfen; die Grenze ist keine
Garantie für noch ungeprüfte Versionen.

Laufende Sitzungen werden nicht unterbrochen. Claude vollständig beenden und neu
öffnen, um ein Update zu übernehmen. Kontoeinstellungen werden nicht überschrieben.
Der Paketcache wird wiederverwendet, die Versionsprüfung benötigt aber Netzwerk.
**Offline-Fallback:** Eine bereits laufende Sitzung weiterverwenden und den
Neustart verschieben. Bei fehlgeschlagenem Start Verbindung wiederherstellen und
neu starten. Ein erfolgreicher Offline-Neustart wird nicht versprochen; bei einem
Releaseproblem kann der Administrator eine bekannte Serverversion manuell fixieren
(siehe [SUPPORT.md](SUPPORT.md)).

[Versionierte Pakete und Prüfsummen](https://github.com/flin-agency/flin-chatgpt-ads-mcp/releases)
bleiben neben dem stabilen Dateinamen verfügbar.

## Funktionen

22 Werkzeuge: lokaler Verbindungsstatus, konfigurierte Konten, Kontoinformationen,
Ausgabenlimits, Kampagnen, Anzeigengruppen, Anzeigen, Landingpage-Crawl, Insights,
Audit-Logs, Geo-Suche, Conversion-Einstellungen, Pixel und Produktfeeds.
Nur fest hinterlegte GET-Endpunkte, keine freien URLs oder Schreiboperationen.
`connection_status` öffnet keinen Browser, fragt keine API ab und gibt weder Keys
noch Kontonamen oder Kundendaten aus. Live-Abfragen erfolgen ausschliesslich über
die bestehenden Datentools nach entsprechender Freigabe.

## Alternative macOS-Installation für andere MCP-Clients

1. Die versionierte `.pkg` aus den [Releases](https://github.com/flin-agency/flin-chatgpt-ads-mcp/releases) öffnen. Es legt das Installationspaket
   unter `/Applications/flin ChatGPT Ads MCP` ab. Alternativ die ZIP entpacken.
2. Dort `install.command` öffnen. Benötigt **uv oder Python 3.11+** und Internet
   für Abhängigkeiten. Mit uv wird bei Bedarf Python 3.12 bereitgestellt.
3. API-Key in `~/.config/flin-chatgpt-ads-mcp/config.json` eintragen.
4. Den ausgegebenen absoluten Programmpfad im MCP-Client konfigurieren.

Das Paket enthält das Python-Wheel; PyPI muss für diese Erstinstallation noch
nicht eingerichtet sein. Es ist nicht Apple-signiert oder notarisiert.
Intel und Apple Silicon werden über die passende lokale Python-Laufzeit unterstützt.
Die Installation überschreibt keine bestehende Kontokonfiguration.

## Konfiguration

Advertiser API-Keys werden in den Einstellungen des OpenAI Ads Managers erstellt.
Ein Key gehört zu einem Werbekonto; ein normaler OpenAI-Modell-API-Key genügt nicht.

Standarddatei: `~/.config/flin-chatgpt-ads-mcp/config.json`.
Alternativ `--config /absoluter/pfad/config.json` oder `FLIN_CHATGPT_ADS_CONFIG`.

```json
{
  "default_account": "kunde_a",
  "accounts": {
    "kunde_a": {"api_key": "DEIN_ADVERTISER_API_KEY"},
    "kunde_b": {"api_key_env": "OPENAI_ADS_KUNDE_B_API_KEY"}
  }
}
```

Pro Eintrag genau `api_key` oder `api_key_env` verwenden. Bei mehreren Konten ohne
Default muss jeder Aufruf `account` enthalten. `list_configured_accounts` zeigt
nur die Namen. Für ein einzelnes Konto ist alternativ `OPENAI_ADS_API_KEY`
ohne Datei möglich. Dateien mit echten Keys nicht in Git ablegen; Dateirechte `600` nutzen.

MCP-Client-Konfiguration nach macOS-Installation (BENUTZER ersetzen):

```json
{
  "mcpServers": {
    "flin-chatgpt-ads": {
      "command": "/Users/BENUTZER/.local/share/flin-chatgpt-ads-mcp/venv/bin/flin-chatgpt-ads-mcp",
      "args": ["--config", "/Users/BENUTZER/.config/flin-chatgpt-ads-mcp/config.json"]
    }
  }
}
```

Für Clients mit anderem Konfigurationsformat dieselben `command`/`args` verwenden.
Dieser lokale stdio-Server benötigt einen Client mit Unterstützung für lokale MCPs.

## PyPI und Updates

Nach der ersten PyPI-Veröffentlichung:

```sh
uv tool install flin-chatgpt-ads-mcp
uv tool upgrade flin-chatgpt-ads-mcp
```

Für die macOS-Paketinstallation stattdessen `update.command` öffnen. Das aktualisiert
die bei der Erstinstallation angelegte Umgebung. Anschliessend MCP-Client neu starten.
Die Konfiguration bleibt erhalten. Updates werden bewusst manuell gestartet.

PyPI Trusted Publisher einrichten:

| Einstellung | Wert |
| --- | --- |
| Project | `flin-chatgpt-ads-mcp` |
| Owner | `flin-agency` |
| Repository | `flin-chatgpt-ads-mcp` |
| Workflow | `release.yml` |
| Environment | `pypi` |

Das GitHub-Environment `pypi` ebenfalls anlegen. Releases lösen Tests und PyPI-Publishing
aus. Erst nach erfolgreichem PyPI-Publishing und einem echten Starttest der neuesten
PyPI-Version werden die macOS-Pakete gebaut und an das Release angehängt. Version in `pyproject.toml`, `desktop/manifest.json` und `__init__.py` erhöhen,
Lockfile aktualisieren, dann Release mit passendem `vX.Y.Z`-Tag erstellen.
Ein PyPI-API-Token wird durch Trusted Publishing nicht benötigt.

## Reporting und Pagination

Erst `get_ad_account` für Währung und Zeitzone aufrufen. Bei `has_more=true`
den Wert von `last_id` als `after` übergeben. Ergebnisse bleiben unverändert im
Feld `result`, mit dem ausgewählten Konto im Feld `account`.

Beispielargumente für `get_ad_account_insights`:

```json
{
  "account": "kunde_a",
  "aggregation_level": "campaign",
  "time_granularity": "daily",
  "fields": ["campaign.id", "campaign.name", "campaign.impressions", "campaign.clicks", "campaign.spend"],
  "time_ranges": ["{\"type\":\"unix_range\",\"start\":1777075200,\"end\":1777248000}"],
  "attribution_window_days": 30,
  "view_through_attribution_window_days": 1,
  "attribution_time_basis": "ad_event_time"
}
```

Zeitstempel an den gewünschten Berichtszeitraum und die Kontozone anpassen.
`time_ranges` akzeptiert auch `["2026-10-01..2026-11-02"]`: beide Tage inklusive,
in der Kontozone. Der MCP übersetzt dies in den dokumentierten `date_range`-Typ;
auch Zeitumstellungen bleiben dadurch korrekt. JSON-kodierte Zeitbereiche funktionieren weiterhin.
Bei unsegmentierten Berichten werden kurze Kennzahlennamen wie `clicks`, `spend`
oder `conversions` um die Berichtsebene ergänzt, z. B. `campaign.clicks`.
Ohne `fields` liefert die API standardmässig überwiegend Impressionen und Metadaten.
`filters` und `sort` enthalten JSON-kodierte Strings gemäss API.
Fehlende Kennzahlen sind nicht automatisch null/0; aktuelle Tagesdaten können vorläufig sein.

## Entwicklung

```sh
uv sync --extra dev
uv run pytest
uv run ruff check .
uv build
bash scripts/build_macos.sh
```

Der letzte Schritt benötigt macOS (`pkgbuild`, `ditto`). Die Tests verwenden
simulierte API-Antworten; ein Live-Test benötigt einen echten Advertiser API-Key.

Die Werkzeugdefinitionen basieren auf der offiziellen Spezifikation vom 03.11.2026.
Die Auswahl ist fest hinterlegt; neue API-Schreiboperationen können nicht automatisch
als Tools erscheinen. API-Funktionsumfang kann je nach Konto/Freischaltung variieren.

Quellen: [API-Übersicht](https://developers.openai.com/ads/api-overview),
[OpenAPI-Spezifikation](https://developers.openai.com/ads/openapi.json),
[Insights](https://developers.openai.com/ads/api-reference/insights),
[Authentifizierung](https://developers.openai.com/ads/api-reference/authentication).
