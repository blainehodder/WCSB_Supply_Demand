# WCSB Supply & Demand Model

## Overview
This project is a modular, data-driven supply and demand modeling platform for the **Western Canadian Sedimentary Basin (WCSB)**. It ingests regulatory production data, forecasts operator-level output, and generates forward-looking crude balances and pricing pressure signals.

The model is designed to support **physical crude traders**, **fundamental analysts**, and **quant researchers** operating in North American energy markets.

---

## Key Features
- **Automated Ingestion** of Alberta Energy Regulator (AER) reports:
  - `ST39`: Crude oil production by operator and facility  
  - `ST53`: Upgrader and synthetic crude output  
  - `ST3`: Crude oil supply, demand, and storage summary  
- **Cleaned, Structured Time Series**: All source files parsed into machine-readable format with consistent schemas and date alignment  
- **Granular Supply Modeling**: Bottom-up production estimates by extraction type (SAGD, Mined, Upgraded)  
- **Interactive Streamlit Dashboard**:
  - Expandable ST3 summaries  
  - Project-level drilldowns (Firebag, Surmont, Horizon, etc.)  
  - Custom notes on outages, ramp-ups, and operator guidance  
- **Forward Forecast Engine** *(in progress)*:
  - Manual + regression-based volume projection  
  - Annotation layer from earnings call transcripts and market commentary  
  - Propagation of project-level changes to regional balances  

---

## Why It Matters
The WCSB is a major determinant of:
- Canadian spreads (e.g. WCS, SYN, MSW basis)
- Pipeline capacity pressures (Enbridge apportionment)
- Midwest and Gulf Coast refinery feedstock trends

Yet most industry models are opaque, Excel-based, or top-down. This system builds a **bottom-up, transparent, and extensible** view of WCSB crude flows—suitable for both discretionary and quantitative workflows.

---

## In Progress
- Demand-side modules (refinery throughput, product exports)  
- Signal generation for WCS-WTI basis moves  
- Sentiment ingestion from earnings transcripts  
- Streamlit UX upgrades (expanders, tooltips, projections UI)  

---

## Usage

```bash
# Clone repo
git clone https://github.com/blainehodder/WCSB_Supply_Demand.git
cd WCSB_Supply_Demand

# Install dependencies
pip install -r requirements.txt

# Run Streamlit dashboard
streamlit run dashboard.py
