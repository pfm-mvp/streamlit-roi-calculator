# 📈 Zaterdag Conversie Calculator – Streamlit

import streamlit as st
import pandas as pd
import requests
from datetime import date

# -----------------------------
# CONFIGURATIE
# -----------------------------
API_URL = st.secrets["API_URL"]
DEFAULT_SHOP_IDS = [26304, 26560, 26509, 26480, 26640, 26359, 26630, 27038, 26647, 26646]

# -----------------------------
# API CLIENT
# -----------------------------
def get_kpi_data_for_stores(shop_ids, start_date, end_date):
    payload = {
        "data": list(shop_ids),  # Zorg dat dit een echte lijst is
        "data_output": ["count_in", "conversion_rate", "turnover"],
        "source": "shops",
        "period": "date",
        "start_date": str(start_date),
        "end_date": str(end_date),
        "step": "day"
    }

    # Debug info om type en structuur te controleren
    st.write("✅ type check:", type(shop_ids), type(payload["data"]))
    st.write("📤 Payload naar Vemcount API:")
    st.json(payload)

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, json=payload, headers=headers)
        st.write("🔁 Statuscode:", response.status_code)
        st.write("📨 Response:", response.text)

        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"❌ Fout bij ophalen data: {response.status_code} - {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"🚨 Exception tijdens API-call: {e}")
        return pd.DataFrame()

# -----------------------------
# SIMULATIE FUNCTIE
# -----------------------------
def simulate_conversion_boost_on_saturdays(df, conversion_boost_pct):
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"].dt.day_name() == "Saturday"]

    df = df.copy()
    df["atv"] = df["turnover"] / (df["count_in"] * df["conversion_rate"])
    df["extra_conversion"] = conversion_boost_pct / 100.0
    df["extra_customers"] = df["count_in"] * df["extra_conversion"]
    df["extra_turnover"] = df["extra_customers"] * df["atv"]

    results = df.groupby("shop_id").agg(
        original_turnover=("turnover", "sum"),
        extra_turnover=("extra_turnover", "sum")
    ).reset_index()

    results["new_total_turnover"] = results["original_turnover"] + results["extra_turnover"]
    results["growth_pct"] = (results["extra_turnover"] / results["original_turnover"]) * 100

    return results

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="ROI Calculator - Conversie op Zaterdagen", layout="wide")
st.title("📈 ROI Calculator - Conversieboost op Zaterdagen")

st.markdown("Simuleer de omzetimpact van een hogere conversie op zaterdagen in 2024 voor je retailportfolio.")

# Sidebar inputs
shop_ids = st.multiselect("Selecteer winkels (shop IDs)", options=DEFAULT_SHOP_IDS, default=DEFAULT_SHOP_IDS)
conversion_boost_pct = st.slider("Conversieverhoging (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# Ophalen data en simulatie uitvoeren
if st.button("📊 Simuleer omzetgroei"):
    with st.spinner("Data ophalen van Vemcount API..."):
        df_kpi = get_kpi_data_for_stores(shop_ids, "2024-01-01", "2024-12-31")

    if not df_kpi.empty:
        df_results = simulate_conversion_boost_on_saturdays(df_kpi, conversion_boost_pct)

        st.success("Simulatie voltooid ✅")

        st.dataframe(df_results.style.format({
            "original_turnover": "€{:,.0f}",
            "extra_turnover": "€{:,.0f}",
            "new_total_turnover": "€{:,.0f}",
            "growth_pct": "{:.2f}%"
        }))

        st.bar_chart(df_results.set_index("shop_id")["extra_turnover"])
    else:
        st.warning("Geen data beschikbaar voor opgegeven periode/winkels.")
