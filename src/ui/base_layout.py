import streamlit as st


def style_background_home():
    st.markdown("""
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(185, 122, 87, 0.14), transparent 34%),
                    linear-gradient(135deg, #f6f0e6 0%, #ece2d0 100%) !important;
            }

            .stApp div[data-testid="stColumn"] > div {
                background: rgba(255, 252, 246, 0.92) !important;
                border: 1px solid #d8c7ac !important;
                border-radius: 8px !important;
                box-shadow: 0 18px 45px rgba(54, 48, 39, 0.08) !important;
                padding: 2rem !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: #f6f0e6 !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Inter:wght@400;500;600;700&display=swap');

            :root {
                --ia-ink: #2f2a24;
                --ia-muted: #6f6659;
                --ia-paper: #fffaf1;
                --ia-panel: #fbf6ec;
                --ia-line: #d8c7ac;
                --ia-sage: #596f62;
                --ia-sage-dark: #405449;
                --ia-clay: #a7624b;
                --ia-clay-dark: #7f4637;
                --ia-charcoal: #3a352e;
                --ia-cream: #efe3cf;
                --ia-on-dark: #fffaf1;
            }

            #MainMenu, footer, header {
                visibility: hidden;
            }

            .block-container {
                max-width: 1180px;
                padding-top: 1.25rem !important;
                padding-bottom: 2rem !important;
            }

            html, body, .stApp, [class*="css"] {
                font-family: 'Inter', sans-serif !important;
                color: var(--ia-ink) !important;
            }

            h1, h2, h3,
            h1 *, h2 *, h3 * {
                color: var(--ia-ink) !important;
                letter-spacing: 0 !important;
            }

            h1 {
                font-family: 'Libre Baskerville', serif !important;
                font-size: 3.1rem !important;
                line-height: 1.08 !important;
                margin-bottom: 0.25rem !important;
            }

            h2 {
                font-family: 'Libre Baskerville', serif !important;
                font-size: 1.9rem !important;
                line-height: 1.2 !important;
                margin-bottom: 0.25rem !important;
            }

            h3 {
                font-size: 1.25rem !important;
                font-weight: 700 !important;
            }

            p, label, span, div {
                color: inherit !important;
            }

            [data-testid="stMarkdownContainer"] p {
                color: var(--ia-muted) !important;
            }

            label,
            [data-testid="stWidgetLabel"],
            [data-testid="stWidgetLabel"] *,
            [data-testid="stTextInput"] label,
            [data-testid="stTextInput"] label * {
                color: var(--ia-ink) !important;
                font-weight: 650 !important;
            }

            div[data-testid="stMetric"],
            div[data-testid="stDataFrame"],
            div[data-testid="stForm"],
            div[data-testid="stExpander"] {
                background: var(--ia-paper);
                border-radius: 8px;
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stDataEditor"] {
                background: #fffaf1 !important;
                border: 1px solid var(--ia-line) !important;
                border-radius: 8px !important;
                overflow: hidden !important;
            }

            div[data-testid="stDataFrame"] *,
            div[data-testid="stDataEditor"] * {
                color: var(--ia-ink) !important;
            }

            div[data-testid="stDataFrame"] canvas,
            div[data-testid="stDataEditor"] canvas {
                filter: invert(0) !important;
            }

            div[data-testid="stDataFrame"] [role="grid"],
            div[data-testid="stDataEditor"] [role="grid"],
            div[data-testid="stDataFrame"] [role="row"],
            div[data-testid="stDataEditor"] [role="row"],
            div[data-testid="stDataFrame"] [role="columnheader"],
            div[data-testid="stDataEditor"] [role="columnheader"],
            div[data-testid="stDataFrame"] [role="gridcell"],
            div[data-testid="stDataEditor"] [role="gridcell"] {
                background-color: #fffaf1 !important;
                color: var(--ia-ink) !important;
                border-color: #d8c7ac !important;
            }

            div[data-testid="stDataFrame"] [role="columnheader"],
            div[data-testid="stDataEditor"] [role="columnheader"] {
                background-color: #efe3cf !important;
                color: #2f2a24 !important;
                font-weight: 700 !important;
            }

            div[data-testid="stDataFrame"] [data-testid="stElementToolbar"],
            div[data-testid="stDataEditor"] [data-testid="stElementToolbar"],
            div[data-testid="stDataFrame"] [data-testid="stToolbar"],
            div[data-testid="stDataEditor"] [data-testid="stToolbar"] {
                background: #efe3cf !important;
                border: 1px solid #d8c7ac !important;
                border-radius: 8px !important;
                box-shadow: none !important;
            }

            hr {
                border-color: var(--ia-line) !important;
            }

            input, textarea, select,
            [data-baseweb="input"],
            [data-baseweb="input"] > div,
            [data-baseweb="textarea"],
            [data-baseweb="select"] > div {
                background-color: #fffaf1 !important;
                border-radius: 6px !important;
                border-color: var(--ia-line) !important;
                color: var(--ia-ink) !important;
            }

            input::placeholder,
            textarea::placeholder {
                color: #8a8071 !important;
                opacity: 1 !important;
            }

            .stButton > button,
            button {
                border-radius: 6px !important;
                border: 1px solid transparent !important;
                box-shadow: none !important;
                font-weight: 650 !important;
                transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease !important;
            }

            .stButton > button[kind="primary"],
            button[kind="primary"] {
                background-color: var(--ia-sage) !important;
                color: var(--ia-on-dark) !important;
                border-color: var(--ia-sage) !important;
            }

            .stButton > button[kind="secondary"],
            button[kind="secondary"] {
                background-color: var(--ia-clay) !important;
                color: var(--ia-on-dark) !important;
                border-color: var(--ia-clay) !important;
            }

            .stButton > button[kind="tertiary"],
            button[kind="tertiary"] {
                background-color: #efe3cf !important;
                color: var(--ia-ink) !important;
                border-color: #cdbb9f !important;
            }

            .stButton > button *,
            button *,
            .stButton > button p,
            .stButton > button span,
            button p,
            button span {
                color: inherit !important;
                opacity: 1 !important;
                fill: currentColor !important;
            }

            .stButton > button[kind="primary"] *,
            .stButton > button[kind="secondary"] *,
            button[kind="primary"] *,
            button[kind="secondary"] * {
                color: var(--ia-on-dark) !important;
            }

            .stButton > button[kind="tertiary"] *,
            button[kind="tertiary"] * {
                color: var(--ia-ink) !important;
            }

            .stButton > button:hover,
            button:hover {
                transform: translateY(-1px);
                filter: brightness(0.96);
            }

            .stButton > button:disabled,
            button:disabled {
                background-color: #ddd0bc !important;
                border-color: #d0bea2 !important;
                color: #746b5f !important;
                opacity: 1 !important;
            }

            .stButton > button:disabled *,
            button:disabled * {
                color: #746b5f !important;
            }

            .stAlert {
                border-radius: 8px !important;
            }

            .intelli-brand {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.85rem;
            }

            .intelli-mark {
                width: 62px;
                height: 62px;
                border-radius: 8px;
                display: grid;
                place-items: center;
                background: #596f62;
                color: #fffaf1;
                font-family: 'Libre Baskerville', serif;
                font-size: 1.45rem;
                font-weight: 700;
                box-shadow: inset 0 0 0 1px rgba(255, 250, 241, 0.28);
            }

            .intelli-brand-home {
                flex-direction: column;
                margin: 2rem 0 2.2rem;
                text-align: center;
            }

            .intelli-brand-home .intelli-mark {
                width: 78px;
                height: 78px;
                font-size: 1.8rem;
                background: #3f5548;
            }

            .intelli-tagline {
                margin: 0.3rem auto 0;
                max-width: 620px;
                color: #5f564a;
                font-size: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)
