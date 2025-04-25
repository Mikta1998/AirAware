import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from capitals_data import get_capitals


# loads the environment variable from .evn file
load_dotenv()

# WAQI API token
WQAI_API_KEY = os.getenv("WQAI_API_KEY")

# Path to fallback AQI data
DUMMY_DATA_FILE = "capitals_data.json"

def load_dummy_data():
    '''
    Load fallback AQI data from local file, if available.
    '''
    try:
        with open(DUMMY_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_dummy_data(data):
    '''
    Save AQI data to loacal fallback file.
    '''
    with open(DUMMY_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

dummy_data = load_dummy_data()

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

def store_dummy_data(country, city, aqi_data):
    """
    Store AQI data as fallback for a given country and city.
    """
    dummy_data[country] = {
        "capital": city,
        "aqi": aqi_data["aqi"],
        "lat": aqi_data["lat"],
        "lon": aqi_data["lon"],
        "timestamp": aqi_data["timestamp"]
    }

    save_dummy_data(dummy_data)

def get_aqi_for_city(city, country):
    """
    Retrieve current AQI data for a given city and country.
    Retruns fresh data from API if possible, otherwise uses recent fallback data. 
    """
    # checks if fallback data exists
    if country in dummy_data:
        last_update = datetime.fromisoformat(dummy_data[country]["timestamp"])#
        # Use fallback data if it's less than one hour old
        if datetime.now() - last_update < timedelta(hours=1):  
            print(f"Using dummy data for {city} ({country})")
            return dummy_data[country]
    
    # Try to fetch live data from the API
    print(f"Fetching data from API for {city} ({country})...")
    aqi_data = fetch_aqi(city)

    if aqi_data:
        store_dummy_data(country, city, aqi_data)
        return aqi_data
    else:
        print(f"API call failed for {city}. Returning stored dummy data...")
        return dummy_data.get(country, None)

def fetch_and_store_aqi_for_all_countries():
    '''
    Update and store AQI data for all capitals from the get_capitals()
    Skips update if data has already been updated today.
    '''
    today_str = datetime.now().strftime('%Y-%m-%d')
    last_updated_date = dummy_data.get("last_updated_date", "")

    if last_updated_date == today_str:
        print("Data have been updated today. Using saved data.")
        return

    print("Updating AQI-Data for all capitals...")

    # gets the information of countries and capitals
    capitals_list = get_capitals()  
    
    for entry in capitals_list:
        country = entry["country"]
        capital = entry["city"]
        aqi_data = get_aqi_for_city(capital, country)

        if aqi_data:
            store_dummy_data(country, capital, aqi_data)
            print(f"{country}: {capital} - AQI: {aqi_data['aqi']} (Aktualisiert: {aqi_data['timestamp']})")
        else:
            print(f"Error by calling the data of {country}: {capital}")

    # Store the date of last successful update
    dummy_data["last_updated_date"] = today_str
    save_dummy_data(dummy_data)
