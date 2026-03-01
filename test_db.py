import socket
import httpx
from database import supabase

# Force IPv4 resolution
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    kwargs['family'] = socket.AF_INET
    return old_getaddrinfo(*args, **kwargs)
socket.getaddrinfo = new_getaddrinfo

try:
    print("Testing connection to Supabase...")
    res = supabase.table('users').select('*').limit(1).execute()
    print("Success:", res)
except Exception as e:
    print("Failure:", e)
