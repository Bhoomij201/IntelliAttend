import streamlit as st
from src.database.db import create_subject



@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")
    sub_id = st.text_input("Subject Code", placeholder="CS01")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")


    if st.button("Create Subject Now", type='primary', width='stretch'):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.toast("Subject Created Succesfully!")
                st.rerun()
            except Exception as e:
                if "unique_subject_code" in str(e):
                    st.error("Subject code already exists. Please use another code.")
                else:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please fill all the fields")