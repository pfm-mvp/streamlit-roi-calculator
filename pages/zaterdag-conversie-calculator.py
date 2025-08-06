# 📈 Zaterdag Conversie Calculator – Streamlit

import streamlit as st
import sys
import os
import pandas as pd
import requests
from datetime import date
import matplotlib.pyplot as plt  # <== deze regel moet er staan

# 👇 Zet dit vóór de import!
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

# ✅ Nu pas importeren
from data_transformer import normalize_vemcount_response

# -----------------------------
# CONFIGURATIE
# -----------------------------
API_URL = st.secrets["API_URL"].rstrip("/")
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

        if response.status_code == 200:
            try:
                full_response = response.json()

                if "data" in full_response and "last_year" in full_response["data"]:
                    raw_data = full_response["data"]["last_year"]
                    return normalize_vemcount_response(raw_data)
                else:
                    return pd.DataFrame()
            except Exception:
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
    if "sales_per_transaction" not in df.columns:
        st.error("❌ 'sales_per_transaction' ontbreekt in de DataFrame.")
        st.write("📋 Beschikbare kolommen:", df.columns.tolist())
        st.stop()

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
st.title("📈 ROI Calculator - Conversieboost on Saturdays")
st.markdown("Simulate the revenue impact of a higher Saturday conversion rate for your retail portfolio.")

# Sidebar inputs
shop_ids = st.multiselect("Selecteer winkels (shop IDs)", options=DEFAULT_SHOP_IDS, default=DEFAULT_SHOP_IDS)
conversion_boost_pct = st.slider("Conversieverhoging (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# Ophalen data en simulatie uitvoeren
if st.button("📊 Simuleer omzetgroei"):
    with st.spinner("Data ophalen van Vemcount API..."):
        df_kpi = get_kpi_data_for_stores(shop_ids, period="last_year", step="day")

    if not df_kpi.empty:
        df_results = simulate_conversion_boost_on_saturdays(df_kpi, conversion_boost_pct)

        st.success("✅ Simulation complete")
        st.subheader("📊 Expected revenue growth from Saturday conversion boost")

    # Apply custom styling to the data table
    def style_table(df):
        return df.style.set_properties(
            **{
                "background-color": "#FAFAFA",
                "color": "#0C111D",
                "border-color": "#85888E",
            }
        ).apply(
            lambda x: ["background-color: #F0F1F1" if i % 2 else "" for i in range(len(x))], axis=0
        ).format({
            "original_turnover": "€{:,.0f}",
            "extra_turnover": "€{:,.0f}",
            "new_total_turnover": "€{:,.0f}",
            "growth_pct": "{:.2f}%"
        })
    st.dataframe(style_table(df_results))

    # Generate bar chart with custom style
    fig, ax = plt.subplots(figsize=(8, 5), facecolor="#F0F1F1")
    ax.bar(df_results["shop_id"].astype(str), df_results["extra_turnover"], color="#762181")
    ax.set_facecolor("#F0F1F1")
    ax.tick_params(colors="#F0F1F1")
    ax.spines['bottom'].set_color("#F0F1F1")
    ax.spines['left'].set_color("#F0F1F1")
    ax.set_ylabel("Extra Turnover (€)", color="#F0F1F1")
    ax.set_xlabel("Store", color="#F0F1F1")
    plt.xticks(color="#F0F1F1")
    plt.yticks(color="#F0F1F1")
    plt.title("Saturday Conversion Boost Impact", color="#F0F1F1")
    plt.tight_layout()

    st.pyplot(fig)
else:
    st.warning("⚠️ No data available for the selected period/stores.")
