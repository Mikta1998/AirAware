# AirAware – Global Air Quality Dashboard

## Einleitung

AirAware ist ein interaktives Dashboard zur Visualisierung und Analyse der Luftqualität (AQI) in Städten weltweit.  
Die App nutzt Echtzeitdaten der [World Air Quality Index (WAQI)](https://waqi.info/) API, speichert diese in einer PostgreSQL-Datenbank und bietet Zeitreihen-Analysen sowie Vorhersagen mit einem Prophet-Modell.

---

## Schnellstart (empfohlen: Docker)

### Voraussetzungen

- [Docker](https://www.docker.com/get-started) und [Docker Compose](https://docs.docker.com/compose/install/) installiert

### Schritt-für-Schritt-Anleitung

1. **Repository klonen**
    ```
    git clone https://github.com/Mikta1998/AirAware.git
    cd AirAware
    ```

2. **.env-Datei**  
    Eine .env wurde mit ins Projekt aufgenommen.
    Sie beinhaltet einen aktuellen API-Key von der WAQI-API und Konfigurationen für die PostGRE-SQL Datenbank.

3. **Container bauen und starten**
    ```
    docker-compose up --build
    ```

4. **App im Browser öffnen**  
   [http://localhost:8501](http://localhost:8501)

**Hinweise:**  
- Die Datenbank ist persistent (Daten bleiben beim Neustart erhalten).
- Die Zeitzone ist auf Europe/Berlin eingestellt.

---

## Alternativer Start (ohne Docker, nur für Entwicklung)

### Für Linux/macOS

1. **(Optional) Virtuelle Umgebung erstellen**
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Abhängigkeiten installieren**
    ```
    pip install -r requirements.txt
    ```

3. **App starten**
    ```
    streamlit run app.py
    ```

---

### Für Windows

1. **(Optional) Virtuelle Umgebung erstellen**
    ```
    python -m venv venv
    venv\Scripts\activate
    ```

2. **Abhängigkeiten installieren**
    ```
    pip install -r requirements.txt
    ```

3. **App starten**
    ```
    streamlit run app.py
    ```

---

## App Features

- **Manuelle Suche nach Städten** mit AQI-Anzeige, Gesundheitsratschlägen und Favoritenfunktion
- **Interaktive Weltkarte** mit AQI-Färbung der Hauptstädte
- **Zeitreihenplots** für AQI-Daten (24h/7d/30d)
- **Prognose-Tool:** Vorhersage der AQI-Werte für jede Hauptstadt (bis zu 7 Tage im Voraus, Prophet-Modell)
- **Favoritenverwaltung**
- **Persistente Speicherung** der AQI-Daten (PostgreSQL)
- **Automatische Aktualisierung** der Daten alle 15 Minuten
- **Modernes Design mit Custom CSS**
- **Interaktive Folium-Karten**

---

## Bekannte Probleme / FAQ

- **Port 8501 belegt:**  
  Passe den Port in der `docker-compose.yaml` an.
- **Docker-Fehler:**  
  Prüfe, ob Docker und Docker Compose korrekt installiert und gestartet sind.
- **Keine Daten:**  
  Die Datenbank wird beim ersten Start automatisch befüllt, dies kann wenige Sekunden dauern.

---

## Links

- **Live-Demo (Streamlit Cloud):**  
  [https://airaware-dashboard.streamlit.app/](https://airaware-dashboard.streamlit.app/)
- **GitHub-Projekt:**  
  [https://github.com/Mikta1998/AirAware](https://github.com/Mikta1998/AirAware)

---

## Kontakt

Bei Fragen oder Problemen gerne ein Issue auf GitHub eröffnen oder eine Mail an [deml20081@hs-ansbach.de] oder [timov20168@hs-ansbach.de] schicken.

---

**Viel Spaß mit AirAware!**
