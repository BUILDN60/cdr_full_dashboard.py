# my_analysis.py
def run_my_analysis(df):
    # Your custom logic
    df['Duration_Minutes'] = df['Duration'] / 60
    summary = df.describe()
    return summary, df
# Run your script on the backend
summary, processed_df = run_my_analysis(df)

st.subheader("📑 Summary from Your Script")
st.write(summary)

st.subheader("🔍 Data after Script Processing")
st.dataframe(processed_df)
def run_my_analysis(df):
    if 'Duration' not in df.columns:
        raise KeyError("The 'Duration' column is missing. Check your JSON structure or MongoDB data.")

    df['Duration_Minutes'] = df['Duration'] / 60
    summary = df.describe()
    return summary, df
from st_aggrid import AgGrid, GridOptionsBuilder

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(resizable=True, filterable=True, sortable=True)
gb.configure_column("iso_time", pivot=True)
gb.configure_column("number", rowGroup=True)
gb.configure_column("call_type", aggFunc="count")
grid_opts = gb.build()

data = AgGrid(df, gridOptions=grid_opts, enable_enterprise_modules=True)