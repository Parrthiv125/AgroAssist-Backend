from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from auth import require_role
from database import supabase
from models.schemas import ProfileUpdate, ProductOut, CartItemAdd, CartItemOut, OrderCreate, OrderOut

router = APIRouter()
farmer_required = require_role(["farmer", "admin"]) # Admin can do farmer things too usually

# --- Profile ---
@router.get("/profile", response_model=dict)
async def get_profile(user: dict = Depends(farmer_required)):
    res = supabase.table("profiles").select("*").eq("user_id", user["user_id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return res.data[0]

@router.put("/profile", response_model=dict)
async def update_profile(profile: ProfileUpdate, user: dict = Depends(farmer_required)):
    update_data = {k: v for k, v in profile.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    res = supabase.table("profiles").update(update_data).eq("user_id", user["user_id"]).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profile update failed")
    return res.data[0]

# --- Products (Marketplace) ---
@router.get("/products", response_model=List[ProductOut])
async def get_products():
    res = supabase.table("products").select("*").execute()
    return res.data

@router.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):
    res = supabase.table("products").select("*").eq("id", product_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return res.data[0]

# --- Cart ---
@router.get("/cart", response_model=List[CartItemOut])
async def get_cart(user: dict = Depends(farmer_required)):
    res = supabase.table("cart_items").select("*, product:products(*)").eq("user_id", user["user_id"]).execute()
    return res.data

@router.post("/cart", response_model=dict)
async def add_to_cart(item: CartItemAdd, user: dict = Depends(farmer_required)):
    # Check max stock
    prod_res = supabase.table("products").select("stock").eq("id", item.product_id).execute()
    if not prod_res.data:
        raise HTTPException(status_code=404, detail="Product not found")
    if prod_res.data[0]["stock"] < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    
    # Exists in cart?
    cart_res = supabase.table("cart_items").select("*").eq("user_id", user["user_id"]).eq("product_id", item.product_id).execute()
    if cart_res.data:
        new_quantity = cart_res.data[0]["quantity"] + item.quantity
        res = supabase.table("cart_items").update({"quantity": new_quantity}).eq("id", cart_res.data[0]["id"]).execute()
    else:
        new_item = {
            "user_id": user["user_id"],
            "product_id": item.product_id,
            "quantity": item.quantity
        }
        res = supabase.table("cart_items").insert(new_item).execute()
    
    return {"message": "Item added to cart", "cart_item": res.data[0]}

@router.delete("/cart/{cart_item_id}")
async def remove_from_cart(cart_item_id: str, user: dict = Depends(farmer_required)):
    res = supabase.table("cart_items").delete().eq("id", cart_item_id).eq("user_id", user["user_id"]).execute()
    return {"message": "Item removed from cart"}

# --- Orders ---
@router.post("/orders")
async def create_order(order: OrderCreate, user: dict = Depends(farmer_required)):
    # 1. Get cart items
    cart_res = supabase.table("cart_items").select("*, product:products(*)").eq("user_id", user["user_id"]).execute()
    if not cart_res.data:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart_items = cart_res.data
    total_price = 0
    
    # 2. Verify stock and calculate total
    for item in cart_items:
        prod = item.get("product")
        if not prod or prod["stock"] < item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {prod['name']}")
        total_price += prod["price"] * item["quantity"]
    
    # 3. Create Order
    new_order = {
        "user_id": user["user_id"],
        "total_price": total_price,
        "address": order.address,
        "status": "PENDING"
    }
    order_res = supabase.table("orders").insert(new_order).execute()
    if not order_res.data:
        raise HTTPException(status_code=500, detail="Failed to create order")
    order_id = order_res.data[0]["id"]
    
    # 4. Create Order Items & Update Stock
    order_items_to_insert = []
    for item in cart_items:
        prod = item["product"]
        order_items_to_insert.append({
            "order_id": order_id,
            "product_id": prod["id"],
            "quantity": item["quantity"],
            "price": prod["price"]
        })
        # Reduce stock
        supabase.table("products").update({"stock": prod["stock"] - item["quantity"]}).eq("id", prod["id"]).execute()
        
    supabase.table("order_items").insert(order_items_to_insert).execute()
    
    # 5. Clear Cart
    supabase.table("cart_items").delete().eq("user_id", user["user_id"]).execute()
    
    return {"message": "Order placed successfully (COD)", "order_id": order_id}

@router.get("/orders")
async def get_orders(user: dict = Depends(farmer_required)):
    res = supabase.table("orders").select("*, items:order_items(*, product:products(*))").eq("user_id", user["user_id"]).order("created_at", desc=True).execute()
    return res.data

@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str, user: dict = Depends(farmer_required)):
    # 1. Fetch the order
    order_res = supabase.table("orders").select("*").eq("id", order_id).eq("user_id", user["user_id"]).execute()
    if not order_res.data:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = order_res.data[0]
    if order["status"] != "PENDING":
        raise HTTPException(status_code=400, detail="Only PENDING orders can be cancelled")
        
    # 2. Fetch order items to restock
    items_res = supabase.table("order_items").select("*").eq("order_id", order_id).execute()
    if items_res.data:
        for item in items_res.data:
            prod_res = supabase.table("products").select("stock").eq("id", item["product_id"]).execute()
            if prod_res.data:
                current_stock = prod_res.data[0]["stock"]
                supabase.table("products").update({"stock": current_stock + item["quantity"]}).eq("id", item["product_id"]).execute()
                
    # 3. Update order status
    update_res = supabase.table("orders").update({"status": "CANCELLED"}).eq("id", order_id).execute()
    if not update_res.data:
         raise HTTPException(status_code=500, detail="Failed to cancel order")
         
    return {"message": "Order cancelled successfully"}
