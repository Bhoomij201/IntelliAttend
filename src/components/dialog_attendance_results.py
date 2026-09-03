import pandas as pd
import streamlit as st

from src.database.db import create_attendance


def _status_to_present(status):
    return "present" in str(status).lower()


def _prepare_review_df(df):
    review_df = df.copy()
    if "Present" not in review_df.columns:
        review_df["Present"] = review_df.get("Status", "").apply(_status_to_present)
    return review_df[["Name", "ID", "Source", "Present"]]


def _build_logs_from_review(review_df, logs):
    updated_logs = []
    for idx, log in enumerate(logs):
        updated = dict(log)
        if idx < len(review_df):
            updated["is_present"] = bool(review_df.iloc[idx]["Present"])
        updated_logs.append(updated)
    return updated_logs


def _display_review_table(review_df):
    display_df = review_df.copy()
    display_df["Status"] = display_df["Present"].apply(
        lambda value: "Present" if value else "Absent"
    )
    return display_df[["Name", "ID", "Source", "Status"]]


def show_attendance_result(df, logs):
    st.write('Review AI results, correct mistakes manually, then save attendance.')

    review_df = _prepare_review_df(df)
    edited_df = st.data_editor(
        review_df,
        hide_index=True,
        width='stretch',
        key='attendance_review_editor',
        column_config={
            "Present": st.column_config.CheckboxColumn(
                "Present",
                help="Tick present or untick absent before saving.",
                default=False,
            )
        },
        disabled=["Name", "ID", "Source"],
    )

    present_count = int(edited_df["Present"].sum())
    total_count = len(edited_df)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Present", present_count)
    with c2:
        st.metric("Absent", total_count - present_count)
    with c3:
        rate = round((present_count / total_count) * 100, 1) if total_count else 0
        st.metric("Attendance", f"{rate}%")

    st.caption("Manual edits here are what will be saved to Supabase.")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button('Discard', width='stretch', type='tertiary'):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        corrected_csv = _display_review_table(edited_df).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Review CSV",
            data=corrected_csv,
            file_name="attendance_review.csv",
            mime="text/csv",
            width='stretch',
        )

    with col3:
        if st.button('Confirm & Save', width='stretch', type='primary'):
            try:
                corrected_logs = _build_logs_from_review(edited_df, logs)
                create_attendance(corrected_logs)
                st.toast("Attendance saved")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception:
                st.error('Sync failed!')


@st.dialog("Attendance Review")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)
