from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from database import supabase
from auth import require_role
import logging

router = APIRouter()
farmer_required = require_role(["farmer", "admin"])

class CropAdvisory(BaseModel):
    id: str
    crop_name: str
    season: str
    weather_tips: str
    general_tips: str
    created_at: str

@router.get("", response_model=List[CropAdvisory])
async def get_advisories(current_user: dict = Depends(farmer_required)):
    """
    Fetches the static crop advisories based on the user's selected crop_types.
    Returns all seeded advice for crops matching the user's profile.
    """
    try:
        # 1. Fetch user's profile to get crop_type
        profile_res = supabase.table("profiles").select("crop_type").eq("user_id", current_user["user_id"]).execute()
        if not profile_res.data:
            return []
            
        crop_type_str = profile_res.data[0].get("crop_type")
        if not crop_type_str:
            return []
            
        # Parse the comma-separated string into a list and trim whitespace
        user_crops = [crop.strip() for crop in crop_type_str.split(",") if crop.strip()]
        
        if not user_crops:
            return []

        PREMADE_ADVISORIES = [
            {
                "id": "adv_wheat",
                "crop_name": "Wheat",
                "season": "Rabi",
                "weather_tips": "In dry winters, ensure light irrigation during the critical tillering and jointing stages. Late frosts can severely impact flowering, so maintain adequate soil moisture to buffer temperatures. If rainfall exceeds 50mm unexpectedly, ensure rapid drainage to prevent root rot.",
                "general_tips": "Always use certified, rust-resistant seed varieties. Apply NPK fertilizers based strictly on soil test recommendations. Top-dress with nitrogen at the first irrigation (21 days after sowing). Keep the field weed-free for the first 30-40 days using appropriate herbicides like Isoproturon.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_rice",
                "crop_name": "Rice",
                "season": "Kharif",
                "weather_tips": "Maintain 2-5 cm of continuous standing water during the transplanting phase to control weeds naturally. High humidity (above 80%) coupled with cloudy days may induce stem borer and bacterial leaf blight attacks. Drain water 10-15 days before harvesting.",
                "general_tips": "Adopt the System of Rice Intensification (SRI) for significantly higher yields with up to 30% lower water inputs. Apply zinc sulphate if the tips of older leaves turn yellow or brown. Weed management is critical in the first 20-45 days.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_maize",
                "crop_name": "Maize",
                "season": "Kharif/Rabi",
                "weather_tips": "Maize is highly sensitive to waterlogging. Ridging is essentially required in heavy rainfall regions to drain excess water securely. Moisture stress during the tasseling and silking stages (45-65 days) drastically reduces yield, so supplement irrigation if dry.",
                "general_tips": "Apply balanced zinc and nitrogen fertilization at the V6 and VT (tasseling) stages for optimum cob filling. Fall Armyworm is a major pest; monitor early whorl stages and apply neem oil or emamectin benzoate at the first sign of damage.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_cotton",
                "crop_name": "Cotton",
                "season": "Kharif",
                "weather_tips": "Avoid waterlogging during heavy monsoons by ensuring proper field drainage, as cotton roots require great aeration. Monitor for pink bollworm during dry, warm spells. Stop irrigation when 30-40% of bolls have opened.",
                "general_tips": "Maintain proper plant spacing (90x45 cm or 120x60 cm) to allow adequate sunlight and air circulation, reducing fungal infections. Nipping the terminal bud at 80-90 days encourages lateral branching and synchronous boll bursting.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_sugarcane",
                "crop_name": "Sugarcane",
                "season": "Annual",
                "weather_tips": "Pre-monsoon drought requires deep trench irrigation to sustain the crop. Earthing up is absolutely essential before heavy winds and monsoon rains arrive to prevent lodging of the tall stalks. Water demand peaks during the grand growth phase.",
                "general_tips": "Ensure timely manual weeding. Always use sett treatment (fungicide dipping) before planting to prevent devastating soil-bone diseases like red rot. Trash mulching helps conserve moisture and dramatically suppresses weeds.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_soybean",
                "crop_name": "Soybean",
                "season": "Kharif",
                "weather_tips": "Soybean needs excellent soil moisture during the critical flowering and pod development stages, but avoid prolonged saturation and stagnant water. Heavy rainfall during pod maturation can cause seed rotting.",
                "general_tips": "Seed inoculation with Rhizobium culture is non-negotiable as it dramatically improves natural nitrogen fixation. Deep summer ploughing helps expose and kill overwintering pupae of defoliating insects. Maintain a weed-free environment up to 45 days.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_mustard",
                "crop_name": "Mustard",
                "season": "Rabi",
                "weather_tips": "Monitor aggressively for aphid outbreaks during cloudy or highly humid days in winter. Delay irrigation if winter rains are forecast. Frost can damage flowers and developing pods; irrigate lightly to raise micro-climate temperature against frost.",
                "general_tips": "Sow early (October) to effectively escape peak aphid infestation. Maintain optimal row spacing (45x15 cm) to prevent moisture stress and excessive humidity in the canopy. Apply Sulphur (20-40 kg/ha) to significantly increase oil content.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_potato",
                "crop_name": "Potato",
                "season": "Rabi",
                "weather_tips": "Protect the crop against late blight during prolonged foggy, cloudy, or drizzly conditions using preventive fungicides (Mancozeb). Potatoes are highly sensitive to frost; maintain wet furrows during freezing nights.",
                "general_tips": "Perform earthing up after 30-35 days of planting to prevent tuber greening (exposure to sunlight). Cut the haulms (vines) 10-15 days before harvest to allow tuber skin to harden properly, improving storage life.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_millets",
                "crop_name": "Millets",
                "season": "Kharif/Zaid",
                "weather_tips": "Millets are highly drought-tolerant but absolutely require good drainage. Heavy continuous rains during flowering can wash away pollen and result in empty grains. Withhold irrigation during the grain-hardening stage.",
                "general_tips": "Intercropping with pulses like pigeon pea or mung bean is highly recommended for soil health. Thinning the seedlings exactly 15 days after germination reduces competition for scarce moisture. Avoid excessive nitrogen which leads to lodging and poor grain filling.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_pulses",
                "crop_name": "Pulses",
                "season": "Rabi/Kharif",
                "weather_tips": "Pulses are exceedingly sensitive to waterlogging at all stages. Avoid sowing if heavy rains are predicted within 48 hours. Provide single life-saving irrigation precisely at the pod initiation stage if the season is exceptionally dry.",
                "general_tips": "Crucially treat seeds with Trichoderma viride or Carbendazim to prevent root and stem rots. Nipping the apical buds at 35-40 days encourages lateral branching and more pods. Apply Phosphorus to boost root nodulation.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_tea",
                "crop_name": "Tea",
                "season": "Perennial",
                "weather_tips": "Prolonged droughts can severely stall sprouting. Use sprinkler irrigation if dry spells exceed 20 days. High humidity and heavy rainfall periods demand strict monitoring for blister blight and red spider mites.",
                "general_tips": "Maintain proper shade tree (e.g., silver oak) density to regulate temperatures and sunlight. Skiffing or light pruning should be scheduled precisely before the onset of the active flushing season to encourage robust new shoots.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_coffee",
                "crop_name": "Coffee",
                "season": "Perennial",
                "weather_tips": "Blossom showers (25-40mm) are vital for triggering synchronous flowering. If natural rain fails, utilize overhead irrigation immediately. Prevent water stagnation during peak monsoons which causes massive berry drop and black rot.",
                "general_tips": "Strictly regulate shade canopy before the monsoon sets in. Implement timely centering and handling of bushes to ensure aeration, which directly mitigates the dreaded Coffee Berry Borer and leaf rust outbreaks.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_fruits",
                "crop_name": "Fruits",
                "season": "Perennial",
                "weather_tips": "Sudden temperature drops can cause fruit drop. Use windbreaks to protect orchards from violent seasonal winds. Install drip irrigation to maintain constant but low-volume moisture during peak fruiting periods without causing water stress.",
                "general_tips": "Annual pruning of dead and overlapping branches is vital for sunlight penetration. Adopt integrated pest management (IPM) using fruit fly traps and neem sprays. Apply organic compost rings around the drip line before the monsoons.",
                "created_at": "2023-10-01"
            },
            {
                "id": "adv_vegetables",
                "crop_name": "Vegetables",
                "season": "Annual",
                "weather_tips": "Rainfall directly speeds up fungal growth on leafy vegetables; use raised beds to aid drainage. Heatwaves cause blossom drop in tomatoes and peppers; use shade nets (50%) to cool the micro-climate during peak summer afternoons.",
                "general_tips": "Crop rotation is the absolute best defense against soil-borne nematodes. Harvest vegetables in the cool early morning or late evening hours to preserve moisture and shelf life. Apply regular, small doses of balanced NPK through fertigation.",
                "created_at": "2023-10-01"
            }
        ]
        
        # 2. Filter the pre-built list to match the user's selected crops
        # Do a case-insensitive check
        matched_advisories = []
        user_crops_lower = [c.lower() for c in user_crops]
        
        for adv in PREMADE_ADVISORIES:
            if adv["crop_name"].lower() in user_crops_lower:
                matched_advisories.append(adv)
                
        return matched_advisories

    except Exception as e:
        logging.error(f"Error fetching crop advisories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
