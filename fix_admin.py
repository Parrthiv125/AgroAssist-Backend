import asyncio
from database import supabase
from auth import get_password_hash

async def fix_admin_password():
    new_hash = get_password_hash("admin123")
    print(f"Executing update with new hash: {new_hash}")
    # Update the admin user directly
    try:
        response = supabase.table("users").update({"password_hash": new_hash}).eq("email", "admin@agroassist.com").execute()
        print("Successfully updated admin password. Response:", response)
    except Exception as e:
        print("Error updating password:", e)

if __name__ == "__main__":
    asyncio.run(fix_admin_password())
