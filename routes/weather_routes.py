import os
import httpx
import traceback
from fastapi import APIRouter, Depends, HTTPException
from auth import require_role
from database import supabase

router = APIRouter()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
@router.get("")
async def get_weather(user: dict = Depends(require_role(["farmer", "admin"]))):
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Weather API key not configured")
        
    # Get farmer's location from profile
    res = supabase.table("profiles").select("latitude", "longitude").eq("user_id", user["user_id"]).execute()
    if not res.data or res.data[0].get("latitude") is None or res.data[0].get("longitude") is None:
        raise HTTPException(status_code=400, detail="Profile location not set. Please update your profile with coordinates.")
    
    lat = res.data[0]["latitude"]
    lon = res.data[0]["longitude"]

    # Call standard OpenWeather API instead of restricted OneCall
    current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=en"
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=en"
    
    async with httpx.AsyncClient() as client:
        try:
            # Fetch Current
            current_response = await client.get(current_url)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            # Fetch Forecast
            forecast_response = await client.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Safely get timezone offset (seconds from UTC)
            timezone_offset = forecast_data.get("city", {}).get("timezone", 0)
            
            # The 5 day / 3 hour forecast returns 40 items. Group by local date.
            import datetime
            daily_forecasts_map = {}
            for item in forecast_data.get("list", []):
                local_dt = item.get("dt") + timezone_offset
                local_date = datetime.datetime.utcfromtimestamp(local_dt).strftime('%Y-%m-%d')
                
                if local_date not in daily_forecasts_map:
                    daily_forecasts_map[local_date] = []
                daily_forecasts_map[local_date].append(item)
                
            daily_forecasts = []
            for date_str, items in daily_forecasts_map.items():
                if len(daily_forecasts) >= 7:
                    break
                    
                # Find the item closest to 14:00 (2 PM) local time for the daily high
                def get_local_hour(itm):
                    return datetime.datetime.utcfromtimestamp(itm.get("dt") + timezone_offset).hour
                
                best_item = min(items, key=lambda x: abs(get_local_hour(x) - 14))
                
                daily_forecasts.append({
                    "dt": best_item.get("dt"),
                    "temp_day": best_item.get("main", {}).get("temp"),
                    "humidity": best_item.get("main", {}).get("humidity"),
                    "wind": best_item.get("wind", {}).get("speed"),
                    "weather": (best_item.get("weather") or [{}])[0].get("description", "Unknown")
                })

            return {
                "current": {
                    "temperature": current_data.get("main", {}).get("temp"),
                    "humidity": current_data.get("main", {}).get("humidity"),
                    "wind": current_data.get("wind", {}).get("speed"),
                    "weather": (current_data.get("weather") or [{}])[0].get("description", "Unknown")
                },
                "forecast": daily_forecasts
            }
        except Exception as e:
            error_trace = traceback.format_exc()
            raise HTTPException(status_code=502, detail=f"External API failure: {repr(e)}\n\n{error_trace}")
