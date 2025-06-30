import json
from collections import Counter, defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="📞 CDR Analyzer", layout="wide")

st.title("📞 Call Detail Record (CDR) Analyzer")
st.markdown("Upload a JSON file and enter a number to analyze filtered call activity.")

uploaded_file = st.file_uploader("📤 Upload your call_logs.json file", type=["json"])
target_number = st.text_input("🔍 Enter a mobile number to filter (e.g., 91979 or +91 or 97 )")

if uploaded_file and target_number:
    try:
        call_data = json.load(uploaded_file)

        filtered_calls = [c for c in call_data if c.get("number") == target_number]
        if not filtered_calls:
            st.warning(f"No records found for {target_number}.")
        else:
            st.success(f"✅ Found {len(filtered_calls)} calls for {target_number}.")

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
                    st.error(f"Error in call record: {e}")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Hourly Call Distribution")
                hours = sorted(hourly_distribution.keys())
                counts = [hourly_distribution[h] for h in hours]
                fig1 = plt.figure(figsize=(10, 4))
                plt.bar(hours, counts, color='skyblue')
                plt.xlabel("Hour of Day")
                plt.ylabel("Number of Calls")
                plt.title(f"Call Activity by Hour for {target_number}")
                plt.grid(True, axis='y', linestyle='--', alpha=0.5)
                st.pyplot(fig1)

            with col2:
                st.subheader("📞 Call Type Breakdown")
                labels = list(call_type_count.keys())
                values = list(call_type_count.values())
                fig2 = plt.figure(figsize=(6, 6))
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.title("Call Type Distribution")
                plt.axis("equal")
                st.pyplot(fig2)

            st.subheader("⏱ Call Duration Histogram")
            if call_durations:
                durations_min = [d / 60 for d in call_durations if d > 0]
                fig3 = plt.figure(figsize=(10, 4))
                plt.hist(durations_min, bins=10, color='orchid', edgecolor='black')
                plt.xlabel("Duration (minutes)")
                plt.ylabel("Number of Calls")
                plt.title("Call Duration Distribution")
                plt.grid(True, axis='y', linestyle='--', alpha=0.6)
                st.pyplot(fig3)

            # Optional: show filtered data
            st.subheader("📋 Filtered Call Records")
            st.dataframe(pd.DataFrame(filtered_calls))

    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.info("Please upload your JSON file and enter a number to analyze.")