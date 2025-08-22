#!/usr/bin/env python3
"""
Zustellmonitor - Home Assistant Addon
Überwacht Sendungen und deren Zustellstatus über die CarLo WebAPI
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class CarLoAPI:
    """CarLo WebAPI Client"""
    
    def __init__(self, host: str, port: int, username: str, password: str, 
                 organization_number: str, api_key: str):
        self.base_url = f"http://{host}:{port}"
        self.username = username
        self.password = password
        self.organization_number = organization_number
        self.api_key = api_key
        self.token = None
        self.session = requests.Session()
        self.session.timeout = 30
    
    def login(self) -> bool:
        """An der CarLo API anmelden"""
        try:
            url = f"{self.base_url}/login"
            data = {
                "username": self.username,
                "password": self.password,
                "organizationNumber": self.organization_number,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            response = self.session.post(url, data=data, headers=headers)
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return bool(self.token)
            else:
                logger.error(f"Login fehlgeschlagen: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Login-Fehler: {e}")
            return False
    
    def get_deliveries(self) -> List[Dict]:
        """Alle aktuellen Sendungen abrufen"""
        if not self.token and not self.login():
            return []
        
        try:
            url = f"{self.base_url}/api/Scannerapp/v1/SsccCurrent/0"
            headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "X-API-KEY": self.api_key,
            }
            
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("ssccCurrent", [])
            elif response.status_code == 401:
                # Token abgelaufen, neu anmelden
                if self.login():
                    return self.get_deliveries()
                return []
            else:
                logger.error(f"API-Fehler: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Sendungen: {e}")
            return []

class DeliveryMonitor:
    """Zustellmonitor Hauptklasse"""
    
    def __init__(self, api: CarLoAPI, update_interval: int = 10):
        self.api = api
        self.update_interval = update_interval
        self.deliveries = []
        self.last_update = None
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.update_deliveries, 'interval', minutes=update_interval)
        self.scheduler.start()
        
        # Initial laden
        self.update_deliveries()
    
    def update_deliveries(self):
        """Sendungen von der API aktualisieren"""
        try:
            self.deliveries = self.api.get_deliveries()
            self.last_update = datetime.now()
            logger.info(f"Sendungen aktualisiert: {len(self.deliveries)} gefunden")
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren: {e}")
    
    def get_deliveries(self, filters: Dict = None, sort_by: str = None, 
                      sort_order: str = "asc") -> List[Dict]:
        """Gefilterte und sortierte Sendungen zurückgeben"""
        deliveries = self.deliveries.copy()
        
        # Filter anwenden
        if filters:
            for key, value in filters.items():
                if value:
                    deliveries = [d for d in deliveries if 
                                str(d.get(key, "")).lower().find(str(value).lower()) != -1]
        
        # Sortierung anwenden
        if sort_by and deliveries:
            reverse = sort_order.lower() == "desc"
            deliveries.sort(key=lambda x: str(x.get(sort_by, "")), reverse=reverse)
        
        return deliveries
    
    def get_delivery_stats(self) -> Dict:
        """Statistiken der Sendungen"""
        if not self.deliveries:
            return {"total": 0, "delivered": 0, "pending": 0, "overdue": 0}
        
        total = len(self.deliveries)
        delivered = len([d for d in self.deliveries if d.get("statusText", "").lower() in 
                        ["zugestellt", "delivered", "completed"]])
        pending = total - delivered
        
        # Überfällige Sendungen (Status "spät" oder ähnlich)
        overdue = len([d for d in self.deliveries if d.get("statusText", "").lower() in 
                      ["spät", "late", "overdue", "verzögert"]])
        
        return {
            "total": total,
            "delivered": delivered,
            "pending": pending,
            "overdue": overdue
        }

# Globale Instanzen
api = None
monitor = None

def initialize_app():
    """Anwendung initialisieren"""
    global api, monitor
    
    # Konfiguration aus Umgebungsvariablen oder Standardwerten
    config = {
        "host": os.getenv("host", "wogdb"),
        "port": int(os.getenv("port", 4711)),
        "username": os.getenv("username", "MABU"),
        "password": os.getenv("password", "detimk23"),
        "organization_number": os.getenv("organization_number", "1"),
        "api_key": os.getenv("api_key", "KJEETC2J[5Bad5!70F9T"),
        "update_interval": int(os.getenv("update_interval", 10))
    }
    
    api_config = {k: v for k, v in config.items() if k != "update_interval"}
    api = CarLoAPI(**api_config)
    monitor = DeliveryMonitor(api, config["update_interval"])
    
    logger.info("Zustellmonitor initialisiert")

# Flask Routen
@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')

@app.route('/api/deliveries')
def api_deliveries():
    """API-Endpunkt für Sendungen"""
    if not monitor:
        return jsonify({"error": "Monitor nicht initialisiert"}), 500
    
    filters = {
        "code": request.args.get("code"),
        "statusText": request.args.get("status"),
        "location1": request.args.get("location")
    }
    
    sort_by = request.args.get("sort_by", "code")
    sort_order = request.args.get("sort_order", "asc")
    
    deliveries = monitor.get_deliveries(filters, sort_by, sort_order)
    return jsonify({
        "deliveries": deliveries,
        "last_update": monitor.last_update.isoformat() if monitor.last_update else None
    })

@app.route('/api/stats')
def api_stats():
    """API-Endpunkt für Statistiken"""
    if not monitor:
        return jsonify({"error": "Monitor nicht initialisiert"}), 500
    
    return jsonify(monitor.get_delivery_stats())

@app.route('/api/update')
def api_update():
    """Manueller Update der Sendungen"""
    if not monitor:
        return jsonify({"error": "Monitor nicht initialisiert"}), 500
    
    monitor.update_deliveries()
    return jsonify({
        "success": True,
        "message": "Sendungen aktualisiert",
        "count": len(monitor.deliveries)
    })

if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=8123, debug=False)
