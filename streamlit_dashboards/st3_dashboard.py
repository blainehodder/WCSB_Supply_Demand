import streamlit as st
import pandas as pd
import calendar

# --- CONFIG ---
ST3_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st3/st3_cleaned.csv"
ST53_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st53/st53_cleaned.csv"
BARREL_CONVERSION = 6.29287

# --- LOAD ST3 ---
@st.cache_data
def load_st3():
    df = pd.read_csv(ST3_URL, header=None)

    if df.shape[1] == 9:
        df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Unused2", "Type", "Value"]
    elif df.shape[1] == 8:
        df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Type", "Value"]
    elif df.shape[1] == 7:
        df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Value"]
        df["Type"] = "flow"
    else:
        st.error(f"Unexpected number of columns: {df.shape[1]}")
        st.stop()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df['Type'] = df['Type'].fillna("flow").str.lower()

    return df

df = load_st3()

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

# --- FILTER & NORMALIZE FLOW VALUES ONLY ---
mask = (df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])
df_filtered = df[mask].copy()
df_filtered['Days'] = df_filtered['Date'].apply(lambda d: calendar.monthrange(d.year, d.month)[1])

is_flow = df_filtered['Type'] == "flow"
df_filtered.loc[is_flow, 'Value'] = df_filtered.loc[is_flow, 'Value'] / df_filtered.loc[is_flow, 'Days']
if convert_to_barrels:
    df_filtered.loc[is_flow, 'Value'] *= BARREL_CONVERSION

df_pivot = df_filtered.pivot(index="Label", columns="Date", values="Value").fillna(0)
dates_sorted = sorted(df_pivot.columns)

# --- RENDER MAIN TABLE ---
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

for row in [
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
    {"type": "data", "label": "In Situ Production"}]:

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

# --- EXPANDER: ST53 In Situ Breakdown ---
with st.expander("In Situ Production Detail by Project"):
    st53 = pd.read_csv(ST53_URL)
    st53 = st53.rename(columns={
        "Bitumen Production": "BitumenVolume",
        "Scheme Name": "Scheme",
        "Operator": "Operator"
    })
    st53['Date'] = pd.to_datetime(st53['Date'], errors='coerce')
    st53['BitumenVolume'] = pd.to_numeric(st53['BitumenVolume'], errors='coerce')
    st53 = st53.dropna(subset=["Operator", "Scheme", "Date", "BitumenVolume"])
    st53['Label'] = st53['Operator'].str.strip() + " – " + st53['Scheme'].str.strip()
    st53_filtered = st53[(st53['Date'] >= date_range[0]) & (st53['Date'] <= date_range[1])].copy()

    if convert_to_barrels:
        st53_filtered['BitumenVolume'] *= BARREL_CONVERSION

    pivot = st53_filtered.pivot_table(
        index="Label",
        columns="Date",
        values="BitumenVolume",
        aggfunc="sum",
        fill_value=0
    )

    pivot['SortMetric'] = pivot[[col for col in pivot.columns if col.year == 2024]].mean(axis=1)
    pivot = pivot.sort_values(by='SortMetric', ascending=False).drop(columns='SortMetric')

    html = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th, td {
            border: 1px solid #dddddd;
            padding: 4px;
            text-align: right;
        }
        th {
            background-color: #f7f7f7;
            position: sticky;
            top: 0;
        }
        .label {
            text-align: left;
        }
    </style>
    <table>
    <tr><th class='label'>Project</th>
    """ + "".join(f"<th>{d.strftime('%b %Y')}</th>" for d in sorted(pivot.columns)) + "</tr>"

    for project, row in pivot.iterrows():
        html += f"<tr><td class='label'>{project}</td>"
        for val in row:
            try:
                html += f"<td>{int(round(val)):,}</td>"
            except:
                html += "<td>–</td>"
        html += "</tr>"

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Built by Blaine Hodder | Data via Alberta Energy Regulator")