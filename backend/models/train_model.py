import sys
import os
import json
from pathlib import Path
import joblib
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.models.model import load_city_data_from_postgres, train_and_forecast
from backend.capitals_data import get_capitals

def find_time_column(df):
    for col in df.columns:
        if col.lower() in {"timestamp", "ds", "date", "datetime", "time"}:
            return col
    raise ValueError(f"No timestamp column is found! Existing columns: {df.columns}")

def main():
    hours_ahead = 7 * 24  # 7 days
    model_dir = Path(__file__).resolve().parent / "saved_models"
    model_dir.mkdir(parents=True, exist_ok=True)

    capitals = get_capitals()
    for city_entry in capitals:
        city_name = city_entry["city"]
        print(f"Train model for {city_name} ...")
        # Lade alle verfügbaren Daten
        df = load_city_data_from_postgres(city_name)
        if len(df) < 10:
            print(f"Not enough data for {city_name}, skip.")
            continue

        time_col = find_time_column(df)
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col)

        # 80/20 Split
        n = len(df)
        split_idx = int(n * 0.8)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        split_point = df[time_col].iloc[split_idx]  # timestamp of the split point

        if len(train_df) < 10:
            print(f"Not enough trainings data for {city_name}, skip.")
            continue

        forecast, model = train_and_forecast(train_df, hours_ahead=hours_ahead)
        model_path = model_dir / f"{city_name}_prophet.pkl"
        joblib.dump(model, model_path)
        # save split info
        split_info = {"split_point": str(split_point), "time_col": time_col}
        with open(model_dir / f"{city_name}_split.json", "w") as f:
            json.dump(split_info, f)
        print(f"Model and split point for {city_name} saved under {model_path}")

if __name__ == "__main__":
    main()
