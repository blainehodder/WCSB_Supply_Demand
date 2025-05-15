import streamlit as st
import pandas as pd
import datetime

# --- CONFIG ---
ST3_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st3/st3_cleaned.csv"

# --- LOAD DATA ---
@st.cache_data

def load_data():
    df = pd.read_csv(ST3_URL, header=None)

    df.columns = [
        "Year", "Month", "Date", "Label", "Name", "Unused1", "Type", "Value"
    ]

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

    st.write("✅ Loaded rows:", len(df))
    st.dataframe(df.head())

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

# --- BUILD HTML TABLE ---
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

# --- HEADERS ---
dates_sorted = sorted(df_pivot.columns)
html += "<tr><th class='label'>Category</th>"
for d in dates_sorted:
    html += f"<th>{d.strftime('%b %Y')}</th>"
html += "</tr>"

# --- ROWS ---
for section, items in section_map.items():
    html += f"<tr><td class='section' colspan='{len(dates_sorted) + 1}'>{section}</td></tr>"
    for label in items:
        html += f"<tr><td class='label'>{label}</td>"
        for d in dates_sorted:
            try:
                val = df_pivot.loc[label, d]
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
