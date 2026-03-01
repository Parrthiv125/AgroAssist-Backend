from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from auth import get_password_hash, verify_password, create_access_token
from database import supabase
from models.schemas import UserRegister, UserLogin, TokenData
from datetime import timedelta
import logging

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    # Check if user exists
    res = supabase.table("users").select("id").eq("email", user.email).execute()
    if len(res.data) > 0:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "password_hash": hashed_password,
        "role": "farmer"
    }

    try:
        response = supabase.table("users").insert(new_user).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        user_data = response.data[0]
        # Create empty profile
        supabase.table("profiles").insert({"user_id": user_data['id']}).execute()
        
        return {"message": "User registered successfully"}
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/login", response_model=TokenData)
async def login(user: UserLogin):
    res = supabase.table("users").select("*").eq("email", user.email).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_db = res.data[0]
    if not verify_password(user.password, user_db["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": str(user_db["id"]), "role": user_db["role"]}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user_db["role"],
        "user_id": str(user_db["id"])
    }
