# analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def analyze_dataframe(df):
    top_contacts = df['Receiver'].value_counts().head(5)
    total_duration = df['Duration'].sum()
    return top_contacts, total_duration

def plot_top_contacts(df):
    top_contacts = df['Receiver'].value_counts().head(5)
    fig = plt.figure()
    sns.barplot(x=top_contacts.index, y=top_contacts.values)
    plt.title("Top 5 Contacts")
    return fig
# analysis.py
def run_my_analysis(df):
    # Your custom logic
    df['Duration_Minutes'] = df['Duration'] / 60
    summary = df.describe()
    return summary, df