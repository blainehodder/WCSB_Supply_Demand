import streamlit as st
import pandas as pd
import datetime
import calendar

# --- CONFIG ---
ST3_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st3/st3_cleaned.csv"
BARREL_CONVERSION = 6.29287

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv(ST3_URL, header=None)

    if df.shape[1] == 9:
        df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Unused2", "Type", "Value"]
    elif df.shape[1] == 8:
        df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Type", "Value"]
    elif df.shape[1] == 7:
        df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Value"]
    else:
        st.error(f"Unexpected number of columns: {df.shape[1]}")
        st.stop()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    return df

df = load_data()

# --- UNIT TOGGLE ---
st.sidebar.header("Settings")
unit_toggle = st.sidebar.radio("Display Units", ["m³/day", "bbl/day"])
convert_to_barrels = unit_toggle == "bbl/day"

# --- DATE RANGE SELECTOR ---
max_date = df['Date'].max()
default_start = max_date - pd.DateOffset(months=23)
default_end = max_date

date_range = st.sidebar.slider(
    "Select date range",
    min_value=df['Date'].min().to_pydatetime(),
    max_value=df['Date'].max().to_pydatetime(),
    value=(default_start.to_pydatetime(), default_end.to_pydatetime()),
    format="%b %Y"
)

mask = (df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])
df_filtered = df[mask].copy()

# --- NORMALIZE TO DAILY ---
df_filtered['Days'] = df_filtered['Date'].dt.daysinmonth.replace(0, 30)
df_filtered['Value'] = df_filtered['Value'] / df_filtered['Days']

if convert_to_barrels:
    df_filtered['Value'] *= BARREL_CONVERSION

df_pivot = df_filtered.pivot(index="Label", columns="Date", values="Value").fillna(0)
dates_sorted = sorted(df_pivot.columns)

# --- TEMPLATE ---
row_template = [
    {"type": "title", "label": "SUPPLY"},
    {"type": "data", "label": "Opening Inventory"},
    {"type": "title", "label": "Production"},
    {"type": "title", "label": "Crude Oil Production"},
    {"type": "data", "label": "Crude Oil Light"},
    {"type": "data", "label": "Crude Oil Medium"},
    {"type": "data", "label": "Crude Oil Heavy"},
    {"type": "data", "label": "Crude Oil Ultra-Heavy"},
    {"type": "data", "label": "Total Crude Oil Production"},
    {"type": "data", "label": "Condensate Production"},
    {"type": "title", "label": "Oil Sands Production"},
    {"type": "title", "label": "Nonupgraded"},
    {"type": "data", "label": "In Situ Production"},
    {"type": "data", "label": "Mined Production"},
    {"type": "data", "label": "Sent for Further Processing"},
    {"type": "data", "label": "Nonupgraded Total"},
    {"type": "data", "label": "Upgraded Production"},
    {"type": "data", "label": "Total Oil Sands Production"},
    {"type": "data", "label": "Total Production"},
    {"type": "title", "label": "Receipts"},
    {"type": "data", "label": "Pentanes Plus  - Plant/Gathering Process"},
    {"type": "data", "label": "Pentanes Plus  - Fractionation Yield"},
    {"type": "data", "label": "Skim Oil Recovered"},
    {"type": "data", "label": "Waste Plant Receipts"},
    {"type": "data", "label": "Other Alberta Receipts"},
    {"type": "data", "label": "Butanes reported as Crude Oil or Equivalent"},
    {"type": "data", "label": "NGL reported as Crude Oil or Equivalent"},
    {"type": "title", "label": "Imports"},
    {"type": "data", "label": "Pentanes Plus"},
    {"type": "data", "label": "Condensates"},
    {"type": "data", "label": "Crude Oil"},
    {"type": "data", "label": "Synthetic Crude Oil"},
    {"type": "data", "label": "Total Imports"},
    {"type": "data", "label": "Total Receipts"},
    {"type": "data", "label": "Flare or Waste"},
    {"type": "data", "label": "Fuel"},
    {"type": "data", "label": "Shrinkage"},
    {"type": "data", "label": "Closing Inventory"},
    {"type": "data", "label": "Adjustments"},
    {"type": "data", "label": "TOTAL OIL & EQUIVALENT SUPPLY"},
]

# --- RENDER ---
st.title("WCSB Oil Supply & Disposition Summary")
st.markdown(f"**Showing:** {date_range[0].strftime('%b %Y')} to {date_range[1].strftime('%b %Y')} | Units: {unit_toggle}**")

html = """
<style>
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }
    th, td {
        border: 1px solid #dddddd;
        padding: 6px;
        text-align: right;
    }
    th {
        background-color: #f0f0f0;
        position: sticky;
        top: 0;
        z-index: 1;
    }
    .section {
        background-color: #dce6f1;
        font-weight: bold;
        text-align: left;
    }
    .label {
        text-align: left;
    }
</style>
<table>
"""

html += "<tr><th class='label'>Category</th>"
for d in dates_sorted:
    html += f"<th>{d.strftime('%b %Y')}</th>"
html += "</tr>"

for row in row_template:
    if row['type'] == 'title':
        html += f"<tr><td class='section' colspan='{len(dates_sorted) + 1}'>{row['label']}</td></tr>"
    elif row['type'] == 'data':
        html += f"<tr><td class='label'>{row['label']}</td>"
        for d in dates_sorted:
            try:
                val = df_pivot.loc[row['label'], d]
                display_val = f"{int(round(val)):,}"
            except:
                display_val = "–"
            html += f"<td>{display_val}</td>"
        html += "</tr>"

html += "</table>"
st.markdown(html, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Built by Blaine Hodder | Data via Alberta Energy Regulator")