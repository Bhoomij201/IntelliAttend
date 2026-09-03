import streamlit as st

st.set_page_config(
    page_title="IntelliAttend",
    page_icon="IA",
    layout="wide",
)

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

def main():
    if 'login_type' not in st.session_state:
        params = st.query_params
        url_role = params.get("role", None)
        if url_role in ['teacher', 'student']:
            st.session_state['login_type'] = url_role
        else:
            st.session_state['login_type'] = None

    # ✅ join-code ko bachao clear hone se
    join_code = st.query_params.get("join-code", None)
    if join_code:
        st.session_state['pending_join_code'] = join_code

    if st.session_state['login_type']:
        st.query_params["role"] = st.session_state['login_type']
    else:
        # ✅ sirf role clear karo, join-code nahi
        if "role" in st.query_params:
            del st.query_params["role"]

    # ✅ QR se aaya to automatically student screen pe bhejo
    if join_code and st.session_state['login_type'] is None:
        st.session_state['login_type'] = 'student'
        st.rerun()

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()

if __name__ == "__main__":
    main()
