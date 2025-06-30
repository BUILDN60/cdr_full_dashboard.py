import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter, defaultdict
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="📞 CDR Analyzer Toolkit", layout="wide")

# --- Title ---
st.title("📞📩 Universal CDR Analyzer")
st.markdown("Upload any supported file format (CSV, JSON, XLSX) to explore call/SMS log data dynamically.")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload a call or SMS log", type=["json", "csv", "xlsx"])

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    try:
        if file_ext == "json":
            data = json.load(uploaded_file)
            df = pd.DataFrame(data)
        elif file_ext == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_ext in ["xls", "xlsx"]:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        df.columns = df.columns.str.strip()
        st.success(f"✅ Loaded {len(df)} records and {len(df.columns)} columns.")
        st.subheader("🔍 Full Data Preview")
        st.dataframe(df, use_container_width=True)

        # --- Filter By Number and Date ---
        if "number" in df.columns and "iso_time" in df.columns:
            df["iso_time"] = pd.to_datetime(df["iso_time"], errors='coerce')
            unique_numbers = df["number"].dropna().unique().tolist()
            selected_number = st.selectbox("🔍 Select number to filter", unique_numbers)
            unique_dates = df["iso_time"].dropna().dt.date.unique()
            selected_date = st.date_input("📅 Select date to filter", min_value=min(unique_dates), max_value=max(unique_dates))

            filtered_df = df[(df["number"] == selected_number) & (df["iso_time"].dt.date == selected_date)]

            if filtered_df.empty:
                st.warning("No matching records found.")
            else:
                st.success(f"✅ Found {len(filtered_df)} records for {selected_number} on {selected_date}.")
                st.dataframe(filtered_df)

                # Call Type Analysis
                if "call_type" in filtered_df.columns:
                    st.subheader("📞 Call Type Distribution")
                    call_counts = filtered_df["call_type"].value_counts()
                    fig1, ax1 = plt.subplots()
                    ax1.pie(call_counts, labels=call_counts.index, autopct='%1.1f%%', startangle=140)
                    ax1.axis('equal')
                    st.pyplot(fig1)

                # Hourly Analysis
                st.subheader("⏱ Hourly Call Distribution")
                if not filtered_df["iso_time"].isnull().all():
                    filtered_df["hour"] = filtered_df["iso_time"].dt.hour
                    hour_counts = filtered_df["hour"].value_counts().sort_index()
                    fig2 = plt.figure(figsize=(10, 4))
                    plt.bar(hour_counts.index, hour_counts.values, color='skyblue')
                    plt.xlabel("Hour")
                    plt.ylabel("# Calls")
                    plt.title("Call Activity by Hour")
                    st.pyplot(fig2)

                # Duration Histogram
                if "duration_sec" in filtered_df.columns:
                    st.subheader("⏱ Call Duration Histogram")
                    durations = filtered_df["duration_sec"].dropna() / 60
                    fig3 = plt.figure(figsize=(10, 4))
                    plt.hist(durations, bins=10, color='orchid', edgecolor='black')
                    plt.xlabel("Duration (minutes)")
                    plt.ylabel("# Calls")
                    plt.title("Call Duration Distribution")
                    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
                    st.pyplot(fig3)

        # --- Plotly Numeric Column Visualizer ---
        st.subheader("📊 Plotly Visualizer for Numeric Columns")
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if numeric_cols:
            selected_cols = st.multiselect("Select numeric columns", numeric_cols)
            if selected_cols:
                top_n = st.slider("Top N rows", min_value=5, max_value=100, value=20)
                melted = df.head(top_n)[selected_cols].reset_index().melt(id_vars="index")
                fig = px.bar(melted, x="index", y="value", color="variable", barmode="group")
                fig.update_layout(title="Selected Numeric Columns", xaxis_title="Index", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to load or process the file: {e}")

else:
    st.info("Please upload a data file to begin analysis.")
    # --- SMS Filters ---
    st.subheader("🔎 Filter SMS by Number and Date")
    df_sms["date"] = pd.to_datetime(df_sms["iso_time"]).dt.date
    sms_unique_numbers = df_sms["number"].dropna().unique().tolist()
    sms_selected_number = st.selectbox("Select SMS number to filter", sms_unique_numbers, key="sms_number")
    sms_unique_dates = sorted(df_sms["date"].dropna().unique())
    sms_selected_date = st.date_input("Select SMS date to filter", min_value=min(sms_unique_dates), max_value=max(sms_unique_dates), key="sms_date")

    sms_filtered_df = df_sms[(df_sms["number"] == sms_selected_number) & (df_sms["date"] == sms_selected_date)]

    if not sms_filtered_df.empty:
        st.success(f"✅ Found {len(sms_filtered_df)} SMS for {sms_selected_number} on {sms_selected_date}.")

        sms_direction_count = Counter(sms_filtered_df["direction"])
        sms_hourly_distribution = sms_filtered_df['iso_time'].apply(lambda x: datetime.fromisoformat(x).hour).value_counts().sort_index()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Hourly SMS Distribution")
            fig4 = plt.figure(figsize=(8, 4))
            plt.bar(sms_hourly_distribution.index, sms_hourly_distribution.values, color='teal')
            plt.title("Hourly SMS Activity")
            plt.xlabel("Hour")
            plt.ylabel("# SMS")
            st.pyplot(fig4)

        with col2:
            st.subheader("📩 SMS Direction Pie Chart")
            fig5 = plt.figure(figsize=(6, 6))
            plt.pie(sms_direction_count.values(), labels=sms_direction_count.keys(), autopct='%1.1f%%', startangle=140)
            plt.axis("equal")
            st.pyplot(fig5)

        st.subheader("📋 Filtered SMS Records")
        st.dataframe(sms_filtered_df, use_container_width=True)

        # --- Optional: SMS Numeric Visualizer ---
        st.subheader("📊 Plotly Visualizer for SMS (if any numeric fields)")
        sms_numeric_cols = sms_filtered_df.select_dtypes(include='number').columns.tolist()
        sms_selected_cols = st.multiselect("Select numeric columns from SMS", sms_numeric_cols, key="sms_numeric")

        if sms_selected_cols:
            sms_top_n = st.slider("Top N rows to plot (SMS)", min_value=5, max_value=len(sms_filtered_df), value=20, key="sms_slider")
            sms_melted = sms_filtered_df.head(sms_top_n)[sms_selected_cols].reset_index().melt(id_vars="index")
            fig_sms = px.bar(sms_melted, x="index", y="value", color="variable", barmode="group")
            fig_sms.update_layout(title="Selected SMS Numeric Data", xaxis_title="Record Index", yaxis_title="Value")
            st.plotly_chart(fig_sms, use_container_width=True)
    else:
        st.warning("No SMS records found for selected number and date.")