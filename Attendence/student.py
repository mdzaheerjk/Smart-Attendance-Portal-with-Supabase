import streamlit as st
from supabase import Client
from .clients import create_supabase_client
from .utils import current_ist_date
from .logger import get_logger

logger = get_logger(__name__)


def show_student_panel():
    IST = None  # preserved variable name usage in old code

    # Create supabase client
    try:
        supabase: Client = create_supabase_client()
    except Exception:
        st.error("Failed to initialize Supabase client.")
        return

    st.title("🎓 Student Attendance Portal")

    try:
        open_classes_response = (
            supabase.table("classroom_settings")
            .select("class_name")
            .eq("is_open", True)
            .execute()
        )
        class_list = (
            [entry["class_name"] for entry in open_classes_response.data]
            if open_classes_response and open_classes_response.data
            else []
        )
    except Exception:
        logger.exception("Failed to fetch open classes")
        st.error("Failed to fetch classes.")
        return

    if not class_list:
        st.warning("🚫 No classrooms are currently open for attendance.")
        st.stop()

    selected_class = st.selectbox("Select Your Class", class_list)

    try:
        settings_response = (
            supabase.table("classroom_settings")
            .select("code", "daily_limit")
            .eq("class_name", selected_class)
            .execute()
        )
        settings = settings_response.data[0]
        required_code = settings["code"]
        daily_limit = settings["daily_limit"]
    except Exception:
        logger.exception("Failed to fetch class settings")
        st.error("Failed to fetch class settings.")
        return

    roll_number_raw = st.text_input("Roll Number").strip()

    # ------------------ FIX ADDED HERE ------------------
    if not roll_number_raw:
        st.info("ℹ️ Please enter your roll number to continue.")
        return

    if not roll_number_raw.isdigit():
        st.error("❌ Roll number must be a number.")
        return

    roll_number = int(roll_number_raw)
    # ------------------------------------------------------

    # fetch roll_map
    try:
        roll_map_response = (
            supabase.table("roll_map")
            .select("name")
            .eq("class_name", selected_class)
            .eq("roll_number", roll_number)
            .execute()
        )
    except Exception:
        logger.exception("Failed to fetch roll map")
        st.error("Failed to check roll map.")
        return

    if roll_map_response and roll_map_response.data:
        locked_name = roll_map_response.data[0]["name"]
        st.info(f"🔒 Name auto-filled for Roll {roll_number}: **{locked_name}**")
        name = locked_name
    else:
        name = st.text_input("Name (Will be locked after first time)").strip()

    code_input = st.text_input("Attendance Code")

    if st.button("✅ Submit Attendance"):
        today = current_ist_date()

        if code_input != required_code:
            st.error("❌ Incorrect attendance code.")
            st.stop()

        try:
            existing_response = (
                supabase.table("attendance")
                .select("*")
                .eq("class_name", selected_class)
                .eq("roll_number", roll_number)
                .eq("date", today)
                .execute()
            )
        except Exception:
            logger.exception("Failed to check existing attendance")
            st.error("Failed to check existing attendance.")
            st.stop()
            return

        if existing_response and existing_response.data:
            st.error("❌ Attendance already marked today.")
            st.stop()
            return

        try:
            attendance_today_response = (
                supabase.table("attendance")
                .select("*", count="exact")
                .eq("class_name", selected_class)
                .eq("date", today)
                .execute()
            )
            attendance_count = attendance_today_response.count or 0
        except Exception:
            logger.exception("Failed to fetch today's attendance count")
            st.error("Failed to check attendance limit.")
            st.stop()
            return

        if attendance_count >= daily_limit:
            st.warning("⚠️ Attendance limit for today has been reached.")
            st.stop()
            return

        # lock roll number if first time
        try:
            if not (roll_map_response and roll_map_response.data):
                supabase.table("roll_map").insert({
                    "class_name": selected_class,
                    "roll_number": roll_number,
                    "name": name
                }).execute()
            else:
                if roll_map_response.data[0]["name"] != name:
                    st.error("❌ Roll number already locked to a different name.")
                    st.stop()
                    return
        except Exception:
            logger.exception("Failed to lock roll map")
            st.error("Failed to lock roll number.")
            st.stop()
            return

        # submit attendance
        try:
            supabase.table("attendance").insert({
                "class_name": selected_class,
                "roll_number": roll_number,
                "name": name,
                "date": today
            }).execute()
            st.success("✅ Attendance submitted successfully!")
        except Exception:
            logger.exception("Failed to submit attendance")
            st.error("Failed to submit attendance.")
