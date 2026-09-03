# Local setup

This project is configured for Python 3.11 in `runtime.txt`, but Python 3.10 is
also a better local choice than Python 3.12 on Windows. The voice attendance
dependency `webrtcvad` often fails on Windows with Python 3.12 unless Microsoft
C++ Build Tools is installed.

## Recommended Windows setup

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Optional voice attendance:

```powershell
pip install -r requirements-voice.txt
```

## Supabase secrets

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in
your own Supabase values:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```

Run the app:

```powershell
streamlit run app.py
```

## If you stay on Python 3.12

Install Microsoft C++ Build Tools, then retry:

```powershell
pip install -r requirements-voice.txt
```
