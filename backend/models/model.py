import pandas as pd
from prophet import Prophet
from backend.data.new_database import PostgresDB

def load_city_data_from_postgres(city_name: str, days: int = 30):
    db = PostgresDB()
    query = """
        SELECT timestamp, aqi FROM aqi_data
        WHERE city = %s
        AND timestamp >= NOW() - INTERVAL '%s days'
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, db.conn, params=(city_name, days))
    df['ds'] = pd.to_datetime(df['timestamp'])
    df['y'] = pd.to_numeric(df['aqi'], errors='coerce')
    df = df[['ds', 'y']].dropna()
    return df

def split_train_eval(df: pd.DataFrame, eval_ratio: float = 0.2):
    df = df.sort_values('ds')
    n = int(len(df) * (1 - eval_ratio))
    train_df = df.iloc[:n]
    eval_df = df.iloc[n:]
    return train_df, eval_df

def train_and_forecast(df: pd.DataFrame, hours_ahead: int = 48):
    if df.empty or len(df) < 10:
        raise ValueError("Not enough data for prediction.")
    model = Prophet(daily_seasonality=True)
    model.fit(df)
    future = model.make_future_dataframe(periods=hours_ahead, freq='H')
    forecast = model.predict(future)
    return forecast, model

def predict_aqi_for_city_and_time(city: str, days: int, target_timestamp: pd.Timestamp):
    """
    Gibt die vorhergesagte AQI für eine Stadt zu einem bestimmten Zeitpunkt zurück.
    Returns the predicted aqi for a capital with a specific time.
    """
    df = load_city_data_from_postgres(city, days=days)
    train_df, _ = split_train_eval(df)
    hours_ahead = int((target_timestamp - train_df['ds'].max()).total_seconds() // 3600)
    if hours_ahead <= 0:
        raise ValueError("Prediction is to close to current time or to close to training data.")
    forecast, _ = train_and_forecast(train_df, hours_ahead=hours_ahead)
    
    pred = forecast.iloc[-1]
    return pred['ds'], pred['yhat']
