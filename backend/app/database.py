"""Database connection using Supabase client."""

from supabase import Client, create_client

from app.config import settings

# Supabase client for database operations
# Use service key for backend to bypass RLS
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key,
)

