# Zustellmonitor - Home Assistant Addon

Ein Home Assistant Addon zur Überwachung von Sendungen und deren Zustellstatus über die CarLo WebAPI.

## Funktionen

- **Automatische Aktualisierung**: Alle 10 Minuten werden die Sendungsdaten von der CarLo API geladen
- **Echtzeit-Überwachung**: Anzeige aller aktuellen Sendungen mit Status
- **Intelligente Farbkodierung**: 
  - 🟢 Grün: Zugestellte Sendungen
  - 🟡 Gelb: Ausstehende Sendungen  
  - 🔴 Rot: Überfällige/verspätete Sendungen
- **Filterfunktionen**: Nach Code/SSCC, Status und Standort filtern
- **Sortierung**: Sortierung nach verschiedenen Feldern (aufsteigend/absteigend)
- **Statistiken**: Übersicht über Gesamtanzahl, ausstehende, zugestellte und überfällige Sendungen
- **Responsive Design**: Funktioniert auf Desktop und mobilen Geräten

## Installation

### 1. Addon-Repository hinzufügen

Füge in Home Assistant unter **Einstellungen > Add-ons > Add-on-Store** das Repository hinzu:

```
https://github.com/dein-username/homeassistant-addons
```

### 2. Addon installieren

1. Gehe zu **Einstellungen > Add-ons > Add-on-Store**
2. Suche nach "Zustellmonitor"
3. Klicke auf "Installieren"

### 3. Konfiguration

Konfiguriere das Addon mit deinen CarLo API-Zugangsdaten:

```yaml
host: "wogdb"
port: 4711
username: "MABU"
password: "detimk23"
organization_number: "1"
api_key: "KJEETC2J[5Bad5!70F9T"
update_interval: 10
```

**Parameter:**
- `host`: CarLo Server Hostname/IP
- `port`: CarLo Server Port (Standard: 4711)
- `username`: Benutzername für die API
- `password`: Passwort für die API
- `organization_number`: Organisationsnummer
- `api_key`: API-Schlüssel
- `update_interval`: Aktualisierungsintervall in Minuten (Standard: 10)

### 4. Addon starten

1. Klicke auf "Start"
2. Das Addon ist dann unter der angegebenen URL erreichbar

## Verwendung

### Web-Interface

Das Addon stellt ein modernes Web-Interface bereit, das über den Browser erreichbar ist.

### API-Endpunkte

Das Addon bietet folgende REST-API-Endpunkte:

- `GET /api/deliveries` - Alle Sendungen abrufen
- `GET /api/stats` - Statistiken abrufen  
- `GET /api/update` - Manueller Update der Daten

### Filter-Parameter

Die API unterstützt folgende Filter-Parameter:

- `code` - Nach Code/SSCC filtern
- `status` - Nach Status filtern
- `location` - Nach Standort filtern
- `sort_by` - Sortierfeld (code, statusText, location1, createdAt)
- `sort_order` - Sortierreihenfolge (asc, desc)

## Technische Details

### Architektur

- **Backend**: Python Flask-Anwendung
- **Frontend**: HTML5 + Bootstrap 5 + JavaScript
- **Datenbank**: Keine (Daten werden direkt von der CarLo API geladen)
- **Container**: Docker-basiert

### Abhängigkeiten

- Python 3.11+
- Flask
- Requests
- APScheduler

### Ports

- **8123**: Web-Interface und API

## Fehlerbehebung

### Häufige Probleme

1. **Verbindungsfehler zur CarLo API**
   - Überprüfe Host und Port
   - Stelle sicher, dass der Server erreichbar ist

2. **Authentifizierungsfehler**
   - Überprüfe Benutzername, Passwort und API-Schlüssel
   - Stelle sicher, dass die Anmeldedaten korrekt sind

3. **Keine Daten angezeigt**
   - Überprüfe die API-Antworten in den Logs
   - Stelle sicher, dass die API Sendungsdaten zurückgibt

### Logs anzeigen

Die Logs des Addons findest du in Home Assistant unter:
**Einstellungen > Add-ons > Zustellmonitor > Logs**

## Entwicklung

### Lokale Entwicklung

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python main.py
```

### Docker Build

```bash
docker build -t zustellmonitor .
docker run -p 8123:8123 zustellmonitor
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

## Support

Bei Problemen oder Fragen erstelle bitte ein Issue im GitHub-Repository oder kontaktiere den Entwickler.
