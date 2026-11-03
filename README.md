# flin ChatGPT Ads MCP

Read-only MCP für die **OpenAI Advertiser API**, mit separaten API-Keys pro Kundenkonto.
Python 3.11+, MCP über stdio. Version 0.1.0.

## Funktionen

21 Werkzeuge: konfigurierte Konten, Kontoinformationen und Ausgabenlimits,
Kampagnen, Anzeigengruppen, Anzeigen, Landingpage-Crawl, Insights auf vier Ebenen,
Audit-Logs, Geo-Suche, Conversion-Einstellungen, Pixel sowie Produktfeeds und Uploadstatus.

Nur fest hinterlegte GET-Endpunkte sind erreichbar. Es gibt kein Werkzeug für
freie URLs, HTTP-Methoden, Uploads, Änderungen oder Aktivierung. Auch der per POST
abgefragte Conversion-Sonderreport ist in dieser Version ausgeschlossen.
API-Keys werden nur aus der lokalen Konfiguration gelesen, niemals als
Werkzeugparameter angefordert. Weiterleitungen werden nicht verfolgt.

## Claude Desktop auf macOS (.mcpb)

Für Claude Desktop **`flin-chatgpt-ads-mcp-0.1.0.mcpb`** aus den GitHub-Releases laden
und öffnen bzw. in Claude Desktop als lokale Erweiterung installieren.
In den Erweiterungseinstellungen den **OpenAI Ads API-Key** eintragen. Für mehrere
Kundenkonten stattdessen eine JSON-Datei wie im Abschnitt Konfiguration auswählen.
Die ausgewählte Datei hat Vorrang; ohne Dateiauswahl wird nur der eingetragene Key genutzt.

Benötigt eine aktuelle Claude-Desktop-Version mit MCPB-0.4-/UV-Unterstützung.
Claude Desktop verwaltet Python und Abhängigkeiten; beim ersten Start ist Internet nötig.
Das Paket enthält den Servercode und benötigt für die Erstinstallation kein PyPI-Release.
API-Keys sind als sensible Einstellung markiert und werden nicht im Paket gespeichert.
Die lokale Konfigurationsdatei muss bei Verwendung weiter vorhanden sein.

Updates für diese Installation: eine neue `.mcpb`-Version in Claude Desktop importieren.
`update.command` und `uv tool upgrade` betreffen separate Installationen, nicht die
von Claude verwaltete Erweiterung.

## Alternative macOS-Installation für andere MCP-Clients

1. `flin-chatgpt-ads-mcp-0.1.0-macos.pkg` öffnen. Es legt das Installationspaket
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
| Workflow | `publish.yml` |
| Environment | `pypi` |

Das GitHub-Environment `pypi` ebenfalls anlegen. Releases lösen Tests, PyPI-Publishing
und macOS-Paketbau aus. Version in `pyproject.toml` und `__init__.py` erhöhen,
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
`time_ranges`, `filters` und `sort` enthalten JSON-kodierte Strings gemäss API.
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
