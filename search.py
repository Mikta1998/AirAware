import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from api import fetch_aqi
from features.features import aqi_advice, aqi_color

# Initialize favorites safely
if "favorites" not in st.session_state:
    st.session_state.favorites = {}

def show_search():
    # CSS styling for favorite button
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        margin-top: 0.65em !important;
        border: 2px solid #FFD600 !important;
        background: transparent !important;
        color: #FFD600 !important;
        font-size: 1.6em !important;
        border-radius: 6px !important;
        font-weight: bold;
        height: 2.2em !important;
        width: 2.2em !important;
        line-height: 1;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button:hover {
        background: #23272b !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("Check Air Quality by City")

    col_search, col_fav = st.columns([5, 1])
    with col_search:
        city = st.text_input("Enter a city name", key="city_search")

    # Ensure favorites are initialized (important for first load)
    if "favorites" not in st.session_state:
        st.session_state.favorites = {}

    show_fav_btn = (
        city
        and "current_result" in st.session_state
        and isinstance(st.session_state.current_result, dict)
        and city.lower() not in [c.lower() for c in st.session_state.favorites.keys()]
    )

    with col_fav:
        if show_fav_btn:
            if st.button("☆", key="fav_btn", help="Save as favourite"):
                st.session_state.favorites[city] = st.session_state.current_result
                st.success(f"{city} saved in favourites!")

    # Initial values
    aqi = None
    label = None
    color = None
    advice = None
    lat, lon = 20, 0  # Default location

    if city:
        with st.spinner("Fetching air quality data..."):
            response = fetch_aqi(city)

        if response and isinstance(response, dict):
            aqi = response.get("aqi", None)

            if aqi == "-" or aqi is None:
                st.warning(f"No AQI data available for **{city}**.")
                st.session_state.current_result = None
                return

            try:
                aqi = int(aqi)
            except (ValueError, TypeError):
                st.warning(f"No valid AQI data for **{city}**.")
                st.session_state.current_result = None
                return

            label, color = aqi_color(aqi)
            advice = aqi_advice(aqi)
            lat = response.get("lat", lat)
            lon = response.get("lon", lon)

            st.session_state.current_result = {
                "aqi": aqi,
                "label": label,
                "color": color,
                "advice": advice,
                "lat": lat,
                "lon": lon
            }
        else:
            st.error("Could not fetch data for this city.")
            st.session_state.current_result = None
    else:
        st.session_state.current_result = None

    if aqi is not None and label:
        st.markdown(f"**AQI:** {aqi}  \n"
                    f"**Air Quality:** <span style='color:{color}; font-weight:bold'>{label}</span>",
                    unsafe_allow_html=True)
        st.info(f"{advice}")
    else:
        st.markdown("**AQI:**  \n**Air Quality:**")

    col1, col2 = st.columns([3, 1], gap="large")

    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi if aqi is not None else 0,
            number={"font": {"size": 42}},
            title={"text": "Air Quality Index", "font": {"size": 22}},
            gauge={
                "axis": {
                    "range": [0, 500],
                    "tickwidth": 2,
                    "tickcolor": "white",
                    "tickfont": {"size": 16},
                    "tickmode": "linear",
                    "tick0": 0,
                    "dtick": 50
                },
                "bar": {
                    "color": color if color else "green",  # Fill gauge bar with AQI color
                    "thickness": 0.3
                },
                "steps": [
                    {"range": [0, 50], "color": "green"},
                    {"range": [51, 100], "color": "yellow"},
                    {"range": [101, 150], "color": "orange"},
                    {"range": [151, 200], "color": "red"},
                    {"range": [201, 300], "color": "purple"},
                    {"range": [301, 500], "color": "maroon"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 4},
                    "thickness": 0.75,
                    "value": aqi if aqi is not None else 0
                }
            },
            domain={"x": [0, 1], "y": [0, 1]}
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "white"},
            autosize=True,
            width=800,
            height=450,
            margin={"t": 80, "b": 40, "l": 40, "r": 40},
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
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

    st.subheader("Location on Interactive Map")

    m = folium.Map(location=[lat, lon], zoom_start=4 if city else 2, tiles="OpenStreetMap")
    if city and aqi is not None:
        folium.Marker(
            location=[lat, lon],
            tooltip=city,
            popup=f"AQI: {aqi}",
            icon=folium.Icon(color="red" if aqi > 100 else "green")
        ).add_to(m)

    st_folium(m, width=800, height=600)