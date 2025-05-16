import streamlit as st
import pandas as pd
import calendar

# --- CONFIG ---
ST3_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st3/st3_cleaned.csv"
ST53_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st53/st53_cleaned.csv"
BARREL_CONVERSION = 6.29287

# --- LOAD ST3 DATA ---
@st.cache_data
def load_st3():
    df = pd.read_csv(ST3_URL, header=None)
    df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Unused2", "Type", "Value"]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    return df

# --- LOAD ST53 DATA ---
@st.cache_data
def load_st53():
    df = pd.read_csv(ST53_URL)
    df.columns = [col.strip() for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'])
    df['Bitumen Production'] = pd.to_numeric(df['Bitumen Production'], errors='coerce')
    return df

df = load_st3()
st53 = load_st53()

# --- UNIT TOGGLE ---
unit_toggle = st.radio("Display Units", ["m³/day", "bbl/day"])
convert_to_barrels = unit_toggle == "bbl/day"

# --- DATE RANGE ---
max_date = df['Date'].max()
default_start = max_date - pd.DateOffset(months=23)
default_end = max_date

date_range = st.slider(
    "Select date range",
    min_value=df['Date'].min().to_pydatetime(),
    max_value=df['Date'].max().to_pydatetime(),
    value=(default_start.to_pydatetime(), default_end.to_pydatetime()),
    format="%b %Y"
)

# --- FILTER ST3 ---
mask = (df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])
df_filtered = df[mask].copy()

df_filtered['Days'] = df_filtered['Date'].apply(lambda d: calendar.monthrange(d.year, d.month)[1])
df_filtered['DailyValue'] = df_filtered.apply(
    lambda row: row['Value'] / row['Days'] if row['Type'] == 'flow' else row['Value'], axis=1
)

if convert_to_barrels:
    df_filtered['DailyValue'] *= BARREL_CONVERSION

df_pivot = df_filtered.pivot(index="Label", columns="Date", values="DailyValue").fillna(0)
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
    {"type": "title", "label": "DISPOSITION"},
    {"type": "title", "label": "Alberta Use"},
    {"type": "data", "label": "Alberta Injection and Well Use"},
    {"type": "data", "label": "Alberta Refinery Sales"},
    {"type": "data", "label": "Waste Plant Use"},
    {"type": "data", "label": "Plant Use"},
    {"type": "data", "label": "Line Fill"},
    {"type": "data", "label": "Load Fluid"},
    {"type": "data", "label": "Alberta Other Sales"},
    {"type": "data", "label": "Total Alberta Use"},
    {"type": "data", "label": "Removals from Alberta"},
    {"type": "data", "label": "Reporting Adjustment"},
    {"type": "data", "label": "TOTAL OIL & EQUIVALENT DISPOSITION"},
]

# --- MAIN TABLE ---
st.title("WCSB Oil Supply & Disposition Summary")
st.markdown(f"**Showing:** {date_range[0].strftime('%b %Y')} to {date_range[1].strftime('%b %Y')} | Units: {unit_toggle}**")

html = """
<style>
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { border: 1px solid #ddd; padding: 6px; text-align: right; }
    th { background-color: #f0f0f0; position: sticky; top: 0; z-index: 1; }
    .section { background-color: #dce6f1; font-weight: bold; text-align: left; }
    .label { text-align: left; }
</style>
<table>
<tr><th class='label'>Category</th>" + "".join(f"<th>{d.strftime('%b %Y')}</th>" for d in dates_sorted) + "</tr>"

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

# --- ST53 EXPANDER ---
st.markdown("---")
with st.expander("In Situ Breakdown by Operator (ST53)"):
    st53_filtered = st53[(st53['Date'] >= date_range[0]) & (st53['Date'] <= date_range[1])].copy()
    if convert_to_barrels:
        st53_filtered['Bitumen Production'] *= BARREL_CONVERSION

    st53_filtered['Operator-Scheme'] = st53_filtered['Operator'] + " – " + st53_filtered['Scheme Name']
    pivot_st53 = st53_filtered.pivot_table(
        index='Operator-Scheme',
        columns='Date',
        values='Bitumen Production',
        aggfunc='sum'
    ).fillna(0)

    pivot_st53['2024_avg'] = pivot_st53[[d for d in pivot_st53.columns if isinstance(d, pd.Timestamp) and d.year == 2024]].mean(axis=1)
    pivot_st53 = pivot_st53.sort_values(by='2024_avg', ascending=False).drop(columns=['2024_avg'])

    html_st53 = """
    <table>
    <tr><th class='label'>Operator – Scheme</th>""" + "".join(f"<th>{d.strftime('%b %Y')}</th>" for d in sorted(pivot_st53.columns) if isinstance(d, pd.Timestamp)) + "</tr>"
    for idx, row in pivot_st53.iterrows():
        html_st53 += f"<tr><td class='label'>{idx}</td>"
        for val in row:
            try:
                html_st53 += f"<td>{int(round(val)):,}</td>"
            except:
                html_st53 += "<td>–</td>"
        html_st53 += "</tr>"
    html_st53 += "</table>"

    st.markdown(html_st53, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Built by Blaine Hodder | Data via Alberta Energy Regulator")
