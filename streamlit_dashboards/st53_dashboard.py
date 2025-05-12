import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 WCSB ST53 Bitumen Production Dashboard")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st53/st53_cleaned.csv"
    df = pd.read_csv(url, parse_dates=["Date"])
    return df

df = load_data()

# Sidebar filters
operators = sorted(df["Operator"].dropna().unique())
schemes = sorted(df["Scheme Name"].dropna().unique())

st.sidebar.header("Filter Options")
selected_operators = st.sidebar.multiselect("Operators", operators, default=operators[:5])
selected_schemes = st.sidebar.multiselect("Scheme Names", schemes)

filtered_df = df[df["Operator"].isin(selected_operators)]
if selected_schemes:
    filtered_df = filtered_df[filtered_df["Scheme Name"].isin(selected_schemes)]

# Line chart
st.subheader("Monthly Bitumen Production (m³)")
prod_over_time = (
    filtered_df.groupby("Date")["Bitumen Production"]
    .sum()
    .reset_index()
    .sort_values("Date")
)
st.line_chart(prod_over_time.set_index("Date"))

# Top producers
st.subheader("Top Producing Operators (Selected Range)")
top_ops = (
    filtered_df.groupby("Operator")["Bitumen Production"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
st.dataframe(top_ops.head(10))
