import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card

from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_attendance_for_teacher
)

from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog

import numpy as np
from datetime import datetime
import pandas as pd
import altair as alt
import html

from src.database.config import supabase
from src.components.dialog_voice_attendance import voice_attendance_dialog


def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()

    elif (
        'teacher_login_type' not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):
        teacher_screen_login()

    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():

    teacher_data = st.session_state.teacher_data

    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='xxlarge'
    )

    with c1:
        header_dashboard()

    with c2:

        st.subheader(
            f"""Welcome, {teacher_data['name']} """
        )

        if st.button(
            "Logout",
            type='secondary',
            key='loginbackbtn',
            shortcut="control+backspace"
        ):

            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'

    tab1, tab2, tab3, tab4 = st.columns(4)

    with tab1:

        type1 = (
            "primary"
            if st.session_state.current_teacher_tab
            == 'take_attendance'
            else "tertiary"
        )

        if st.button(
            'Take Attendance',
            type=type1,
            width='stretch',
            icon=':material/ar_on_you:'
        ):

            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:

        type2 = (
            "primary"
            if st.session_state.current_teacher_tab
            == 'manage_subjects'
            else "tertiary"
        )

        if st.button(
            'Manage Subjects',
            type=type2,
            width='stretch',
            icon=':material/book_ribbon:'
        ):

            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:

        type3 = (
            "primary"
            if st.session_state.current_teacher_tab
            == 'attendance_records'
            else "tertiary"
        )

        if st.button(
            'Attendance Records',
            type=type3,
            width='stretch',
            icon=':material/cards_stack:'
        ):

            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    with tab4:

        type4 = (
            "primary"
            if st.session_state.current_teacher_tab
            == 'analytics'
            else "tertiary"
        )

        if st.button(
            'Analytics',
            type=type4,
            width='stretch',
            icon=':material/query_stats:'
        ):

            st.session_state.current_teacher_tab = 'analytics'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()

    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()

    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    if st.session_state.current_teacher_tab == "analytics":
        teacher_tab_analytics()

    footer_dashboard()


def teacher_tab_take_attendance():

    teacher_id = st.session_state.teacher_data['teacher_id']

    st.header('Take AI Attendance')

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning(
            'You havent created any subjects yet! Please create one to begin!'
        )
        return

    subject_options = {
        f"{s['name']} ({s['subject_code']}) - {s['section']}":
        s['subject_id']
        for s in subjects
    }

    col1, col2 = st.columns(
        [3, 1],
        vertical_alignment='bottom'
    )

    with col1:

        selected_subject_label = st.selectbox(
            'Select Subject',
            options=list(subject_options.keys())
        )

    with col2:

        if st.button(
            'Add Photos',
            type='primary',
            icon=':material/photo_prints:',
            width='stretch'
        ):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:

        st.header('Added Photos')

        gallery_cols = st.columns(4)

        for idx, img in enumerate(
            st.session_state.attendance_images
        ):

            with gallery_cols[idx % 4]:

                st.image(
                    img,
                    width='stretch',
                    caption=f'Photo {idx+1}'
                )

    has_photos = bool(
        st.session_state.attendance_images
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            'Clear all photos',
            width='stretch',
            type='tertiary',
            icon=':material/delete:',
            disabled=not has_photos
        ):

            st.session_state.attendance_images = []
            st.rerun()

    with c2:

        if st.button(
            'Run Face Analysis',
            width='stretch',
            type='secondary',
            icon=':material/analytics:',
            disabled=not has_photos
        ):

            with st.spinner(
                'Deep scanning classroom photos...'
            ):

                all_detected_ids = {}

                for idx, img in enumerate(
                    st.session_state.attendance_images
                ):

                    img_np = np.array(
                        img.convert('RGB')
                    )

                    detected, _, _ = predict_attendance(
                        img_np
                    )

                    if detected:

                        for sid in detected.keys():

                            student_id = int(sid)

                            all_detected_ids.setdefault(
                                student_id,
                                []
                            ).append(f"Photo {idx+1}")

                enrolled_res = (
                    supabase.table('subject_students')
                    .select("*, students(*)")
                    .eq('subject_id', selected_subject_id)
                    .execute()
                )

                enrolled_students = enrolled_res.data

                if not enrolled_students:

                    st.warning(
                        'No students enrolled in this course'
                    )

                else:

                    results = []
                    attendance_to_log = []

                    current_timestamp = (
                        datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        )
                    )

                    for node in enrolled_students:

                        student = node['students']

                        sources = all_detected_ids.get(
                            int(student['student_id']),
                            []
                        )

                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources)
                            if is_present else "-",
                            "Status": "✅ Present"
                            if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(
                        pd.DataFrame(results),
                        attendance_to_log
                    )

    with c3:

        if st.button(
            'Use Voice Attendance',
            type='primary',
            width='stretch',
            icon=':material/mic:'
        ):

            voice_attendance_dialog(
                selected_subject_id
            )


