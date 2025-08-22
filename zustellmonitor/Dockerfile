FROM python:3.11-slim

# Installiere System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /app

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Port freigeben
EXPOSE 8123

# Anwendung starten
CMD ["python", "main.py"]
