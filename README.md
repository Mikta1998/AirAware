# Global Air Quality Dashboard

This Streamlit app uses real-time data from the [World Air Quality Index (WAQI)](https://waqi.info/) API to display the current air quality (AQI) in cities around the world.

Its goal is to help users understand the air quality in any city and receive guidance on how to proceed based on live Air Quality Index values.

## How the App Works

The user can check the air quality in four different ways:

### 1. Manual Search by City - (Check a City)

- Enter any city name into the search bar.
- A request is sent to the WAQI API to fetch the latest AQI data.
- The app displays:
  - A color-coded AQI gauge showing the air quality level (Good, Moderate, Unhealthy, etc.).
  - Health advice based on the AQI value.
  - An interactive map showing the location of the city.
  - Option to save the city to a list of favourites.

---

### 2. Worldmap of Countries and Capitals with Air Pollution (AQI) - (Compare Capitals)

- An interactive world map where countries are colored based on their capital city's AQI:
  - Green (Good, 0–50)
  - Yellow (Moderate, 51–100)
  - Red (Unhealthy, >100)
  - Gray (No Data)
- Black dots represent the capital cities.
- Features:
  - Update button to refresh real-time AQI data (limited to once per hour).
  - Tabs for:
    - Top 10 capitals by AQI worldwide (best and worst).
    - Top 10 capitals by continent.
    - Capitals with AQI data.
    - Capitals without AQI data.
  - Compare two capitals side-by-side.

---

### 3. Auto-Detect User Location - (Check my Location)

- The app attempts to detect the user's city using the [ipinfo.io](https://ipinfo.io) API.
- Once the city is detected, the app displays:
  - A color-coded AQI gauge showing the air quality level.
  - Health advice based on the AQI value.
  - A map with the city's location.

> **Note:** IP-based location detection may be approximate and may detect nearby large cities instead of exact locations.

---

### 4. My Favourite Cities

- This page lists all cities saved by the user as favourites.
- For each saved city, it shows:
  - The latest AQI value.
  - The air quality category.
  - Health advice.
  - Geographic coordinates.
- Users can easily remove cities from their favourites list.

---

## App Features

- Real-time air quality monitoring (WAQI API)
- Manual search by city
- Auto-location detection
- World map with AQI-based coloring
- Health advice and AQI color legends
- Favorites saving and management
- Compare AQI between capitals
- Interactive Folium maps
- Modern design with custom CSS
"""