def teacher_tab_manage_subjects():

    teacher_id = st.session_state.teacher_data['teacher_id']

    col1, col2 = st.columns(2)

    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:

        if st.button(
            'Create New Subject',
            width='stretch'
        ):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)

    if subjects:

        for sub in subjects:

            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]

            def share_btn(sub=sub):

                if st.button(
                    f"Share Code: {sub['name']}",
                    key=f"share_{sub['subject_id']}",
                    icon=":material/share:"
                ):

                    share_subject_dialog(
                        sub['name'],
                        sub['subject_code']
                    )

                st.space()

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn
            )

    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")


def teacher_tab_attendance_records():

    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return

    data = []

    for r in records:

        ts = r.get('timestamp')

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(
            ['ts_group', 'Time', 'Subject', 'Subject Code']
        )
        .agg(
            Present_Count=('is_present', 'sum'),
            Total_Count=('is_present', 'count')
        )
        .reset_index()
    )

    summary['Attendance Stats'] = (
        "✅ "
        + summary['Present_Count'].astype(str)
        + " / "
        + summary['Total_Count'].astype(str)
        + ' Students'
    )

    display_df = (
        summary.sort_values(
            by='ts_group',
            ascending=False
        )[
            ['Time', 'Subject', 'Subject Code', 'Attendance Stats']
        ]
    )

    _render_light_table(display_df)

    detail_df = _attendance_dataframe(records)
    export_df = detail_df.copy()
    export_df['Time'] = export_df['timestamp'].apply(
        lambda value: value.strftime("%Y-%m-%d %I:%M %p") if pd.notna(value) else "N/A"
    )
    export_df['Status'] = export_df['is_present'].apply(
        lambda value: 'Present' if value else 'Absent'
    )
    export_df = export_df.rename(columns={
        'student': 'Student',
        'student_id': 'Student ID',
        'subject': 'Subject',
        'subject_code': 'Subject Code',
        'section': 'Section',
        'session': 'Session',
    })[
        ['Time', 'Session', 'Subject', 'Subject Code', 'Section', 'Student', 'Student ID', 'Status']
    ]

    st.divider()
    st.subheader('Export Attendance')

    export_col1, export_col2 = st.columns(2)
    with export_col1:
        st.download_button(
            'Download CSV Report',
            data=export_df.to_csv(index=False).encode('utf-8'),
            file_name=f"intelliattend_records_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime='text/csv',
            width='stretch',
            icon=':material/download:',
        )

    with export_col2:
        st.download_button(
            'Download PDF Report',
            data=_build_attendance_pdf(export_df),
            file_name=f"intelliattend_records_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime='application/pdf',
            width='stretch',
            icon=':material/picture_as_pdf:',
        )


def _attendance_dataframe(records):
    rows = []

    for record in records:
        ts = record.get('timestamp')
        subject = record.get('subjects') or {}
        student = record.get('students') or {}

        try:
            session_time = datetime.fromisoformat(str(ts).replace("Z", "+00:00")) if ts else None
        except ValueError:
            session_time = None

        rows.append({
            "timestamp": session_time,
            "session": str(ts).split(".")[0] if ts else "Unknown",
            "date": session_time.date() if session_time else None,
            "subject_id": record.get('subject_id'),
            "subject": subject.get('name', 'Unknown'),
            "subject_code": subject.get('subject_code', 'Unknown'),
            "section": subject.get('section', 'Unknown'),
            "student_id": record.get('student_id'),
            "student": student.get('name', f"Student {record.get('student_id')}"),
            "is_present": bool(record.get('is_present', False)),
        })

    return pd.DataFrame(rows)


def _render_light_table(df):
    if df.empty:
        st.info('No records to display.')
        return

    headers = "".join(
        f'<th>{html.escape(str(column))}</th>'
        for column in df.columns
    )
    rows = []
    for _, row in df.iterrows():
        cells = "".join(
            f'<td>{html.escape(str(value))}</td>'
            for value in row
        )
        rows.append(f"<tr>{cells}</tr>")

    st.markdown(
        (
            '<div style="overflow-x:auto;border:1px solid #d8c7ac;'
            'border-radius:8px;background:#fffaf1;">'
            '<table style="width:100%;border-collapse:collapse;color:#2f2a24;">'
            '<thead><tr style="background:#efe3cf;">'
            f'{headers}'
            '</tr></thead>'
            '<tbody>'
            f'{"".join(rows)}'
            '</tbody></table></div>'
            '<style>'
            'table th{padding:12px;text-align:left;border-bottom:1px solid #d8c7ac;'
            'font-weight:700;color:#2f2a24;}'
            'table td{padding:12px;border-bottom:1px solid #eadcc8;color:#2f2a24;}'
            'table tr:last-child td{border-bottom:none;}'
            '</style>'
        ),
        unsafe_allow_html=True,
    )


