from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash = pwd_context.hash("admin123")

print("\n--- RUN THIS SQL IN SUPABASE SQL EDITOR ---")
print(f"UPDATE public.users SET password_hash = '{hash}' WHERE email = 'admin@agroassist.com';")
print("-------------------------------------------\n")
