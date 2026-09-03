import streamlit as st

from src.components.header import header_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    style_background_home()
    style_base_layout()
    header_home()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            <div style="min-height:170px;">
                <p style="color:#a7624b; font-weight:700; margin-bottom:0.4rem;">Student Access</p>
                <h2 style="margin-top:0;">FaceID Check-In</h2>
                <p style="color:#6f6659;">
                    Sign in using face recognition, enroll into subjects with a
                    shared code, and track your attendance record.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button('Open Student Portal', type='primary', width='stretch'):
            st.session_state['login_type'] = 'student'
            st.rerun()

    with col2:
        st.markdown("""
            <div style="min-height:170px;">
                <p style="color:#a7624b; font-weight:700; margin-bottom:0.4rem;">Teacher Access</p>
                <h2 style="margin-top:0;">Classroom Dashboard</h2>
                <p style="color:#6f6659;">
                    Create subjects, share QR enrollment links, analyze classroom
                    photos, and review attendance sessions.
                </p>
            </div>
        """, unsafe_allow_html=True)
        if st.button('Open Teacher Portal', type='primary', width='stretch'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()
