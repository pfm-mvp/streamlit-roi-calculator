# 📈 Zaterdag Conversie Calculator – Streamlit

import streamlit as st
import sys
import os
import pandas as pd
import requests
from datetime import date
from data_transformer import normalize_vemcount_response

# Zorg dat parent directory toegankelijk is
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

# -----------------------------
# CONFIGURATIE
# -----------------------------
API_URL = st.secrets["API_URL"].rstrip("/")  # verwijder eventuele trailing slash
DEFAULT_SHOP_IDS = [26304, 26560, 26509, 26480, 26640, 26359, 26630, 27038, 26647, 26646]

# -----------------------------
# API CLIENT
# -----------------------------
def get_kpi_data_for_stores(shop_ids, period="last_year", step="day"):
    params = [("data", shop_id) for shop_id in shop_ids]
    params += [
        ("data_output", "count_in"),
        ("data_output", "conversion_rate"),
        ("data_output", "turnover"),
        ("data_output", "sales_per_transaction"),
        ("source", "shops"),
        ("period", period),
        ("step", step)
    ]

    try:
        response = requests.post(API_URL, params=params)
        st.write("🔁 Statuscode:", response.status_code)

        if response.status_code == 200:
            try:
                full_response = response.json()

                # ✅ Pak correcte laag
                if "data" in full_response and "last_year" in full_response["data"]:
                    raw_data = full_response["data"]["last_year"]

                    # (optioneel) debug: toon 1 dag
                    sample_shop = list(raw_data.values())[0]
                    sample_day = list(sample_shop.get("dates", {}).values())[0]
                    st.write("🧪 Sample dagdata:", sample_day)

                    return normalize_vemcount_response(raw_data)
                else:
                    st.warning("⚠️ Response heeft niet het verwachte 'last_year' formaat.")
                    return pd.DataFrame()
            except Exception as json_error:
                st.error(f"❌ JSON parsing mislukt: {json_error}")
                return pd.DataFrame()
        else:
            st.error(f"❌ Fout bij ophalen data: {response.status_code} - {response.text}")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"🚨 API-call exception: {e}")
        return pd.DataFrame()

# -----------------------------
# SIMULATIE FUNCTIE
# -----------------------------
def simulate_conversion_boost_on_saturdays(df, conversion_boost_pct):
    if "date" not in df.columns:
        raise ValueError("❌ De kolom 'date' ontbreekt in de DataFrame. Check je normalisatie.")

    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"].dt.day_name() == "Saturday"]

    df = df.copy()
    df["atv"] = df["sales_per_transaction"].replace(0, pd.NA)
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
        df_kpi = get_kpi_data_for_stores(shop_ids, period="last_year", step="day")

    if not df_kpi.empty:
        df_results = simulate_conversion_boost_on_saturdays(df_kpi, conversion_boost_pct)

        st.success("✅ Simulatie voltooid")
        st.subheader("📊 Verwachte omzetgroei bij conversieboost op zaterdagen")

        st.dataframe(df_results.style.format({
            "original_turnover": "€{:,.0f}",
            "extra_turnover": "€{:,.0f}",
            "new_total_turnover": "€{:,.0f}",
            "growth_pct": "{:.2f}%"
        }))

        st.bar_chart(df_results.set_index("shop_id")["extra_turnover"])
    else:
        st.warning("⚠️ Geen data beschikbaar voor opgegeven periode/winkels.")
