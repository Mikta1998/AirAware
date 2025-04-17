import requests
import streamlit as st

# WAQI API token
API_TOKEN = "afc709dc393523e499cf5b668fac2c187635602c"

# Caches the result for 1 hour to reduce API calls
@st.cache_data(ttl=3600)
def fetch_aqi(city):
    # Builds the API request URL using the city and the token
    url = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"

    try:
        # Sends GET request to the WAQI API
        res = requests.get(url, timeout=5)
        data = res.json()

        # If the response is valid and contains data
        if data["status"] == "ok":
            return {
                "city": city,
                "aqi": data["data"]["aqi"],                        # Air Quality Index
                "lat": data["data"]["city"]["geo"][0],             # Latitude
                "lon": data["data"]["city"]["geo"][1]              # Longitude
            }

    except Exception:
        pass

    # Returns None if something went wrong or data was invalid
    return None