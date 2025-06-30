import streamlit as st
import json
from collections import defaultdict, Counter
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# ----------------- Analysis Functions -----------------

def analyze_calls(call_records):
    incoming = [c for c in call_records if c.get('call_type') == 'incoming']
    outgoing = [c for c in call_records if c.get('call_type') == 'outgoing']
    longest_call = max(call_records, key=lambda c: c.get('duration_sec', 0), default=None)
    hourly_calls = defaultdict(int)

    for c in call_records:
        try:
            hour = datetime.fromisoformat(c["iso_time"]).hour
            hourly_calls[hour] += 1
        except:
            pass

    return {
        "total_calls": len(call_records),
        "incoming_calls": len(incoming),
        "outgoing_calls": len(outgoing),
        "longest_call_duration": longest_call["duration_sec"] if longest_call else 0,
        "call_distribution_by_hour": dict(hourly_calls)
    }

def analyze_sms(sms_records):
    incoming = [s for s in sms_records if s.get('direction') == 'in']
    outgoing = [s for s in sms_records if s.get('direction') == 'out']
    contact_freq = Counter(s.get('number') for s in sms_records if s.get('number'))
    most_contacted = contact_freq.most_common(1)[0] if contact_freq else ("None", 0)

    return {
        "total_sms": len(sms_records),
        "incoming_sms": len(incoming),
        "outgoing_sms": len(outgoing),
        "most_contacted_number": most_contacted
    }

# ----------------- Streamlit Web App -----------------

st.title("📞📩 Live CDR Analyzer")

# File upload section
call_file = st.file_uploader("Upload Call Logs JSON", type=["json"])
sms_file = st.file_uploader("Upload SMS Logs JSON", type=["json"])

if call_file and sms_file:
    # Load JSON data
    call_data = json.load(call_file)
    sms_data = json.load(sms_file)

    # Run analysis
    call_stats = analyze_calls(call_data)
    sms_stats = analyze_sms(sms_data)

    # Show summary
    st.subheader("📊 Call Summary")
    st.json(call_stats)

    st.subheader("📨 SMS Summary")
    st.json(sms_stats)

    # Plot hourly call activity
    st.subheader("⏱ Call Activity by Hour")
    call_hours = call_stats["call_distribution_by_hour"]
    if call_hours:
        hour_df = pd.DataFrame(list(call_hours.items()), columns=["Hour", "Calls"]).sort_values("Hour")
        st.bar_chart(hour_df.set_index("Hour"))
    else:
        st.info("No valid call timestamps found.")

else:
    st.info("Please upload both Call and SMS JSON files.")