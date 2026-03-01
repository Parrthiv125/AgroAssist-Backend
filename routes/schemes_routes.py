from fastapi import APIRouter
from typing import List, Optional
from database import supabase
from models.schemas import SchemeOut

router = APIRouter()

@router.get("", response_model=List[SchemeOut])
async def get_schemes(state: Optional[str] = None):
    query = supabase.table("schemes").select("*")
    if state:
        # Fetch schemes for specific state AND All India schemes
        # Note: supabase-py OR filter syntax can be tricky, doing python-side filter for simplicity 
        # or simple DB eq for specific state and All India
        res = query.execute()
        filtered = [s for s in res.data if s.get("state") == state or s.get("state") == "All India"]
        return filtered
    
    res = query.execute()
    return res.data
