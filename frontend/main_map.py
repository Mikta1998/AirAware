import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from backend.capitals_data import get_capitals
from backend.api import get_aqi_for_city
from backend.data.new_database import PostgresDB


UPDATE_INTERVAL_MINUTES = 15

db = PostgresDB()

# button for updating the AQI-values manually
def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def update_aqi_data():
    capitals_list = get_capitals()
    for entry in capitals_list:
        country = entry["country"]
        capital = entry["city"]
        aqi_data = get_aqi_for_city(capital, country)

        if aqi_data:
            aqi_value = safe_int(aqi_data.get("aqi"))
            if aqi_value is not None:
                db.insert_aqi(
                    country=country,
                    city=capital,
                    lat=aqi_data["lat"],
                    lon=aqi_data["lon"],
                    aqi=aqi_value,
                    timestamp=aqi_data["timestamp"]
                )

# automatically update of aqi values every 15 minutes
if "last_update" not in st.session_state:
    st.session_state["last_update"] = None

now = datetime.utcnow()

# automatic update, if session_state is set and 15 minutes are over
if st.session_state["last_update"] is not None:
    if now - st.session_state["last_update"] > timedelta(minutes=15):
        update_aqi_data()
        st.session_state["last_update"] = now


def get_aqi_color(aqi):
    '''
    Returns a hex color code corresponding to the AQI level.
    
    Parameters:
    - aqi (int or None): Air Quality Index value (AQI)

    Returns:
    - str: Hex color code representing AQI category:
        - AQI 0-50 (good) = green (#4caf50)
        - AQI 51-100 (moderate) = yellow (#ffeb3b)
        - AQI >100 (bad) = red (#f44336)
        - AQI None (No Data) = gray (#cccccc)
    '''

    if aqi is None:
        return "#cccccc" # gray=no data
    elif aqi <= 50:
        return "#4caf50" # green=good
    elif aqi <= 100:
        return "#ffeb3b" # yellow=moderate
    else:
        return "#f44336" # red=bad

def render_centered_table(df, aqi_col=True):
    '''
    Renders a pandas DataFrame with centered column styles.
    '''
    
    styles = [
        dict(selector="th.col0", props=[("text-align", "center")]),
        dict(selector="td.col0", props=[("text-align", "center")])
    ]
    if aqi_col and "Air pollution (AQI)" in df.columns:
        styles.append(dict(selector="th.col3", props=[("text-align", "center")]))
        styles.append(dict(selector="td.col3", props=[("text-align", "center")]))
    styled = df.style.set_table_styles(styles).hide(axis="index")
    st.markdown(styled.to_html(), unsafe_allow_html=True)

