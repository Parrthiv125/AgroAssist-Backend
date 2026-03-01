import os
from dotenv import load_dotenv
from supabase import create_client, Client
import asyncio

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def update_database():
    try:
        # 1. Create crop_advisories table 
        # Since supabase python client doesn't support raw DDL easily, we'll try a raw RPC or HTTP call if needed,
        # but the easiest way is usually to execute the SQL directly via the dashboard or a REST call.
        # Alternatively, we can just use the supabase client to try and insert, and if it fails, it means the table doesn't exist.
        
        print("Note: To create the 'crop_advisories' table, please ensure the schema is updated in the Supabase Dashboard SQL Editor.")
        print("Attempting to insert seed data...")

        advisories = [
            {
                "crop_name": "Wheat",
                "season": "Rabi",
                "weather_tips": "Avoid heavy irrigation during high winds to prevent lodging. If temperature drops below 5°C, ensure light irrigation to protect from frost.",
                "general_tips": "Wheat requires well-pulverized soil. Sow seeds at 4-5 cm depth. First irrigation is critical at the Crown Root Initiation (CRI) stage, 21-25 days after sowing. Monitor closely for Yellow Rust and apply Propiconazole if spotted early."
            },
            {
                "crop_name": "Rice",
                "season": "Kharif",
                "weather_tips": "Maintain 2-3 cm of standing water during the transplanting phase. In case of heavy rainfall forecasts, ensure proper field drainage to prevent submergence issues.",
                "general_tips": "For optimal growth, apply nitrogen in 3 split doses. Keep the field weed-free for the first 45 days. Watch for Leaf Folder and Stem Borer pests; use neem-based pesticides for early control or Chlorpyriphos if infestation exceeds the economic threshold."
            },
            {
                "crop_name": "Cotton",
                "season": "Kharif",
                "weather_tips": "Dry weather is essential during the boll bursting stage to avoid rotting. Deep summer plowing is recommended to expose soil-borne pests to extreme heat.",
                "general_tips": "Sow seeds on ridges for better root aeration and water management. Regular scouting for Pink Bollworm is mandatory; install pheromone traps early in the season. Defoliants can be considered to synchronize boll bursting before harvest."
            },
            {
                "crop_name": "Sugarcane",
                "season": "Annual",
                "weather_tips": "Sugarcane requires heavy irrigation. Ensure deep watering during peak summer months. However, avoid waterlogging during the monsoon to prevent Red Rot disease.",
                "general_tips": "Plant setts treated with fungicide to ensure healthy germination. Earthing up should be done before the onset of monsoons to prevent lodging of tall canes. Trash mulching helps conserve soil moisture and suppresses weeds."
            },
            {
                "crop_name": "Maize",
                "season": "All Seasons",
                "weather_tips": "Maize is highly sensitive to waterlogging. Ensure excellent drainage, especially during the seedling and silking stages, to prevent stalk rot.",
                "general_tips": "Maize is a heavy feeder of nitrogen. Apply fertilizer in splits for maximum efficiency. Fall Armyworm is a major threat; install light traps and use Spinetoram or Emamectin Benzoate if the pest is detected in the whorls."
            }
        ]

        # Insert data
        res = supabase.table("crop_advisories").insert(advisories).execute()
        print(f"Successfully inserted {len(res.data)} static advisories.")

    except Exception as e:
        print(f"Error updating database: {e}")
        print("Make sure you run the schema.sql in Supabase Dashboard first to create the table!")

if __name__ == "__main__":
    asyncio.run(update_database())
