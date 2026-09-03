import bcrypt
import streamlit as st
from postgrest.exceptions import APIError

from src.database.config import supabase


def format_database_error(exc, action):
    message = getattr(exc, "message", str(exc))
    if "Invalid path specified" in message or "PGRST125" in message:
        return (
            "Supabase URL is not in the expected format. In "
            "`.streamlit/secrets.toml`, set `SUPABASE_URL` to your project "
            "base URL, like `https://your-project-ref.supabase.co`. Do not "
            "use a URL ending with `/rest/v1`."
        )
    return (
        f"Supabase error while trying to {action}. Check that your database "
        "tables and column names match this project."
    )


def _execute(query, action):
    try:
        return query.execute()
    except APIError as exc:
        st.error(format_database_error(exc, action))
        st.caption(str(exc))
        st.stop()


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def check_teacher_exists(username):
    # Check for unique username, returns false when username is already taken
    response = _execute(
        supabase.table("teachers").select("username").eq("username", username),
        "check teacher username",
    )
    return len(response.data) > 0


def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = _execute(
        supabase.table("teachers").insert(data),
        "create a teacher profile",
    )
    return response.data


def teacher_login(username, password):
    response = _execute(
        supabase.table("teachers").select("*").eq("username", username),
        "log in teacher",
    )
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None


def get_all_students():
    response = _execute(
        supabase.table('students').select("*"),
        "load students",
    )
    return response.data


def try_get_all_students():
    try:
        response = supabase.table('students').select("*").execute()
        return response.data, None
    except APIError as exc:
        return None, format_database_error(exc, "load students")


def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {'name': new_name, 'face_embedding': face_embedding, "voice_embedding": voice_embedding}
    response = _execute(
        supabase.table('students').insert(data),
        "create a student profile",
    )
    return response.data


def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = _execute(
        supabase.table("subjects").insert(data),
        "create a subject",
    )
    return response.data


def get_teacher_subjects(teacher_id):
    response = _execute(
        supabase.table('subjects')
        .select("*, subject_students(count), attendance_logs(timestamp)")
        .eq("teacher_id", teacher_id),
        "load teacher subjects",
    )
    subjects = response.data

    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions

        sub.pop('subject_student', None)
        sub.pop('attendance_logs', None)

    return subjects


def enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response = _execute(
        supabase.table('subject_students').insert(data),
        "enroll student",
    )
    return response.data


def unenroll_student_to_subject(student_id, subject_id):
    response = _execute(
        supabase.table('subject_students')
        .delete()
        .eq('student_id', student_id)
        .eq('subject_id', subject_id),
        "unenroll student",
    )
    return response.data


def get_student_subjects(student_id):
    response = _execute(
        supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id),
        "load student subjects",
    )
    return response.data


def get_student_attendance(student_id):
    response = _execute(
        supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id),
        "load student attendance",
    )
    return response.data


def create_attendance(logs):
    response = _execute(
        supabase.table('attendance_logs').insert(logs),
        "create attendance logs",
    )
    return response.data


def get_attendance_for_teacher(teacher_id):
    response = _execute(
        supabase.table('attendance_logs')
        .select("*, subjects!inner(*), students(*)")
        .eq('subjects.teacher_id', teacher_id),
        "load attendance records",
    )
    return response.data
