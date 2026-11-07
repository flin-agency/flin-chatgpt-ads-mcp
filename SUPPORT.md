# Hilfe

1. In Claude nur `connection_status` aufrufen. `server_version` ist die laufende
   Serverversion, die Erweiterungsversion in den Einstellungen ist der Starter.
2. `incomplete`: Key-Felder und eindeutige Kontonamen prüfen. Falls eine JSON-Datei
   ausgewählt ist, wird nur sie verwendet; korrigieren oder abwählen. Neu starten.
3. `configured`, `unknown`, `not_checked`: Lokal eingerichtet, Live-Zugriff noch
   ungeprüft. Es gibt keinen OAuth-Dialog. Advertiser-Key und kundenseitige Freigabe
   mit dem Administrator klären. Das Update selbst erteilt keine API-Freigabe.
4. API-Fehler nach einer freigegebenen Abfrage: Bei 401 den Key prüfen/ersetzen,
   bei 403 Kontozugriff/Freischaltung klären. Keys niemals zur Diagnose versenden.
5. Starterfehler: Aktuelles MCPB importieren, Claude aktualisieren, Internet/PyPI
   prüfen und vollständig neu starten. Laufende Sitzungen können weiterlaufen;
   ein Offline-Neustart ist nicht garantiert. Zehn UI-Konten bleiben beim Import
   unter derselben Erweiterungskennung erhalten; nicht vorher deinstallieren.

## Fallback für Administratoren

Bei einer fehlerhaften neuen Serverversion kann ein manuell eingerichteter
stdio-Client vorübergehend mit `uv tool run --from flin-chatgpt-ads-mcp==VERSION
flin-chatgpt-ads-mcp --config /absoluter/pfad/config.json` auf eine nachweislich
funktionierende veröffentlichte Version festgelegt werden. VERSION ersetzen;
kein Key als Befehlsargument. Dies ist ein bewusst manuell verwalteter Fallback,
kein automatischer Offline-Modus. Für Claude mit UI-Keys bevorzugt ein korrigiertes
MCPB vom Maintainer verwenden, statt Keys in eine neue Klartextdatei zu kopieren.

## Entfernen und Bereinigen

Zuerst Keys im Ads Manager widerrufen, wenn sie nicht mehr genutzt werden sollen.
Dann Erweiterung samt gespeicherten Feldern über Claudes Einstellungen entfernen.
Eine separat gewählte JSON-Datei wird dabei nicht automatisch gelöscht. Die
Standarddatei liegt unter `~/.config/flin-chatgpt-ads-mcp/config.json`. Ebenso selbst
angelegte Key-Umgebungsvariablen entfernen. UV-Paketcache optional mit
`uv cache clean flin-chatgpt-ads-mcp` bereinigen; das widerruft keine Keys und entfernt
keine Chatdaten. Bei alternativer PKG-Installation kann die nicht mehr benötigte
Umgebung unter `~/.local/share/flin-chatgpt-ads-mcp` entfernt werden.
Chats/Exporte und etwaige Host-Protokolle separat prüfen; nur ausgewählte eigene
Dateien löschen. Details zur Speicherung: [PRIVACY.md](PRIVACY.md).

Für öffentliche [Fehlermeldungen](https://github.com/flin-agency/flin-chatgpt-ads-mcp/issues)
nur Server-/Starterversion, macOS-Version, Architektur, die fünf Statusfelder und
bereinigte Fehlermeldung angeben. Keine Kontonamen, Keys, Kundenberichte oder
ungefilterten Umgebungsprotokolle mitsenden.
