# Attendence/analytics.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from .clients import create_supabase_client
from .logger import get_logger

logger = get_logger(__name__)

def show_analytics_panel():
    st.subheader("📊 Attendance Analytics")

    try:
        supabase = create_supabase_client()
    except Exception:
        st.error("Failed to initialize Supabase client.")
        return

    try:
        class_list_response = supabase.table("classroom_settings").select("class_name").execute()
        class_list = [item["class_name"] for item in class_list_response.data] if class_list_response and class_list_response.data else []
    except Exception:
        logger.exception("Failed to fetch class list")
        st.error("Failed to fetch class list.")
        return

    if not class_list:
        st.warning("No classes found.")
        return

    selected_class = st.selectbox("Select Class", class_list)

    try:
        data = supabase.table("attendance").select("*").eq("class_name", selected_class).execute().data
    except Exception:
        logger.exception("Failed to fetch attendance data")
        st.error("Failed to fetch attendance data.")
        return

    if not data:
        st.warning(f"No attendance data for class '{selected_class}'.")
        return

    df = pd.DataFrame(data)
    df["status"] = "P"
    pivot_df = df.pivot_table(index=["roll_number", "name"], columns="date", values="status", aggfunc="first", fill_value="A").reset_index()
    pivot_df.columns.name = None  # Remove column grouping name

    st.dataframe(pivot_df, use_container_width="stretch")

    date_cols = pivot_df.columns[2:]
    pivot_df["Present_Count"] = pivot_df[date_cols].apply(lambda row: sum(val == "P" for val in row), axis=1)
    pivot_df["Attendance %"] = (pivot_df["Present_Count"] / len(date_cols) * 100).round(2)

    st.subheader("📈 Attendance Count (Top 30)")
    top_df = pivot_df[["name", "Present_Count"]].nlargest(30, "Present_Count").set_index("name")
    st.bar_chart(top_df)

    st.subheader("🏆 Top 3 Students")
    st.table(pivot_df.sort_values("Attendance %", ascending=False).head(3)[["name", "Present_Count", "Attendance %"]])

    st.subheader("⚠️ Bottom 3 Students")
    st.table(pivot_df.sort_values("Attendance %").head(3)[["name", "Present_Count", "Attendance %"]])

    st.subheader("🎯 Filter by Attendance Range")
    min_val, max_val = float(pivot_df["Attendance %"].min()), float(pivot_df["Attendance %"].max())
    selected_range = st.slider("Select range (%)", 0.0, 100.0, (min_val, max_val), step=1.0)

    filtered = pivot_df[(pivot_df["Attendance %"] >= selected_range[0]) & (pivot_df["Attendance %"] <= selected_range[1])]
    st.markdown(f"Showing **{len(filtered)}** students between **{selected_range[0]}%** and **{selected_range[1]}%**")
    st.dataframe(filtered[["name", "roll_number", "Present_Count", "Attendance %"]], use_container_width="stretch")

    # Pie Chart Summary
    try:
        flattened = pivot_df[date_cols].values.flatten()
        present = sum(val == "P" for val in flattened)
        absent = sum(val != "P" for val in flattened)

        fig, ax = plt.subplots()
        ax.pie([present, absent], labels=["Present", "Absent"], autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    except Exception:
        logger.exception("Failed to render pie chart")
        st.error("Failed to render summary chart.")
