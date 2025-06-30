import streamlit as st
import pandas as pd
import json
import plotly.express as px

# Page configuration
st.set_page_config(page_title="📊 Dynamic CDR Visualizer", layout="wide")

st.title("📊 CDR Data Plotly Visualizer")
st.markdown("Upload your JSON file and choose numeric columns to visualize using interactive Plotly charts.")

# --- Step 1: Upload JSON File ---
uploaded_file = st.file_uploader("📤 Upload your call_logs.json file", type=["json"])

if uploaded_file:
    try:
        # Load and parse JSON
        data = json.load(uploaded_file)
        df = pd.DataFrame(data)
        df.columns = df.columns.str.strip()

        st.success(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns.")
        st.subheader("🔍 Preview of Data")
        st.dataframe(df.head(10), use_container_width=True)

        # --- Step 2: Numeric Columns ---
        numeric_cols = df.select_dtypes(include='number').columns.tolist()

        if numeric_cols:
            selected_columns = st.multiselect("📌 Select numeric columns to plot", numeric_cols)

            if selected_columns:
                top_n = st.slider("Top N rows to plot", min_value=5, max_value=100, value=20)

                # Melt for Plotly bar chart
                melted = df.head(top_n)[selected_columns].reset_index().melt(id_vars="index")

                fig = px.bar(
                    melted, 
                    x="index", 
                    y="value", 
                    color="variable", 
                    barmode="group",
                    title=f"📊 Bar Chart of Selected Columns (Top {top_n} Rows)"
                )
                fig.update_layout(xaxis_title="Record Index", yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠ Please select at least one column to visualize.")
        else:
            st.error("❌ No numeric columns found in uploaded file.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

else:
    st.info("Please upload a JSON file to get started.")