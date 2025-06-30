  # app.py
import streamlit as st
import pandas as pd
import json
from mongo_utils import connect_mongo, insert_data, fetch_data_as_dataframe
from analysis import analyze_dataframe, plot_top_contacts, run_my_analysis

st.title("📞 CDR Web Application")

collection = connect_mongo()

uploaded_file = st.file_uploader("Upload your JSON file", type=["json"], key="json_uploader")

if uploaded_file:
    data = json.load(uploaded_file)
    df = pd.json_normalize(data)
    st.success("✅ Data Loaded Successfully!")

    # Upload to MongoDB
    if st.button("⬆ Upload to MongoDB"):
        insert_data(collection, data)
        st.success("✅ Data Inserted into MongoDB!")

# Load from MongoDB for display and analysis
if st.button("📥 Load Data from MongoDB"):
    df = fetch_data_as_dataframe(collection)
    st.dataframe(df)

    st.subheader("📈 Analysis from MongoDB Data")
    summary, processed_df = run_my_analysis(df)
    st.write("🔹 Summary:")
    st.write(summary)

    st.subheader("📊 Top Contacts Visualization")
    st.pyplot(plot_top_contacts(df))

    st.subheader("🔎 Filter and Sort")
    # Example: Filter by a contact
    contact_filter = st.selectbox("Filter by Receiver", options=df['Receiver'].unique())
    filtered_df = df[df['Receiver'] == contact_filter]
    st.dataframe(filtered_df)

 # app.py
import streamlit as st
import json
from cdr_analyzer import analyze_from_uploaded_json
import matplotlib.pyplot as plt

st.set_page_config(page_title="CDR Web App", layout="wide")
st.title("📞 Call & SMS Log Analyzer")

# Upload files with unique keys
call_file = st.file_uploader("📤 Upload Call Logs (JSON)", type="json", key="call_uploader")
sms_file = st.file_uploader("📤 Upload SMS Logs (JSON)", type="json", key="sms_uploader")

if call_file and sms_file:
    try:
        call_data = json.load(call_file)
        sms_data = json.load(sms_file)

        analyzer = analyze_from_uploaded_json(call_data, sms_data)

        st.success("✅ Data Analyzed Successfully!")

        # Show Summary
        st.subheader("📋 Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📞 Call Type Count")
            st.json(dict(analyzer.call_type_count))
        with col2:
            st.write("### 📩 SMS Direction Count")
            st.json(dict(analyzer.sms_direction_count))

        st.write("### 🔝 Top 5 Frequent Contacts")
        for number, count in analyzer.contact_frequency.most_common(5):
            st.markdown(f"- *{number}*: {count} times")

        # Plotting
        st.subheader("📊 Hourly Activity Chart")

        hours = sorted(analyzer.hourly_stats.keys())
        calls = [analyzer.hourly_stats[h]["calls"] for h in hours]
        sms = [analyzer.hourly_stats[h]["sms"] for h in hours]
        bar_width = 0.4
        x = list(range(len(hours)))

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar([i - bar_width / 2 for i in x], calls, width=bar_width, label='Calls', color='steelblue')
        ax.bar([i + bar_width / 2 for i in x], sms, width=bar_width, label='SMS', color='salmon')

        ax.set_xticks(x)
        ax.set_xticklabels([f"{h}:00" for h in hours])
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Count")
        ax.set_title("Call & SMS Activity by Hour")
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"⚠ Error during processing: {e}")

else:
    st.info("👆 Please upload both call and SMS log JSON files to begin.")
    from cdr_analyzer import CDRAnalyzer

analyzer = CDRAnalyzer.analyze_from_uploaded_json(call_data, sms_data)

from cdr_analyzer import analyze_from_uploaded_json

# After uploading files and converting to dict:
analyzer = analyze_from_uploaded_json(call_data, sms_data)
analyzer.generate_summary()
analyzer.plot_activity(show_inline=True)

