import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Service role for admin bypass

# In production, ensure these are set
if not SUPABASE_URL or not SUPABASE_KEY:
    # We will instantiate a dummy client or raise error depending on context
    # Assuming the user will replace them before running.
    print("Warning: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    supabase = None
    print(f"Error initializing Supabase client: {e}")
