import streamlit as st
import pandas as pd
import datetime

# --- CONFIG ---
ST3_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st3/st3_cleaned.csv"

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv(ST3_URL)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# --- FILTER TO LAST 24 MONTHS BY DEFAULT ---
max_date = df['Date'].max()
default_start = max_date - pd.DateOffset(months=23)
default_end = max_date

# --- DATE RANGE SELECTOR ---
st.sidebar.header("Date Range")
date_range = st.sidebar.slider(
    "Select date range",
    min_value=df['Date'].min().to_pydatetime(),
    max_value=df['Date'].max().to_pydatetime(),
    value=(default_start.to_pydatetime(), default_end.to_pydatetime()),
    format="%b %Y"
)

mask = (df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])
df_filtered = df[mask]

# --- PIVOT WIDE ---
df_pivot = df_filtered.pivot(index="Label", columns="Date", values="Value")
df_pivot = df_pivot.fillna(0)

# --- GROUPS AND STRUCTURE ---
section_map = {
    "Production": [
        "Crude Oil Light", "Crude Oil Medium", "Crude Oil Heavy",
        "Condensate Production", "Pentanes Plus", "Upgraded Bitumen",
        "In Situ Production", "Mined Production"
    ],
    "Disposition": [
        "Deliveries to Upgraders", "Deliveries to Market",
        "Inventory Change", "Losses"
    ]
}

# --- DISPLAY HEADER ---
st.title("WCSB Oil Supply & Disposition Summary")
st.markdown(f"**Showing:** {date_range[0].strftime('%b %Y')} to {date_range[1].strftime('%b %Y')}")

# --- RENDER SECTIONS ---
for section, items in section_map.items():
    with st.expander(section, expanded=True):
        subset = df_pivot.loc[df_pivot.index.isin(items)]
        styled = subset.style.format("{:.0f}", na_rep="-").set_table_attributes('class="dataframe" style="font-size:14px"')
        st.dataframe(styled, use_container_width=True)

# --- PLACEHOLDER FOR FUTURE LINE CHART BUTTON ---
# Add line charts per label in later version

# --- FOOTER ---
st.markdown("---")
st.caption("Built by Blaine Hodder | Data via Alberta Energy Regulator")
