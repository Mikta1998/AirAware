# Architektur der AirAware WebApp

## Überblick

AirAware ist eine Webanwendung zur Visualisierung und Analyse der globalen Luftqualität (AQI). Sie kombiniert ein Python-Backend mit einer PostgreSQL-Datenbank und einem Streamlit-Frontend.

## Komponenten

### Backend

- Verantwortlich für das Abrufen, Verarbeiten und Speichern von AQI-Daten.
- Nutzt die REST-API des World Air Quality Index (WAQI), um Echtzeitdaten für Hauptstädte weltweit zu beziehen.
- Implementierung in Python, u.a. `api.py` für API-Anfragen und Datenmanagement.
- Speichert die AQI-Daten inkl. Metadaten (Koordinaten, Zeitstempel) in PostgreSQL.
- Verwendet Umgebungsvariablen (`.env`) für API-Key und Datenbankkonfiguration.
- Stellt Funktionen bereit, um Datenbank regelmäßig mit aktuellen Daten zu aktualisieren und Fallback-Daten zu verwenden, falls API nicht erreichbar ist.

### Datenbank

- PostgreSQL-Datenbank für persistente Speicherung der AQI-Daten.
- Daten bleiben beim Neustart der Container erhalten (persistent Docker-Volume).
- Verbindung über Umgebungsvariablen (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).

### Frontend

- Implementiert mit Streamlit.
- Zeigt interaktive Karten, Zeitreihen und Vorhersagen (Prophet-Modell) der AQI-Werte.
- Ermöglicht manuelle Suche, Favoritenverwaltung und dynamische Datenvisualisierung.
- Läuft als eigener Docker-Container und kommuniziert mit der Datenbank.

### Deployment & Konfiguration

- Docker-Compose orchestriert die Container (Datenbank + Streamlit-App).
- `.env`-Datei enthält alle notwendigen Konfigurationen (API-Key, DB-Zugang).
- Docker-Volumes sichern Datenpersistenz.
- Ports sind konfigurirbar (Standard: 5432 für DB, 8501 für Streamlit).

## Datenfluss

1. Backend ruft über REST-API aktuelle AQI-Daten ab.
2. AQI-Daten werden in der PostgreSQL-Datenbank gespeichert.
3. Frontend liest Daten aus der Datenbank aus und visualisiert sie.
4. Nutzerinteraktionen im Frontend ermöglichen gezielte Abfragen und Vorhersagen.

---

**Zusammenfassung:**  
Die modulare Architektur trennt Datenbeschaffung, Speicherung und Visualisierung klar. Docker sorgt für einfaches Deployment und portable Umgebung. Die Nutzung von Umgebungsvariablen und Persistenzvolumes gewährleistet flexible und stabile Ausführung.

