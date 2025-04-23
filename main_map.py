import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import json
from capitals_data import get_capitals
from api import dummy_data, fetch_and_store_aqi_for_all_countries, save_dummy_data

def get_aqi_color(aqi):
    if aqi is None:
        return "#cccccc"
    elif aqi <= 50:
        return "#4caf50"
    elif aqi <= 100:
        return "#ffeb3b"
    else:
        return "#f44336"

def render_centered_table(df, aqi_col=True):
    
    styles = [
        dict(selector="th.col0", props=[("text-align", "center")]),
        dict(selector="td.col0", props=[("text-align", "center")])
    ]
    if aqi_col and "Air pollution (AQI)" in df.columns:
        styles.append(dict(selector="th.col3", props=[("text-align", "center")]))
        styles.append(dict(selector="td.col3", props=[("text-align", "center")]))
    styled = df.style.set_table_styles(styles).hide(axis="index")
    st.markdown(styled.to_html(), unsafe_allow_html=True)

def show_main_map():
    st.markdown("<h4 style='margin-bottom: 0.5em;'>🌐 Worldmap: Air pollution by countries & capitals</h4>", unsafe_allow_html=True)
    
    # Legende
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

    geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    countries_geojson = requests.get(geojson_url).json()

    capitals = get_capitals()

    try:
        with open("capitals_data.json", "r") as f:
            real_aqi_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        real_aqi_data = {}

    # adding AQI values to every city
    for c in capitals:
        country = c["country"]
        country_data = real_aqi_data.get(country, {})

        aqi_value = country_data.get("aqi", None)
        timestamp = country_data.get("timestamp", None)

        c["aqi"] = int(aqi_value) if aqi_value is not None and aqi_value != "-" else None
        c["timestamp"] = timestamp

    country_aqi_map = {c["country"]: c["aqi"] for c in capitals}

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

    # builds map
    m = folium.Map(
        location=[30, 10],
        zoom_start=1.5,
        min_zoom=1.5,
        max_zoom=1.5,
        tiles="CartoDB positron",
        dragging=False,
        scrollWheelZoom=False,
        doubleClickZoom=False,
        boxZoom=False,
        touchZoom=False,
        zoom_control=False
    )

    folium.GeoJson(
        countries_geojson,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=[""], labels=False, sticky=False)
    ).add_to(m)

    # mapping the capitals on the worldmap
    for capital in capitals:
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

    # button for updating the AQI-values manually
    if st.button("🔄 Update"):
        st.info("Update can take up to five minutes.")
        with st.spinner("Load new Data..."):
            # ensure to reload the data after every saved date
            dummy_data["last_updated_date"] = "1900-01-01"
            save_dummy_data(dummy_data)
            fetch_and_store_aqi_for_all_countries()
            st.success("Updated successfully.")
            
            # this reloads all tab windows (tables)
            st.session_state.refresh = True  # trigger for reloading 
            st.rerun()  

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
/* Selectbox geschlossen */
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
/* Hover-Effekt */
div[role="option"]:hover {
    background-color: #343a40 !important;
    color: #fff !important;
}

div[data-baseweb="select"] .css-1n6sfyn-option[aria-selected="true"] {
    background-color: #343a40 !important;
    color: #fff !important;
}
/* Label der Selectbox */
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
    
    df = pd.DataFrame(capitals)

    # --- Comparison Tool ---
    st.markdown("## 🌆 City Comparison Tool")

    city_options = df[df["aqi"].notnull()]["city"].unique()
    city1 = st.selectbox("Select first city", city_options, key="city1")
    city2 = st.selectbox("Select second city", city_options, key="city2")
    
    if city1 and city2 and city1 != city2:
        data1 = df[df["city"] == city1].iloc[0]
        data2 = df[df["city"] == city2].iloc[0]
    
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{data1['city']} ({data1['country']})**")
            st.metric("Air Pollution (AQI)", int(data1["aqi"]))
            st.caption(f"Last update: {pd.to_datetime(data1['timestamp']).strftime('%Y-%m-%d %H:%M')}")
    
        with col2:
            st.markdown(f"**{data2['city']} ({data2['country']})**")
            st.metric("Air Pollution (AQI)", int(data2["aqi"]))
            st.caption(f"Last update: {pd.to_datetime(data2['timestamp']).strftime('%Y-%m-%d %H:%M')}")
    
        diff = int(data2["aqi"]) - int(data1["aqi"])
        better_city = data1["city"] if data1["aqi"] < data2["aqi"] else data2["city"]
        aqi_diff = abs(diff)
    
        st.info(f"**{better_city}** has better air quality by **{aqi_diff} AQI** points.")

    # --- Tabs for tables ---

    st.markdown("### Air pollution ranking")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Top 10 Worldwide", "Top 10 best by continent", "Top 10 worst by continent", "Capitals with AQI-Data", "No AQI-Data"])

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
        # Top 10 best by continent
        continents = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]
        for continent in continents:
            continent_df = df[df["continent"] == continent]
            best_countries = continent_df[continent_df['aqi'].notnull()].sort_values("aqi").head(10)

            top10_table = best_countries[["country", "aqi", "timestamp"]].rename(
                columns={"country": "Countries", "aqi": "Air pollution (AQI)", "timestamp" : "Timestamp"}
            )
            top10_table.insert(0, "Rank", range(1, len(top10_table) + 1))
            top10_table["Air pollution (AQI)"] = top10_table["Air pollution (AQI)"].astype(int)
            top10_table["Timestamp"] = pd.to_datetime(top10_table["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")

            st.markdown(f"#### Top 10 best countries by AQI in {continent}")
            render_centered_table(top10_table, aqi_col=True)

    with tab3:
        # Top 10 worst by continent
        for continent in continents:
            continent_df = df[df["continent"] == continent]
            worst_countries = continent_df[continent_df['aqi'].notnull()].sort_values("aqi", ascending=False).head(10)

            top10_table = worst_countries[["country", "aqi", "timestamp"]].rename(
                columns={"country": "Countries", "aqi": "Air pollution (AQI)", "timestamp" : "Timestamp"}
            )
            top10_table.insert(0, "Rank", range(1, len(top10_table) + 1))
            top10_table["Air pollution (AQI)"] = top10_table["Air pollution (AQI)"].astype(int)
            top10_table["Timestamp"] = pd.to_datetime(top10_table["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M")

            st.markdown(f"#### Top 10 worst countries by AQI in {continent}")
            render_centered_table(top10_table, aqi_col=True)

    with tab4:
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

    with tab5:
        # No AQI Data
        capitals_without_data = df[df['aqi'].isnull()]
        capitals_without_data_table = capitals_without_data[["city", "country"]].rename(
            columns={"city": "Capital", "country": "Countries"}
        )
        capitals_without_data_table.insert(0, "Rank", range(1, len(capitals_without_data_table) + 1))
        st.markdown("#### Capital Cities without AQI Data")
        render_centered_table(capitals_without_data_table, aqi_col=False)
