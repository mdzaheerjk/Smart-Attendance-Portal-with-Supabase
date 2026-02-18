# Attendence/supabase_client.py
"""
Thin compatibility wrapper kept for backwards 
compatibility with existing imports.
Use Attendence.clients.create_supabase_client() 
in new code.
"""
from .clients import create_supabase_client

supabase = None
try:
    supabase = create_supabase_client()
except Exception:
    # Fail silently here -- calling code will 
    # handle exceptions when trying to use supabase
    supabase = None