def show_worldmap():
    '''
    Displays a worldmap with countries coloured by the AQI value of their capital.
    '''
    # title and description
    st.markdown("<h4 style='margin-bottom: 0.5em;'>🌐 Worldmap: Air pollution by countries & capitals</h4>", unsafe_allow_html=True)
    
    st.write("This world map shows the capitals of each country. " \
    "Each country is coloured green (good), yellow (moderate), or red (bad) according to the AQI value of the capital. " \
    "The colour change is defined by the AQI spectrum.")

    # colour legend
    st.markdown("""
    <div style='display: flex; justify-content: center; gap: 24px; margin-bottom: 16px;'>
      <div style='display: flex; align-items: center; gap: 6px;'>
        <span style='display:inline-block;width:18px;height:18px;background:#4caf50;border-radius:50%;'></span> Good (0–50)
      </div>
      <div style='display: flex; align-items: center; gap: 6px;'>
        <span style='display:inline-block;width:18px;height:18px;background:#ffeb3b;border-radius:50%;border:1px solid #888;'></span> Moderate (51–100)
      </div>
      <div style='display: flex; align-items: center; gap: 6px;'>
        <span style='display:inline-block;width:18px;height:18px;background:#f44336;border-radius:50%;'></span> Bad (&gt;100)
      </div>
      <div style='display: flex; align-items: center; gap: 6px;'>
        <span style='display:inline-block;width:18px;height:18px;background:#000000;border-radius:50%;border:1px solid #888;'></span> Capitals
      </div>
      <div style='display: flex; align-items: center; gap: 6px;'>
        <span style='display:inline-block;width:18px;height:18px;background:#cccccc;border-radius:50%;border:1px solid #888;'></span> No Data
      </div>
    </div>
    """, unsafe_allow_html=True)

    # loading GeoJSON with land boarders
    geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    countries_geojson = requests.get(geojson_url).json()

    # loading database
    db = PostgresDB()

    # loading capitals data
    aqi = db.get_latest_aqi_per_city()

    # loading recent AQI data out of capitals_data.json or runs without data 
    try:
        with open("capitals_data.json", "r") as f:
            real_aqi_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        real_aqi_data = {}

    # maps the country with colour by it's capital AQI
    country_aqi_map = {c["country"]: c["aqi"] for c in aqi}

    def style_function(feature):
        country_name = feature["properties"]["name"]
        if country_name == "Antarctica":
            return {"fillOpacity": 0, "weight": 0, "color": "white", "fillColor": "white"}
        aqi = country_aqi_map.get(country_name, None)
        return {
            "fillOpacity": 0.7,
            "weight": 0.5,
            "color": "white",
            "fillColor": get_aqi_color(aqi)
        }

    # defining borders for the map
    min_lat, max_lat = -60, 75    # without arctis and antarctis
    min_lon, max_lon = -180, 180  # whole world in its width

    # calculating center of the map borders
    center_lat = (min_lat + max_lat) / 2
    center_lon = 0

    # start zoom (default)
    zoom_level = 2

    # map configurations
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        min_zoom=zoom_level,
        max_zoom=8,           
        tiles="CartoDB positron",
        max_bounds=True
    )

    folium.GeoJson(
        countries_geojson,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=[""], labels=False, sticky=False)
    ).add_to(m)

    # mapping the capitals on the worldmap
    for capital in aqi:
        folium.CircleMarker(
            location=[capital["lat"], capital["lon"]],
            radius=2,
            color="black",
            fill=True,
            fill_color="black",
            fill_opacity=1,
            tooltip=capital["city"]
        ).add_to(m)

    # shows the map
    st_folium(m, use_container_width=True, height=600)

    if st.button("🔄 Update"):
        st.info("Update can take up to 5 minutes.")
        with st.spinner("Loading new data..."):
            capitals_list = get_capitals()
            inserted_rows = []

            for entry in capitals_list:
                country = entry["country"]
                capital = entry["city"]
                aqi_data = get_aqi_for_city(capital, country)

                if aqi_data:
                    aqi_value = safe_int(aqi_data.get("aqi"))
                    if aqi_value is not None:
                        db.insert_aqi(
                            country=country,
                            city=capital,
                            lat=aqi_data["lat"],
                            lon=aqi_data["lon"],
                            aqi=aqi_value,
                            timestamp=aqi_data["timestamp"]
                        )
                        inserted_rows.append({
                            "country": country,
                            "city": capital,
                            "lat": aqi_data["lat"],
                            "lon": aqi_data["lon"],
                            "aqi": aqi_value,
                            "timestamp": aqi_data["timestamp"]
                        })

            st.success("Update finished.")

    # --------- TAB & DROPDOWN STYLING (CSS) ----------
    st.markdown("""
<style>
/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #23272b;
    border-radius: 8px 8px 0 0;
    padding: 0.2em 0.5em;
    margin-bottom: 0.5em;
    border: 1px solid #444;
}
.stTabs [data-baseweb="tab"] {
    color: #eee !important;
    padding: 0.5em 1.2em !important;
    font-weight: 500;
    border-radius: 6px 6px 0 0;
    margin-right: 0.2em;
}
.stTabs [aria-selected="true"] {
    background: #343a40 !important;
    color: #fff !important;
    border-bottom: 2px solid #4caf50 !important;
}
/* Selectbox closed */
div[data-baseweb="select"] > div {
    background-color: #23272b !important;
    color: #eee !important;
    border-radius: 6px !important;
    border: 1px solid #444 !important;
}
div[data-baseweb="select"] svg {
    color: #eee !important;
}

div[role="option"], li[role="option"], div[data-baseweb="option"] {
    background-color: #23272b !important;
    color: #eee !important;
}
/* Hover effect */
div[role="option"]:hover {
    background-color: #343a40 !important;
    color: #fff !important;
}

div[data-baseweb="select"] .css-1n6sfyn-option[aria-selected="true"] {
    background-color: #343a40 !important;
    color: #fff !important;
}
/* Label of the Selectbox */
label {
    color: #eee !important;
}

.stTabs [data-baseweb="tab-list"] {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    white-space: nowrap;
    scrollbar-width: thin;
    scrollbar-color: #555 #2c2f33;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
    height: 6px;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
    background: #2c2f33;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
    
    # --- Comparison Tool ---
    # DataFrame with capitals data
    df_aqi = pd.DataFrame(aqi)

    capitals = get_capitals()

    df_capitals = pd.DataFrame(capitals)[["country", "continent"]]

    # merge dataframes
    df = pd.merge(df_aqi, df_capitals, on="country", how="left")

    # Comparison tool of two capitals
    st.markdown("## City Comparison Tool")
    city_options = df[df["aqi"].notnull()]["city"].unique()
    city1 = st.selectbox("Select first city", city_options, key="city1")
    city2 = st.selectbox("Select second city", city_options, key="city2")
    
    if city1 and city2 and city1 != city2:
        # loading data of both cities
        data1 = df[df["city"] == city1].iloc[0]
        data2 = df[df["city"] == city2].iloc[0]
    
        # two columns for comparison
        col1, col2 = st.columns(2)

        # data of city1
        with col1:
            st.markdown(f"**{data1['city']} ({data1['country']})**")
            st.metric("Air Pollution (AQI)", int(data1["aqi"]))
            st.caption(f"Last update: {pd.to_datetime(data1['timestamp']).strftime('%Y-%m-%d %H:%M')}")
    
        # data of city2
        with col2:
            st.markdown(f"**{data2['city']} ({data2['country']})**")
            st.metric("Air Pollution (AQI)", int(data2["aqi"]))
            st.caption(f"Last update: {pd.to_datetime(data2['timestamp']).strftime('%Y-%m-%d %H:%M')}")
    
        # displays the comparison
        diff = int(data2["aqi"]) - int(data1["aqi"])
        better_city = data1["city"] if data1["aqi"] < data2["aqi"] else data2["city"]
        aqi_diff = abs(diff)
    
        st.info(f"**{better_city}** has better air quality by **{aqi_diff} AQI** points.")

    # --- Tabs for tables ---

    st.markdown("### Air pollution ranking")

    # tab windows to categories and compare capitals
    tab1, tab2, tab3 = st.tabs(["Top 10 capitals worldwide", "Top 10 capitals by continent", "Capitals with AQI-Data"])

    with tab1:
        # Top 10 Worldwide
        option = st.selectbox(
            "Select top 10 capitals by air pollution (AQI):",
            (
                "Top 10 best capitals (low AQI)",
                "Top 10 worst capitals (high AQI)"
            )
        )
        if option == "Top 10 best capitals (low AQI)":
            top10 = df[df['aqi'].notnull()].sort_values("aqi").head(10)
        else:
            top10 = df[df['aqi'].notnull()].sort_values("aqi", ascending=False).head(10)

        top10_table = top10[["city", "country", "aqi", "timestamp"]].rename(
            columns={"city": "Capital", "country": "Countries", "aqi": "Air pollution (AQI)", "timestamp" : "Timestamp"}
        )
        top10_table.insert(0, "Rank", range(1, len(top10_table) + 1))
        top10_table["Air pollution (AQI)"] = top10_table["Air pollution (AQI)"].astype(int)
        top10_table["Timestamp"] = pd.to_datetime(top10_table["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")

        st.markdown("#### Top 10 capitals by Air pollution")
        render_centered_table(top10_table, aqi_col=True)

    with tab2:
        # Top10 capitals by continent (AQI)
        st.markdown("#### Top 10 capitals by continent (AQI)")

        # Dropdown of best/worst data
        option = st.selectbox(
            "Select:",
            ("Top 10 best countries (low AQI)", "Top 10 worst countries (high AQI)")
        )

        continents = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]

        # display top10 best and worst capitals by continent
        for continent in continents:
            continent_df = df[df["continent"] == continent]

            if option == "Top 10 best countries (low AQI)":
                top_countries = continent_df[continent_df['aqi'].notnull()].sort_values("aqi").head(10)
            else:
                top_countries = continent_df[continent_df['aqi'].notnull()].sort_values("aqi", ascending=False).head(10)

            top10_table = top_countries[["country", "aqi", "timestamp"]].rename(
                columns={"country": "Countries", "aqi": "Air pollution (AQI)", "timestamp" : "Timestamp"}
            )
            top10_table.insert(0, "Rank", range(1, len(top10_table) + 1))
            top10_table["Air pollution (AQI)"] = top10_table["Air pollution (AQI)"].astype(int)
            top10_table["Timestamp"] = pd.to_datetime(top10_table["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")

            st.markdown(f"#### {option} in {continent}")
            render_centered_table(top10_table, aqi_col=True)

    with tab3:
        # Capitals with AQI-Data
        capitals_with_data = df[df['aqi'].notnull()]
        capitals_with_data_table = capitals_with_data[["city", "country", "aqi", "timestamp"]].rename(
            columns={"city": "Capital", "country": "Countries", "aqi": "Air pollution (AQI)", "timestamp" : "Timestamp"}
        )
        capitals_with_data_table.insert(0, "Rank", range(1, len(capitals_with_data_table) + 1))
        capitals_with_data_table["Air pollution (AQI)"] = capitals_with_data_table["Air pollution (AQI)"].astype(int)
        capitals_with_data_table["Timestamp"] = pd.to_datetime(capitals_with_data_table["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")

        st.markdown("#### Capital Cities with AQI Data")
        render_centered_table(capitals_with_data_table)

