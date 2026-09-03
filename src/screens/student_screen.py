import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding, is_voice_available, voice_unavailable_message
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time
from src.components.dialog_enroll import enroll_dialog
from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    if 'pending_join_code' in st.session_state:
        code = st.session_state.pop('pending_join_code')
        auto_enroll_dialog(code)
        return

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}")
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()

    st.space()

    c1, c2 = st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    total_classes = sum(item['total'] for item in stats_map.values())
    total_attended = sum(item['attended'] for item in stats_map.values())
    overall_percent = round((total_attended / total_classes) * 100, 1) if total_classes else 0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric('Overall Attendance', f'{overall_percent}%')
    with m2:
        st.metric('Classes Attended', total_attended)
    with m3:
        st.metric('Total Classes', total_classes)

    st.divider()

    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        stats = stats_map.get(sid, {"total": 0, "attended": 0})
        subject_percent = round((stats['attended'] / stats['total']) * 100, 1) if stats['total'] else 0
        attendance_status = (
            'No records'
            if stats['total'] == 0
            else 'Needs attention'
            if subject_percent < 75
            else 'On track'
        )

        def unenroll_button(sid=sid, sub=sub):
            if st.button(
                "Unenroll from this course",
                type='tertiary',
                width='stretch',
                icon=':material/delete_forever:',
                key=f'unenroll_{sid}'
            ):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f"Unenrolled from {sub['name']} successfully!")
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button
            )
            st.progress(subject_percent / 100)
            st.caption(
                f"Attendance: {subject_percent}% | Status: {attendance_status}"
            )

    footer_dashboard()


def student_screen():
    style_background_dashboard()
    style_base_layout()

    params = st.query_params
    join_code = params.get("join-code", None)

    if join_code:
        st.session_state['pending_join_code'] = join_code
        st.query_params.clear()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns([4, 1], vertical_alignment='top', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button(
            "Home",
            type='tertiary',
            key='student_login_home_btn',
            icon=':material/home:',
            width='stretch'
        ):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()

    show_registration = False
    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))
        with st.spinner('AI is scanning..'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('Face not found!')
            elif num_faces > 1:
                st.warning('Multiple faces found')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)
                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! You might be a new student!')
                    show_registration = True

    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Deeksha')

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your voice for voice only attendance" if is_voice_available() else voice_unavailable_message())

            audio_widget = st.audio_input('Record a short phrase like I am present, My name is Akash.')

            # ✅ .getvalue() use karo .read() ki jagah
            if audio_widget is not None:
                bytes_data = audio_widget.getvalue()
                if bytes_data:
                    st.session_state['reg_audio'] = bytes_data
                    st.success("✅ Voice recorded! Now click Create Account.")

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None

                            if is_voice_available() and 'reg_audio' in st.session_state:
                                voice_emb = get_voice_embedding(
                                    st.session_state['reg_audio']
                                )
                                del st.session_state['reg_audio']

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)
                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile Created! Hi {new_name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("Couldn't capture your facial features for registration")
                else:
                    st.warning('Please enter your name!')

    footer_dashboard()
