import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="📊 CSV Data Analyzer", layout="wide")
st.title("📊📂 Multi-CSV Data Analyzer Toolkit")
st.markdown("Upload one or more CSV files to analyze, visualize, and filter your data.")

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader("📤 Upload CSV file(s)", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    for idx, csv_file in enumerate(uploaded_files):
        st.markdown(f"---\n### 📁 File: {csv_file.name}")

        try:
            df = pd.read_csv(csv_file)
            df.columns = df.columns.str.strip()

            st.success(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns.")
            st.subheader("📄 Full Data Preview")
            st.dataframe(df, use_container_width=True)

            # ---------------- OPTIONAL FILTERING ----------------
            st.subheader("🔍 Optional Filtering")

            col_names = df.columns.tolist()

            # Filter by number column
            number_col = st.selectbox(
                "📞 Select number column (or None)",
                ["None"] + col_names,
                key=f"number_col_{idx}"
            )
            selected_number = None
            if number_col != "None":
                unique_numbers = df[number_col].dropna().unique().tolist()
                selected_number = st.selectbox(
                    "Select a number", unique_numbers, key=f"sel_number_{idx}"
                )

            # Filter by date column
            date_col = st.selectbox(
                "📅 Select date column (or None)",
                ["None"] + col_names,
                key=f"date_col_{idx}"
            )
            selected_date = None
            if date_col != "None":
                try:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    date_options = df[date_col].dropna().dt.date.unique()
                    selected_date = st.date_input(
                        "Pick a date",
                        min_value=min(date_options),
                        max_value=max(date_options),
                        key=f"sel_date_{idx}"
                    )
                except:
                    st.warning("⚠ Failed to parse date column. Check format.")

            # Apply filtering
            filtered_df = df.copy()
            if number_col != "None" and selected_number:
                filtered_df = filtered_df[filtered_df[number_col] == selected_number]
            if date_col != "None" and selected_date:
                filtered_df = filtered_df[
                    pd.to_datetime(filtered_df[date_col], errors='coerce').dt.date == selected_date
                ]

            st.success(f"🔎 Filtered data: {len(filtered_df)} rows")
            st.dataframe(filtered_df, use_container_width=True)

            # ---------------- VISUALIZATIONS ----------------

            st.subheader("📊 Plot Numeric Columns")
            numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
            selected_plot_cols = st.multiselect(
                "Select numeric columns to visualize", numeric_cols, key=f"plot_cols_{idx}"
            )

            if selected_plot_cols:
                top_n = st.slider("Number of rows to plot", 5, min(100, len(filtered_df)), 20, key=f"topn_{idx}")
                melt_df = filtered_df[selected_plot_cols].head(top_n).reset_index().melt(id_vars="index")
                fig_bar = px.bar(melt_df, x="index", y="value", color="variable", barmode="group")
                st.plotly_chart(fig_bar, use_container_width=True)

            # Pie chart
            st.subheader("🥧 Pie Chart for Categorical Column")
            cat_cols = filtered_df.select_dtypes(include='object').columns.tolist()
            cat_col = st.selectbox("Select column for pie chart", ["None"] + cat_cols, key=f"pie_col_{idx}")
            if cat_col != "None":
                counts = filtered_df[cat_col].value_counts().nlargest(10)
                fig_pie, ax = plt.subplots()
                ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=140)
                ax.axis("equal")
                st.pyplot(fig_pie)

            # Histogram
            st.subheader("⏱ Histogram for a Numeric Column")
            hist_col = st.selectbox("Select column for histogram", ["None"] + numeric_cols, key=f"hist_col_{idx}")
            if hist_col != "None":
                fig_hist, ax2 = plt.subplots()
                ax2.hist(filtered_df[hist_col].dropna(), bins=10, color='skyblue', edgecolor='black')
                ax2.set_title(f"Distribution of {hist_col}")
                ax2.set_xlabel(hist_col)
                ax2.set_ylabel("Frequency")
                st.pyplot(fig_hist)

        except Exception as e:
            st.error(f"❌ Error processing file {csv_file.name}: {e}")
else:
    st.info("📂 Please upload one or more CSV files to begin.")