import streamlit as st
from supabase import Client, create_client


class MissingSupabaseClient:
    def table(self, *_args, **_kwargs):
        st.error(
            "Supabase is not configured yet. Create `.streamlit/secrets.toml` "
            "and add SUPABASE_URL plus SUPABASE_KEY before using login, "
            "enrollment, or attendance features."
        )
        st.stop()


def _load_supabase_client():
    try:
        url = _normalize_supabase_url(st.secrets["SUPABASE_URL"])
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        return MissingSupabaseClient()

    return create_client(url, key)


def _normalize_supabase_url(url):
    url = str(url).strip().rstrip("/")
    for suffix in ("/rest/v1", "/auth/v1", "/storage/v1"):
        if url.endswith(suffix):
            return url[: -len(suffix)]
    return url


supabase: Client | MissingSupabaseClient = _load_supabase_client()
