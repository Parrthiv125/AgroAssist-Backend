import os
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from auth import require_role
from models.schemas import ChatRequest, ChatResponse, AdvisoryRequest

router = APIRouter()
farmer_required = require_role(["farmer", "admin"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Define the model with context
system_instruction = (
    "You are an expert Indian agriculture AI assistant named AgroAssist. "
    "Respond ONLY to queries related to farming, agriculture, crops, weather impact on farming, "
    "fertilizers, schemes, and livestock. If asked about non-agricultural topics (e.g., coding, "
    "politics, generic chit-chat), politely decline and state you ONLY assist with agriculture."
)

@router.post("/ai-chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest, user: dict = Depends(farmer_required)):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")

    try:
        model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=system_instruction)
        response = model.generate_content(request.prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {str(e)}")

@router.post("/crop-advisory", response_model=ChatResponse)
async def crop_advisory(request: AdvisoryRequest, user: dict = Depends(farmer_required)):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")

    prompt = (
        f"Provide short, actionable Indian farming advisory for the crop '{request.crop_type}' "
        f"during the '{request.season}' season. Provide 1) Irrigation advice, "
        f"2) Pest alerts and prevention, and 3) Fertilizer guidance."
    )
    
    try:
        model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=system_instruction)
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI generation failed: {str(e)}")
