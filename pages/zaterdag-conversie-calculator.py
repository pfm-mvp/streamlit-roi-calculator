# 📈 Zaterdag Conversie Calculator – Streamlit

import streamlit as st
import sys
import os
import pandas as pd
import requests
import plotly.express as px
from datetime import date

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
            full_response = response.json()
            if "data" in full_response and "last_year" in full_response["data"]:
                raw_data = full_response["data"]["last_year"]
                return normalize_vemcount_response(raw_data)
        else:
            st.error(f"❌ Error fetching data: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"🚨 API call exception: {e}")
    return pd.DataFrame()

# -----------------------------
# SIMULATIE FUNCTIE
# -----------------------------
def simulate_conversion_boost_on_saturdays(df, conversion_boost_pct):
    if "date" not in df.columns:
        raise ValueError("❌ The 'date' column is missing from the DataFrame.")
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"].dt.day_name() == "Saturday"].copy()

    if "sales_per_transaction" not in df.columns:
        st.error("❌ 'sales_per_transaction' is missing in the data.")
        st.write("📋 Available columns:", df.columns.tolist())
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
st.set_page_config(page_title="ROI Calculator - Saturday Conversion", layout="wide")
# ✅ Custom styling for slider, multiselect and success box
st.markdown(
    """
    <style>
    /* ✅ Fix slider track fill color (via SVG target) */
    [data-baseweb="slider"] svg [stroke] {
        stroke: #D8456C !important;
    }

    [data-baseweb="slider"] svg [fill] {
        fill: #D8456C !important;
    }

    /* ✅ Fix slider thumb kleur */
    [data-baseweb="slider"] div[role="slider"] {
        background-color: #D8456C !important;
        border: 2px solid #D8456C !important;
    }

    /* ✅ Multiselect pills */
    [data-baseweb="tag"] {
        background-color: #762181 !important;
        color: white !important;
    }

    /* ✅ Success alert (fallback voor custom box) */
    .stAlert-success {
        background-color: #FEAC76 !important;
        color: black !important;
        border: none !important;
    }

    /* ✅ Algemene fix voor consistentie */
    [data-testid="stSlider"] {
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("📈 ROI Calculator – Saturday Conversion Boost")
st.markdown("Simulate the revenue impact of a higher Saturday conversion rate for your retail portfolio.")

shop_ids = st.multiselect("Select stores (shop IDs)", options=DEFAULT_SHOP_IDS, default=DEFAULT_SHOP_IDS)
conversion_boost_pct = st.slider("Conversion increase (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# ✅ Simulatieblok
if st.button("📊 Run simulation"):
    with st.spinner("Calculating hidden location potential..."):
        df_kpi = get_kpi_data_for_stores(shop_ids, period="last_year", step="day")

    if not df_kpi.empty:
        df_results = simulate_conversion_boost_on_saturdays(df_kpi, conversion_boost_pct)

        st.markdown('<div class="custom-success">✅ Simulation complete</div>', unsafe_allow_html=True)
        st.subheader("📊 Expected revenue growth from Saturday conversion boost")

        # ✅ Tabel
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

        # ✅ Plotly grafiek (verticale, leesbare bars)
        df_results["store_name"] = "Store " + df_results["shop_id"].astype(str)

        fig = px.bar(
            df_results,
            x="store_name",
            y="extra_turnover",
            color_discrete_sequence=["#762181"],
            labels={"store_name": "Store", "extra_turnover": "Extra Turnover (€)"},
            title="Saturday Conversion Boost Impact"
        )

        fig.update_layout(
            plot_bgcolor="#F0F1F1",
            paper_bgcolor="#F0F1F1",
            font_color="#feac76",
            xaxis=dict(
                title="Store",
                title_font=dict(color="#feac76"),
                tickfont=dict(color="#feac76"),
                linecolor="#85888E",
                gridcolor="#85888E",
                type='category'
            ),
            yaxis=dict(
                title="Extra Turnover (€)",
                title_font=dict(color="#feac76"),
                tickfont=dict(color="#feac76"),
                linecolor="#85888E",
                gridcolor="#85888E"
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected period/stores.")
