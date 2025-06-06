import streamlit as st
import pandas as pd
import calendar
import platform

# --- CONFIG ---
ST3_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st3/st3_cleaned.csv"
ST53_URL = "https://raw.githubusercontent.com/blainehodder/WCSB_Supply_Demand/main/clean_data/st53/st53_cleaned.csv"
BARREL_CONVERSION = 6.29287

# --- CUSTOM THEME ---
st.markdown("""
    <style>
        body {
            background-color: #f9fafb;
            color: #1f2937;
            font-family: 'Segoe UI', sans-serif;
        }
        .css-1d391kg, .css-1kyxreq {
            padding-top: 1rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            border: 1px solid #e5e7eb;
            padding: 6px;
            text-align: center;
        }
        th {
            background-color: #f3f4f6;
            position: sticky;
            top: 0;
            z-index: 1;
        }
        .section {
            background-color: #dbeafe;
            font-weight: bold;
            text-align: left;
        }
        .label {
            text-align: left;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_st3():
    df = pd.read_csv(ST3_URL, header=None)
    if df.shape[1] == 9:
        df.columns = ["Year", "Month", "Date", "Label", "Name", "Unused1", "Unused2", "Type", "Value"]
    else:
        st.error(f"Unexpected number of columns: {df.shape[1]}")
        st.stop()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    return df

@st.cache_data
def load_st53():
    df = pd.read_csv(ST53_URL)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Bitumen Production"] = pd.to_numeric(df["Bitumen Production"], errors="coerce")
    return df

st3 = load_st3()
st53 = load_st53()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Controls")
    unit_toggle = st.radio("Display Units", ["m³/day", "bbl/day"])
    convert_to_barrels = unit_toggle == "bbl/day"

    st.markdown("---")
    st.header("🗓 Date Range")
    max_date = st3["Date"].max()
    default_start = max_date - pd.DateOffset(months=23)
    default_end = max_date

    # Detect browser-safe date format
    date_range = st.slider(
        "Select date range",
        min_value=st3["Date"].min().to_pydatetime(),
        max_value=st3["Date"].max().to_pydatetime(),
        value=(default_start.to_pydatetime(), default_end.to_pydatetime()),
        format="YYYY-MM"
    )


# --- SUMMARY BLOCK ---
st.markdown("""
### 📌 Market Context Summary
*This section will be manually populated to summarize recent market events, outages, apportionment notes, and strategic updates.*

- **Maintenance Season:** Placeholder for scheduled upgrader outages
- **Pipeline Apportionment:** Placeholder for Enbridge/CER apportionment notice
- **Market Impact:** Placeholder for recent differentials or pricing pressures
""")

# --- MAIN DATA PROCESSING ---
mask = (st3["Date"] >= date_range[0]) & (st3["Date"] <= date_range[1])
st3_filtered = st3[mask].copy()
is_flow = st3_filtered["Type"].str.lower().eq("flow")
st3_filtered["Days"] = st3_filtered["Date"].apply(lambda d: calendar.monthrange(d.year, d.month)[1])
st3_filtered.loc[is_flow, "Value"] = st3_filtered.loc[is_flow, "Value"] / st3_filtered.loc[is_flow, "Days"]
if convert_to_barrels:
    st3_filtered["Value"] *= BARREL_CONVERSION
    st53["Bitumen Production"] *= BARREL_CONVERSION
st3_pivot = st3_filtered.pivot(index="Label", columns="Date", values="Value").fillna(0)
dates_sorted = sorted(st3_pivot.columns)

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
    {"type": "expander"},
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

html_top = "<table><tr><th class='label'>Category</th>" + "".join(
    f"<th>{d.strftime('%b %Y')}</th>" for d in dates_sorted
) + "</tr>"

expander_inserted = False
html_bottom = ""
for row in row_template:
    if row["type"] == "title":
        html_bottom += f"<tr><td class='section' colspan='{len(dates_sorted)+1}'>{row['label']}</td></tr>"
    elif row["type"] == "data":
        html_bottom += f"<tr><td class='label'>{row['label']}</td>"
        for d in dates_sorted:
            try:
                val = st3_pivot.loc[row["label"], d]
                html_bottom += f"<td>{int(round(val)):,}</td>"
            except:
                html_bottom += "<td>–</td>"
        html_bottom += "</tr>"
    elif row["type"] == "expander" and not expander_inserted:
        html_top += html_bottom + "</table>"
        st.markdown(html_top, unsafe_allow_html=True)

        with st.expander("In Situ Breakdown (ST53)", expanded=False):
            st53_mask = (st53["Date"] >= date_range[0]) & (st53["Date"] <= date_range[1])
            st53_filtered = st53[st53_mask].copy()
            st53_filtered["Label"] = st53_filtered["Operator"] + " – " + st53_filtered["Scheme Name"]

            pivot = st53_filtered.pivot_table(
                index="Label",
                columns="Date",
                values="Bitumen Production",
                aggfunc="sum",
                fill_value=0
            )
            pivot["__avg__"] = pivot.mean(axis=1)
            pivot = pivot.sort_values("__avg__", ascending=False).drop(columns="__avg__")

            colgroup_html = "<colgroup><col style='width: 20%;'>" + "".join(
                "<col style='width: 6.66%;'>" for _ in sorted(pivot.columns)
            ) + "</colgroup>"
            
            sub_html = "<table>" + colgroup_html + "<tr><th class='label'>Operator – Scheme</th>" + "".join(
                f"<th>{d.strftime('%b %Y')}</th>" for d in sorted(pivot.columns)
            ) + "</tr>"

            for label, row in pivot.iterrows():
                sub_html += f"<tr><td class='label'>{label}</td>"
                for d in sorted(pivot.columns):
                    val = row[d]
                    sub_html += f"<td>{int(round(val)):,}</td>"
                sub_html += "</tr>"
            sub_html += "</table>"
            st.markdown(sub_html, unsafe_allow_html=True)

        html_top = "<table><tr><th class='label'>Category</th>" + "".join(
            f"<th>{d.strftime('%b %Y')}</th>" for d in dates_sorted
        ) + "</tr>"
        html_bottom = ""
        expander_inserted = True

html_final = html_top + html_bottom + "</table>"
st.markdown(html_final, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Built by Blaine Hodder | Data via Alberta Energy Regulator")
