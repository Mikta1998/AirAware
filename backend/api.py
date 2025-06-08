import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backend.capitals_data import get_capitals
from backend.data.new_database import PostgresDB


# loads the environment variable from .evn file
load_dotenv()

# WAQI API token
WQAI_API_KEY = os.getenv("WQAI_API_KEY")

def fetch_aqi(city):
    """
    Fetch real-time AQI-data for a specific city using the WAQI API.
    Returns a dictionary with AQI and metadata, or Nine if the request fails.
    """
    url = f"https://api.waqi.info/feed/{city}/?token={WQAI_API_KEY}"
    
    try:
        res = requests.get(url, timeout=5)
        data = res.json()

        if data["status"] == "ok":
            return {
                "city": city, # city name
                "aqi": data["data"]["aqi"], # AQI-value
                "lat": data["data"]["city"]["geo"][0], # longitude
                "lon": data["data"]["city"]["geo"][1], # latitude
                "timestamp": datetime.now().isoformat()  # saves the timestamp
            }
    except Exception:
        pass
    
    return None

def fetch_and_store_aqi_for_all_countries():
    """
    Holt und speichert AQI-Daten für alle Hauptstädte in der PostgreSQL-DB.
    Nutzt Fallback-Daten, falls API nicht erreichbar ist.

    Gets and saves aqi data for all capitals in the PostgreSQL-DB.
    Uses fallback data, if api is not reachable.
    """
    print("Updating AQI-Data for all capitals...")

    capitals_list = get_capitals()
    db = PostgresDB()

    for entry in capitals_list:
        country = entry["country"]
        capital = entry["city"]
        aqi_data = get_aqi_for_city(capital, country)  # gets data from fallback

        if aqi_data:
            # checks if all values exists and are correct
            if None in [aqi_data.get("lat"), aqi_data.get("lon"), aqi_data.get("aqi")]:
                print(f"Uncorrect data for {country}: {capital}, skip insert: {aqi_data}")
                continue
            try:
                db.insert_aqi(
                    country=country,
                    city=capital,
                    lat=aqi_data["lat"],
                    lon=aqi_data["lon"],
                    aqi=aqi_data["aqi"],
                    timestamp=aqi_data["timestamp"]
                )
                print(f"{country}: {capital} - AQI: {aqi_data['aqi']} ({aqi_data['timestamp']}) saved!")
            except Exception as e:
                print(f"Error while saving in the database for {country}: {capital}: {e}")
                try:
                    db.conn.rollback()
                except Exception as rollback_e:
                    print(f"Rollback error: {rollback_e}")

        else:
            print(f"Error by calling the data of {country}: {capital}")


def get_aqi_for_city(city, country):
    """
    Retrieve current AQI data for a given city and country.
    Retruns fresh data from API if possible, otherwise uses recent fallback data. 
    """
    
    # Try to fetch live data from the API
    print(f"Fetching data from API for {city} ({country})...")
    aqi_data = fetch_aqi(city)

    if aqi_data:
        return aqi_data
    else:
        print(f"API call failed for {city}. Returning stored dummy data...")