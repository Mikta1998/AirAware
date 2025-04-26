
def aqi_color(aqi):
    # ensure aqi is an integer if possible
    try:
        aqi = int(aqi)
    except (ValueError, TypeError):
        return "No Data", "gray"

    if aqi <= 50: return "Good", "green"
    elif aqi <= 100: return "Moderate", "yellow"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups", "orange"
    elif aqi <= 200: return "Unhealthy", "red"
    elif aqi <= 300: return "Very Unhealthy", "purple"
    return "Hazardous", "maroon"

def aqi_advice(aqi):
    if aqi <= 50:
        return "Air is clean. Great day to go outside!"
    elif aqi <= 100:
        return "Air is acceptable. Sensitive groups can still go out, but take it easy."
    elif aqi <= 150:
        return "Unhealthy for sensitive people (asthma, elderly). Limit outdoor activities."
    elif aqi <= 200:
        return "Unhealthy. Everyone should reduce prolonged outdoor exertion."
    elif aqi <= 300:
        return "Very unhealthy. Stay indoors with windows closed if possible."
    return "Hazardous. Avoid all outdoor activity. Use air purifiers if available."