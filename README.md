# Global Air Quality Dashboard

This Streamlit app uses real-time data from the [World Air Quality Index (WAQI)](https://waqi.info/) API to display the current air quality (AQI) in cities around the world.

Its goal is to help users understand the air quality in any city and receive guidance on how to proceed based on live Air Quality Index values.

##  How the App Works

The user can check the air quality in two different ways.

### 1. Manual Search by City

- Enter any city name into the search bar.
- A request is sent to the WAQI API to fetch the latest AQI data.
- The app displays:
  - A color-coded chart showing the air quality level (Good, Moderate, Unhealthy, etc.).
  - Health advice based on the AQI
  - A map showing the location of the city.


### 2. Auto-Detects User Location

- The app attempts to detect the user's current city based on their IP address using the [ipinfo.io](https://ipinfo.io) API.
- This IP-based detection estimates the user’s location, usually by identifying the nearest big city.
- Once the city is determined the same app display the same information as in the Manual Search by City:
  - A color-coded chart showing the air quality level (Good, Moderate, Unhealthy, etc.).
  - Health advice based on the AQI
  - A map showing the location of the city.
  
> **Note:** IP-based detection is approximate and may be incorrect at times. It's an attempt to show what the app could be capable of if there were a way to pinpoint the exact location of the user using streamlit.


## App Features

- Real-time air quality monitoring
- Gauge chart with color scale (green to maroon)
- Health recommendations based on AQI levels
- Interactive Folium map
- Sidebar navigation to switch between city search and auto-location
