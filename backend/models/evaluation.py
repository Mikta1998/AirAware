import sys
import os
import json
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.models.model import load_city_data_from_postgres
from backend.capitals_data import get_capitals

def find_time_and_target_column(df):
    for tcol in ["timestamp", "ds", "date", "datetime"]:
        if tcol in df.columns:
            time_col = tcol
            break
    else:
        raise ValueError(f"No Column is found! Column: {df.columns}")

    for ycol in ["aqi", "y", "value", "target"]:
        if ycol in df.columns:
            target_col = ycol
            break
    else:
        raise ValueError(f"No Column is found! Column: {df.columns}")

    return time_col, target_col

def evaluate_model(city_name, model_dir, results):
    model_path = model_dir / f"{city_name}_prophet.pkl"
    split_path = model_dir / f"{city_name}_split.json"
    if not (model_path.exists() and split_path.exists()):
        print(f"No model or split point is found for {city_name}, skip.")
        return

    model = joblib.load(model_path)
    with open(split_path) as f:
        split_info = json.load(f)
    split_point = pd.to_datetime(split_info["split_point"])

    df = load_city_data_from_postgres(city_name, days=30)
    try:
        time_col, target_col = find_time_and_target_column(df)
    except ValueError as e:
        print(f"{city_name}: {e}")
        return

    df[time_col] = pd.to_datetime(df[time_col])
    eval_df = df[df[time_col] >= split_point]

    if eval_df.empty:
        print(f"No evaluation data for {city_name}, skip.")
        return

    future = pd.DataFrame({'ds': eval_df[time_col]})
    forecast = model.predict(future)
    y_true = eval_df[target_col].values
    y_pred = forecast['yhat'].values

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"{city_name}: MAE = {mae:.2f}, RMSE = {rmse:.2f}")

    # results saved in evaluation_resuslts.csv
    results.append({
        "city": city_name,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2)
    })

def main():
    model_dir = Path(__file__).resolve().parent / "saved_models"
    capitals = get_capitals()
    results = []
    for city_entry in capitals:
        city_name = city_entry["city"]
        evaluate_model(city_name, model_dir, results)

    # writing results in the csv file
    results_df = pd.DataFrame(results)
    csv_path = Path(__file__).resolve().parent / "evaluation_results.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"\nResults saved in: {csv_path}")

if __name__ == "__main__":
    main()
