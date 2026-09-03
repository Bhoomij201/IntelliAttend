import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time

@st.dialog("Enroll in Subject")
def enroll_dialog(prefill_code=None):
    st.write('Enter the subject code provided by your teacher to enroll')
    join_code = st.text_input(
        'Subject Code',
        placeholder='Eg. CS101',
        value=prefill_code or ""
    )

    if st.button('Enroll now', type='primary', width='stretch'):
        if join_code:
            res = (
                supabase.table('subjects')
                .select('subject_id, name, subject_code, section')
                .eq('subject_code', join_code)
                .order('subject_id', desc=True)
                .execute()
            )
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data['student_id']
                check = (
                    supabase.table('subject_students')
                    .select('*')
                    .eq('subject_id', subject['subject_id'])
                    .eq('student_id', student_id)
                    .execute()
                )
                if check.data:
                    st.warning('You are already enrolled in this program')
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.success(f"Successfully enrolled in {subject['name']}")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error('Invalid subject code')
        else:
            st.warning('Please enter a subject code')