def _pdf_escape(value):
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf_page(lines):
    stream_lines = ["BT", "/F1 10 Tf", "50 780 Td", "14 TL"]
    for line in lines:
        stream_lines.append(f"({_pdf_escape(line[:110])}) Tj")
        stream_lines.append("T*")
    stream_lines.append("ET")
    return "\n".join(stream_lines)


def _build_attendance_pdf(export_df):
    lines = [
        "IntelliAttend Attendance Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}",
        "",
    ]

    if export_df.empty:
        lines.append("No attendance records available.")
    else:
        for _, row in export_df.iterrows():
            lines.append(
                f"{row['Time']} | {row['Subject']} ({row['Subject Code']}) | "
                f"{row['Student']} [{row['Student ID']}] | {row['Status']}"
            )

    pages = [lines[i:i + 48] for i in range(0, len(lines), 48)]
    if not pages:
        pages = [["IntelliAttend Attendance Report", "No records available."]]

    objects = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")

    page_refs = " ".join(f"{3 + idx * 2} 0 R" for idx in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{page_refs}] /Count {len(pages)} >>")

    for idx, page_lines in enumerate(pages):
        page_obj_id = 3 + idx * 2
        content_obj_id = page_obj_id + 1
        objects.append(
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {3 + len(pages) * 2} 0 R >> >> "
            f"/Contents {content_obj_id} 0 R >>"
        )
        content = _build_pdf_page(page_lines)
        objects.append(f"<< /Length {len(content.encode('latin-1', errors='replace'))} >>\nstream\n{content}\nendstream")

    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf = ["%PDF-1.4\n"]
    offsets = [0]
    for obj_id, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode('latin-1', errors='replace')) for part in pdf))
        pdf.append(f"{obj_id} 0 obj\n{obj}\nendobj\n")

    xref_offset = sum(len(part.encode('latin-1', errors='replace')) for part in pdf)
    pdf.append(f"xref\n0 {len(objects) + 1}\n")
    pdf.append("0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.append(f"{offset:010d} 00000 n \n")
    pdf.append(
        "trailer\n"
        f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        "startxref\n"
        f"{xref_offset}\n"
        "%%EOF"
    )

    return "".join(pdf).encode('latin-1', errors='replace')


def _metric_card(label, value, helper):
    st.markdown(
        (
            '<div style="background:#fffaf1;border:1px solid #d8c7ac;'
            'border-radius:8px;padding:18px 20px;box-shadow:0 10px 28px '
            'rgba(54,48,39,0.06);">'
            f'<p style="margin:0 0 6px;color:#6f6659;font-weight:650;">{label}</p>'
            f'<h2 style="margin:0;color:#2f2a24;font-size:2rem;">{value}</h2>'
            f'<p style="margin:6px 0 0;color:#7a7063;font-size:0.9rem;">{helper}</p>'
            '</div>'
        ),
        unsafe_allow_html=True
    )


def teacher_tab_analytics():
    st.header('Analytics Dashboard')

    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info('No attendance records yet. Take attendance once to see analytics here.')
        return

    df = _attendance_dataframe(records)

    if df.empty:
        st.info('No attendance records available for analytics.')
        return

    subjects = sorted(df['subject'].dropna().unique().tolist())
    filter_col1, filter_col2 = st.columns([2, 1])

    with filter_col1:
        selected_subjects = st.multiselect(
            'Filter by subject',
            options=subjects,
            default=subjects,
        )

    with filter_col2:
        status_filter = st.selectbox(
            'Attendance status',
            options=['All', 'Present only', 'Absent only'],
        )

    filtered = df[df['subject'].isin(selected_subjects)] if selected_subjects else df.iloc[0:0]

    if status_filter == 'Present only':
        filtered = filtered[filtered['is_present']]
    elif status_filter == 'Absent only':
        filtered = filtered[~filtered['is_present']]

    if filtered.empty:
        st.warning('No records match the selected filters.')
        return

    total_logs = len(filtered)
    total_sessions = filtered['session'].nunique()
    present_count = int(filtered['is_present'].sum())
    attendance_rate = round((present_count / total_logs) * 100, 1) if total_logs else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _metric_card('Attendance Rate', f'{attendance_rate}%', 'Present records in current filter')
    with k2:
        _metric_card('Sessions', total_sessions, 'Unique attendance runs')
    with k3:
        _metric_card('Present Marks', present_count, 'Total present entries')
    with k4:
        _metric_card('Total Records', total_logs, 'Present plus absent entries')

    st.divider()

    subject_summary = (
        filtered.groupby(['subject', 'subject_code'], as_index=False)
        .agg(
            total=('is_present', 'count'),
            present=('is_present', 'sum'),
        )
    )
    subject_summary['absent'] = subject_summary['total'] - subject_summary['present']
    subject_summary['attendance_percent'] = (
        subject_summary['present'] / subject_summary['total'] * 100
    ).round(1)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader('Subject Attendance Percentage')
        subject_chart = (
            alt.Chart(subject_summary)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X('subject:N', title='Subject', sort='-y'),
                y=alt.Y('attendance_percent:Q', title='Attendance %', scale=alt.Scale(domain=[0, 100])),
                color=alt.value('#596f62'),
                tooltip=[
                    alt.Tooltip('subject:N', title='Subject'),
                    alt.Tooltip('subject_code:N', title='Code'),
                    alt.Tooltip('attendance_percent:Q', title='Attendance %'),
                    alt.Tooltip('present:Q', title='Present'),
                    alt.Tooltip('total:Q', title='Total'),
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(subject_chart, width='stretch')

    with chart_col2:
        st.subheader('Present vs Absent')
        stacked = subject_summary.melt(
            id_vars=['subject'],
            value_vars=['present', 'absent'],
            var_name='status',
            value_name='count',
        )
        stacked_chart = (
            alt.Chart(stacked)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X('subject:N', title='Subject'),
                y=alt.Y('count:Q', title='Records'),
                color=alt.Color(
                    'status:N',
                    title='Status',
                    scale=alt.Scale(
                        domain=['present', 'absent'],
                        range=['#596f62', '#a7624b'],
                    ),
                ),
                tooltip=['subject:N', 'status:N', 'count:Q'],
            )
            .properties(height=320)
        )
        st.altair_chart(stacked_chart, width='stretch')

    st.subheader('Attendance Trend by Session')
    session_summary = (
        filtered.groupby(['session', 'timestamp', 'subject'], as_index=False)
        .agg(total=('is_present', 'count'), present=('is_present', 'sum'))
    )
    session_summary['attendance_percent'] = (
        session_summary['present'] / session_summary['total'] * 100
    ).round(1)
    session_summary = session_summary.sort_values('timestamp')

    trend_chart = (
        alt.Chart(session_summary)
        .mark_line(point=True)
        .encode(
            x=alt.X('timestamp:T', title='Session Time'),
            y=alt.Y('attendance_percent:Q', title='Attendance %', scale=alt.Scale(domain=[0, 100])),
            color=alt.Color('subject:N', title='Subject'),
            tooltip=[
                alt.Tooltip('subject:N', title='Subject'),
                alt.Tooltip('session:N', title='Session'),
                alt.Tooltip('attendance_percent:Q', title='Attendance %'),
                alt.Tooltip('present:Q', title='Present'),
                alt.Tooltip('total:Q', title='Total'),
            ],
        )
        .properties(height=340)
    )
    st.altair_chart(trend_chart, width='stretch')

    st.subheader('Student Attendance Summary')
    student_summary = (
        filtered.groupby(['student', 'student_id', 'subject'], as_index=False)
        .agg(total=('is_present', 'count'), present=('is_present', 'sum'))
    )
    student_summary['Attendance %'] = (
        student_summary['present'] / student_summary['total'] * 100
    ).round(1)
    student_summary = student_summary.rename(columns={
        'student': 'Student',
        'subject': 'Subject',
        'present': 'Present',
        'total': 'Total',
    })
    student_summary['Status'] = student_summary['Attendance %'].apply(
        lambda value: 'Needs attention' if value < 75 else 'On track'
    )

    st.dataframe(
        student_summary[
            ['Student', 'Subject', 'Present', 'Total', 'Attendance %', 'Status']
        ].sort_values(['Attendance %', 'Student']),
        width='stretch',
        hide_index=True,
    )


def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():
    c1, c2 = st.columns([4, 1], vertical_alignment='top', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button(
            "Home",
            type='tertiary',
            key='teacher_login_home_btn',
            icon=':material/home:',
            width='stretch'
        ):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
    

def teacher_screen_register():
    c1, c2 = st.columns([4, 1], vertical_alignment='top', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button(
            "Home",
            type='tertiary',
            key='teacher_register_home_btn',
            icon=':material/home:',
            width='stretch'
        ):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()
