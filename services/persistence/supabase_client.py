import os
import logging

from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is not configured. "
        "Add it to your .env file."
    )


if not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY is not configured. "
        "Add it to your .env file."
    )


try:
    supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )
except Exception as exc:
    logging.error(
        f"Failed to initialize Supabase client: {exc}",
        exc_info=True
    )
    raise