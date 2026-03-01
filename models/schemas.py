from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    village: Optional[str] = None
    state: Optional[str] = None
    land_size: Optional[float] = None
    crop_type: Optional[str] = None
    full_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# --- Product Schemas ---
class ProductBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    category: str
    stock: int = 0
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: str
    created_at: datetime

# --- Cart Schemas ---
class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = 1

class CartItemOut(BaseModel):
    id: str
    product_id: str
    quantity: int
    product: Optional[ProductOut] = None

# --- Order Schemas ---
class OrderCreate(BaseModel):
    address: str

class OrderItemOut(BaseModel):
    id: str
    product_id: str
    quantity: int
    price: float
    product: Optional[dict] = None

class OrderOut(BaseModel):
    id: str
    user_id: str
    total_price: float
    address: str
    status: str
    created_at: datetime
    items: Optional[List[OrderItemOut]] = []

# --- Scheme Schemas ---
class SchemeBase(BaseModel):
    title: str
    description: str
    eligibility: str
    benefits: str
    state: str
    apply_link: str

class SchemeCreate(SchemeBase):
    pass

class SchemeOut(SchemeBase):
    id: str
    created_at: datetime

# --- AI Chat ---
class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

# --- Weather ---
class WeatherResponse(BaseModel):
    current: dict
    forecast: List[dict]

# --- Crop Advisory ---
class AdvisoryRequest(BaseModel):
    crop_type: str
    season: str
