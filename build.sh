#!/bin/bash

# Zustellmonitor Addon Build-Skript
echo "Baue Zustellmonitor Addon..."

# Verzeichnisstruktur erstellen
mkdir -p templates

# Docker Image bauen
echo "Baue Docker Image..."
docker build -t zustellmonitor:latest .

# Image testen
echo "Teste Docker Image..."
docker run --rm -d --name zustellmonitor-test -p 8123:8123 zustellmonitor:latest

# Warte kurz und teste den Service
sleep 5
if curl -s http://localhost:8123/api/stats > /dev/null; then
    echo "✅ Addon läuft erfolgreich!"
    echo "🌐 Web-Interface: http://localhost:8123"
    echo "📊 API-Endpunkt: http://localhost:8123/api/stats"
else
    echo "❌ Addon konnte nicht gestartet werden"
fi

# Container stoppen
docker stop zustellmonitor-test

echo ""
echo "Build abgeschlossen!"
echo ""
echo "Installation in Home Assistant:"
echo "1. Repository hinzufügen"
echo "2. Addon installieren"
echo "3. Konfiguration anpassen"
echo "4. Addon starten"
