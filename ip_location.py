import streamlit as st
import requests
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from api import fetch_aqi  # function to get air quality data from WAQI API
from features.features import aqi_advice, aqi_color

@st.cache_data
def detect_city():
    '''
    This function tries to detect the user's city based on their IP address
    '''
    try:
        info = requests.get("https://ipinfo.io", timeout=3).json()  # call IP info API
        return info.get("city")  # extract city name
    except:
        return None  # return nothing if the API fails

def show_ip_location():
    '''
    This is the main function that shows the AQI based on user's location.
    '''
    st.subheader("📍 Check by My Location (Auto-detected)")

    city = detect_city()  # Get the city name based on IP

    # Initial default values if city or AQI not found
    aqi = 0
    label = "No data"
    color = "white"
    advice = "-"
    lat, lon = 20, 0  # Default coordinates if not detected

    if city:
        # Show a message with the detected city
        st.success(f"📍 Detected city: **{city}**")

        # Use that city to get the AQI data from the WAQI API
        data = fetch_aqi(city)

        if data and isinstance(data, dict):
            fetched_aqi = data.get("aqi", None)

            if fetched_aqi != "-" and fetched_aqi is not None:
                try:
                    aqi = int(fetched_aqi)  # AQI value
                    label, color = aqi_color(aqi)  # AQI category label and color
                    advice = aqi_advice(aqi)  # Health advice based on AQI
                    lat = data.get("lat", lat)  # Update coordinates if available
                    lon = data.get("lon", lon)
                except (ValueError, TypeError):
                    st.warning(f"No valid AQI data for **{city}**.")
            else:
                st.warning(f"No AQI data available for **{city}**.")
        else:
            st.error("Could not fetch AQI data for your city.")
    else:
        # If the IP-based city detection failed
        st.warning("Could not detect your city via IP.")

    # Display AQI and advice if available
    if label != "No data":
        st.markdown(f"**AQI:** {aqi}  \n"
                    f"**Air Quality:** <span style='color:{color}; font-weight:bold'>{label}</span>",
                    unsafe_allow_html=True)
        st.info(f"💡 {advice}")
    else:
        st.markdown("**AQI:** 0  \n**Air Quality:** No data")

    # Gauge chart and legend side by side
    col1, col2 = st.columns([3, 1], gap="large")

    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi,
            number={"font": {"size": 42}},  # AQI number size
            title={"text": "Air Quality Index", "font": {"size": 22}},
            gauge={
                "axis": {
                    "range": [0, 500],  # AQI range
                    "tickwidth": 2,
                    "tickcolor": "white",
                    "tickfont": {"size": 16},
                    "tickmode": "linear",
                    "tick0": 0,
                    "dtick": 50
                },
                "bar": {"color": color if label != "No data" else "gray", "thickness": 0.3},  # Bar color matches AQI status
                "steps": [  # Colored steps
                    {"range": [0, 50], "color": "green"},
                    {"range": [51, 100], "color": "yellow"},
                    {"range": [101, 150], "color": "orange"},
                    {"range": [151, 200], "color": "red"},
                    {"range": [201, 300], "color": "purple"},
                    {"range": [301, 500], "color": "maroon"},
                ],
                "threshold": {  # Arrow indicator
                    "line": {"color": color if label != "No data" else "gray", "width": 4},
                    "thickness": 0.75,
                    "value": aqi
                }
            },
            domain={"x": [0, 1], "y": [0, 1]}
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
            font={"color": "white"},
            autosize=True,
            width=800,
            height=450,
            margin={"t": 80, "b": 40, "l": 40, "r": 40},
        )

        # Plot chart without download or fullscreen tools
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        # Display AQI color guide
        st.markdown("""
        <div style='padding-top: 1rem;'>
            <strong>AQI Color Guide:</strong>
            <ul style='list-style-type: none; padding-left: 0; font-size: 0.9rem;'>
                <li><span style='color:green; font-weight: bold;'>■ 0-50:</span> Good</li>
                <li><span style='color:yellow; font-weight: bold;'>■ 51-100:</span> Moderate</li>
                <li><span style='color:orange; font-weight: bold;'>■ 101-150:</span> Unhealthy for Sensitive Groups</li>
                <li><span style='color:red; font-weight: bold;'>■ 151-200:</span> Unhealthy</li>
                <li><span style='color:purple; font-weight: bold;'>■ 201-300:</span> Very Unhealthy</li>
                <li><span style='color:maroon; font-weight: bold;'>■ 301-500:</span> Hazardous</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Location on Map")

    # Show map even if no AQI data is available
    m = folium.Map(location=[lat, lon], zoom_start=4, tiles="OpenStreetMap")
    if city and label != "No data":
        # Add marker if AQI data was found
        folium.Marker(
            [lat, lon],
            tooltip=city,
            popup=f"AQI: {aqi}",
            icon=folium.Icon(color="red" if aqi > 100 else "green")
        ).add_to(m)
    st_folium(m, width=800, height=600)