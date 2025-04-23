import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from capitals_data import get_capitals


# Lade Umgebungsvariablen
load_dotenv()

# WAQI API token
WQAI_API_KEY = os.getenv("WQAI_API_KEY")

# Path to fallback AQI-values
DUMMY_DATA_FILE = "capitals_data.json"

def load_dummy_data():
    '''
    This loads the fallback AQI-values if exists
    '''
    try:
        with open(DUMMY_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_dummy_data(data):
    '''
    this saves the fallback AQI-values as a json file
    '''
    with open(DUMMY_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

dummy_data = load_dummy_data()

def fetch_aqi(city):
    """
    Calls the AQI-Values of a city.
    """
    url = f"https://api.waqi.info/feed/{city}/?token={WQAI_API_KEY}"
    
    try:
        res = requests.get(url, timeout=5)
        data = res.json()

        if data["status"] == "ok":
            return {
                "city": city,
                "aqi": data["data"]["aqi"],
                "lat": data["data"]["city"]["geo"][0],
                "lon": data["data"]["city"]["geo"][1],
                "timestamp": datetime.now().isoformat()  # saves the timestamp
            }
    except Exception:
        pass
    
    return None

def store_dummy_data(country, city, aqi_data):
    """
    This function saves fallback AQI-Values.
    The fallback AQI-Values are the last known values, for example of your last update.
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
    This function asks for the current AQI-Values.
    """
    # Prüfen, ob es die Dummy-Daten gibt
    if country in dummy_data:
        # checks if fallback values are at least current, for example less of one hour ago
        last_update = datetime.fromisoformat(dummy_data[country]["timestamp"])
        if datetime.now() - last_update < timedelta(hours=1):  # calculates if fallback data is relative current
            print(f"Using dummy data for {city} ({country})")
            return dummy_data[country]
    
    # API-Request if no AQI-values is knonw
    print(f"Fetching data from API for {city} ({country})...")
    aqi_data = fetch_aqi(city)

    if aqi_data:
        # if values exists, save as fallback data
        store_dummy_data(country, city, aqi_data)
        return aqi_data
    else:
        # if API fails, fallback data is the output
        print(f"API call failed for {city}. Returning stored dummy data...")
        return dummy_data.get(country, None)

def fetch_and_store_aqi_for_all_countries():
    '''
    Call and save the AQI-Data
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

    # Update global "last_updated_date"
    dummy_data["last_updated_date"] = today_str
    save_dummy_data(dummy_data)
