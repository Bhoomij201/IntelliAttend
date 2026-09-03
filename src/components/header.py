import streamlit as st


def header_home():
    st.markdown("""
        <div class="intelli-brand intelli-brand-home">
            <div class="intelli-mark">IA</div>
            <div>
                <h1>IntelliAttend</h1>
                <p class="intelli-tagline">
                    A calm, intelligent attendance workspace for face recognition,
                    voice verification, QR enrollment, and course records.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def header_dashboard():
    st.markdown("""
        <div class="intelli-brand" style="justify-content:flex-start;">
            <div class="intelli-mark">IA</div>
            <h2 style="margin:0;">IntelliAttend</h2>
        </div>
    """, unsafe_allow_html=True)
