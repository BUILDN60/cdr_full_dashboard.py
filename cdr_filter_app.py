import json
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="📞 CDR Analyzer", layout="wide")

st.title("📞 Call Detail Record (CDR) Analyzer")
st.markdown("Upload call logs and filter by mobile number and date.")

# Upload JSON file
uploaded_file = st.file_uploader("📤 Upload call_logs.json", type=["json"])

# Input fields
number_filter = st.text_input("🔍 Enter mobile number (e.g. +919797674849)")
date_filter = st.date_input("📅 Select Date")

# Analyze if all inputs provided
if uploaded_file and number_filter and date_filter:
    try:
        call_data = json.load(uploaded_file)
        target_date_str = date_filter.strftime("%Y-%m-%d")

        # Filter
        filtered_calls = []
        for call in call_data:
            call_number = call.get("number")
            iso_time = call.get("iso_time")
            call_date = datetime.fromisoformat(iso_time).strftime("%Y-%m-%d")
            if call_number == number_filter and call_date == target_date_str:
                filtered_calls.append(call)

        if not filtered_calls:
            st.warning(f"No records found for {number_filter} on {target_date_str}.")
        else:
            st.success(f"✅ {len(filtered_calls)} calls found for {number_filter} on {target_date_str}.")

            # Analyze
            call_type_count = Counter()
            hourly_distribution = defaultdict(int)
            call_durations = []

            for call in filtered_calls:
                try:
                    call_type_count[call["call_type"]] += 1
                    hour = datetime.fromisoformat(call["iso_time"]).hour
                    hourly_distribution[hour] += 1
                    call_durations.append(call["duration_sec"])
                except Exception as e:
                    st.error(f"Error in record: {e}")

            # Plot 1: Hourly Activity
            st.subheader("📊 Hourly Call Activity")
            hours = sorted(hourly_distribution.keys())
            counts = [hourly_distribution[h] for h in hours]
            fig1 = plt.figure(figsize=(10, 4))
            plt.bar(hours, counts, color='cornflowerblue')
            plt.title(f"Hourly Activity\n{number_filter} on {target_date_str}")
            plt.xlabel("Hour of Day")
            plt.ylabel("Number of Calls")
            plt.grid(True, axis='y', linestyle='--', alpha=0.5)
            plt.xticks(range(24))
            st.pyplot(fig1)

            # Plot 2: Call Type
            st.subheader("📞 Call Type Distribution")
            labels = list(call_type_count.keys())
            values = list(call_type_count.values())
            fig2 = plt.figure(figsize=(6, 6))
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.title("Call Type Breakdown")
            plt.axis("equal")
            st.pyplot(fig2)

            # Plot 3: Duration Histogram
            st.subheader("⏱ Call Duration Histogram")
            if call_durations:
                durations_min = [d / 60 for d in call_durations if d > 0]
                fig3 = plt.figure(figsize=(10, 4))
                plt.hist(durations_min, bins=10, color='orchid', edgecolor='black')
                plt.title("Call Duration (Minutes)")
                plt.xlabel("Duration")
                plt.ylabel("Call Count")
                plt.grid(True, axis='y', linestyle='--', alpha=0.6)
                st.pyplot(fig3)

            # Table
            st.subheader("📋 Filtered Call Records")
            st.dataframe(pd.DataFrame(filtered_calls))

    except Exception as e:
        st.error(f"⚠ Error: {e}")

else:
    st.info("Please upload a call log and enter both number and date.")