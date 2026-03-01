from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from auth import require_role
from database import supabase
from models.schemas import ProductCreate, SchemeCreate, ProductOut, SchemeOut

router = APIRouter()
admin_required = require_role(["admin"])

# --- Admin Products ---
@router.post("/products", response_model=ProductOut)
async def create_product(product: ProductCreate, user: dict = Depends(admin_required)):
    res = supabase.table("products").insert(product.dict()).execute()
    return res.data[0]

@router.put("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: str, product: ProductCreate, user: dict = Depends(admin_required)):
    update_data = {k: v for k, v in product.dict().items() if v is not None}
    res = supabase.table("products").update(update_data).eq("id", product_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return res.data[0]

@router.delete("/products/{product_id}")
async def delete_product(product_id: str, user: dict = Depends(admin_required)):
    res = supabase.table("products").delete().eq("id", product_id).execute()
    return {"message": "Product deleted successfully"}

# --- Admin Schemes ---
@router.post("/schemes", response_model=SchemeOut)
async def create_scheme(scheme: SchemeCreate, user: dict = Depends(admin_required)):
    res = supabase.table("schemes").insert(scheme.dict()).execute()
    return res.data[0]

@router.put("/schemes/{scheme_id}", response_model=SchemeOut)
async def update_scheme(scheme_id: str, scheme: SchemeCreate, user: dict = Depends(admin_required)):
    update_data = {k: v for k, v in scheme.dict().items() if v is not None}
    res = supabase.table("schemes").update(update_data).eq("id", scheme_id).execute()
    return res.data[0]

@router.delete("/schemes/{scheme_id}")
async def delete_scheme(scheme_id: str, user: dict = Depends(admin_required)):
    res = supabase.table("schemes").delete().eq("id", scheme_id).execute()
    return {"message": "Scheme deleted successfully"}

# --- Admin Orders ---
@router.get("/orders")
async def get_all_orders(user: dict = Depends(admin_required)):
    res = supabase.table("orders").select("*, items:order_items(*, product:products(*))").order("created_at", desc=True).execute()
    return res.data

@router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str, user: dict = Depends(admin_required)):
    valid_statuses = ["PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    res = supabase.table("orders").update({"status": status}).eq("id", order_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Order not found")
    return res.data[0]
