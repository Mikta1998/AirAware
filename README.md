# Global Air Quality Dashboard

This Streamlit app uses real-time data from the [World Air Quality Index (WAQI)](https://waqi.info/) API to display the current air quality (AQI) in cities around the world.

Its goal is to help users understand the air quality in any city and receive guidance on how to proceed based on live Air Quality Index values.

##  How the App Works

The user can check the air quality in two different ways.

### 1. Manual Search by City - (Check a City)

- Enter any city name into the search bar.
- A request is sent to the WAQI API to fetch the latest AQI data.
- The app displays:
  - A color-coded chart showing the air quality level (Good, Moderate, Unhealthy, etc.).
  - Health advice based on the AQI
  - A map showing the location of the city.

### 2. Worldmap of countries and capitals with Air pollution (AQI) - (Copare Capitals)
- Colored map (green, yellow, red, gray) based on AQI categories 
- Capital marked with black dots on the worldmap
- Custom legend and an interactive worldmap
- Update button to refresh realtime AQI data via API call - currently limited by 1 hour
  - Tabs for:
    - Top10 AQI-ranked capitals (worldwide and per continent)
    - All capitals with AQI data
    - More capitals without AQI data

### 3. Auto-Detects User Location - (Check my Location)

- The app attempts to detect the user's current city based on their IP address using the [ipinfo.io](https://ipinfo.io) API.
- This IP-based detection estimates the user’s location, usually by identifying the nearest big city.
- Once the city is determined the same app display the same information as in the Manual Search by City:
  - A color-coded chart showing the air quality level (Good, Moderate, Unhealthy, etc.).
  - Health advice based on the AQI
  - A map showing the location of the city.
  
> **Note:** IP-based detection is approximate and may be incorrect at times. It's an attempt to show what the app could be capable of if there were a way to pinpoint the exact location of the user using streamlit.


### 4. My favourite Cities
- This page saves all your favourite cities
- This can be seen as a quick view of a city's air pollution score

## App Features

- Real-time air quality monitoring
- Gauge chart with color scale (green to maroon)
- Health recommendations based on AQI levels
- Interactive Folium maps
- Sidebar navigation to switch between city search and auto-location
- Dashboard of capitals AQI data
- Comparison tool of two capitals
- Saving your favourite cities
