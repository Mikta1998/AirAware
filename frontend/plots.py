import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import joblib

from backend.data.new_database import PostgresDB

def model_filename(city):
    return f"{city}_prophet.pkl"

def predict_aqi_for_city_and_time_from_model(city: str, target_timestamp: pd.Timestamp):
    model_path = f"backend/models/saved_models/{model_filename(city)}"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model for {city} exists. Please train a model first.")
    model = joblib.load(model_path)
    future = pd.DataFrame({'ds': [target_timestamp]})
    forecast = model.predict(future)
    pred = forecast.iloc[0]
    return pred['ds'], pred['yhat']

def show_aqi_plots():
    st.title("📊 AQI-Time-series-analytics & Prediction")

    db = PostgresDB()
    entries = db.get_all_aqi()
    if not entries:
        st.warning("The database is empty.")
        return

    df = pd.DataFrame(entries, columns=["id", "country", "city", "lat", "lon", "aqi", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    countries = sorted(df["country"].unique())
    selected_country = st.selectbox("Choose a country", countries)

    cities = sorted(df[df["country"] == selected_country]["city"].unique())
    selected_city = st.selectbox("Stadt wählen", cities)

    # categories for the time series plots
    time_options = {
        "Letzte 24 Stunden": timedelta(days=1),
        "Letzte 7 Tage": timedelta(days=7),
        "Letzte 30 Tage": timedelta(days=30),
    }
    selected_period_label = st.selectbox("Choose a timestamp", list(time_options.keys()))
    selected_period = time_options[selected_period_label]

    time_threshold = datetime.utcnow() - selected_period
    df_filtered = df[
        (df["country"] == selected_country) &
        (df["city"] == selected_city) &
        (df["timestamp"] >= time_threshold)
    ].sort_values("timestamp")

    if df_filtered.empty:
        st.warning(f"No data for {selected_city} at timestamp {selected_period_label}.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df_filtered["timestamp"], df_filtered["aqi"], marker='o', linestyle='-')
        ax.set_title(f"AQI in {selected_city}, {selected_country} ({selected_period_label})")
        ax.set_xlabel("Zeit")
        ax.set_ylabel("AQI")
        ax.grid(True)
        st.pyplot(fig, use_container_width=True)

    st.markdown("---")
    st.header("🔮 AQI-Prediction")

    # allows only future date (first: tomorrow)
    min_date = (datetime.utcnow() + timedelta(days=1)).date()
    max_date = (datetime.utcnow() + timedelta(days=7)).date()
    vorhersage_datum = st.date_input("Choose a prediction date", value=min_date, min_value=min_date, max_value=max_date)
    vorhersage_stunde = st.slider("Choose a time", 0, 23, 12)
    target_timestamp = pd.Timestamp.combine(vorhersage_datum, time(hour=vorhersage_stunde))

    if st.button("Show prediction"):
        try:
            pred_time, pred_aqi = predict_aqi_for_city_and_time_from_model(
                selected_city,
                target_timestamp=target_timestamp
            )
            st.success(f"Prediction for {selected_city} at {pred_time.strftime('%Y-%m-%d %H:%M')}: AQI ≈ {int(pred_aqi)}")
        except Exception as e:
            st.error(f"Prediction did not work: {e}")
