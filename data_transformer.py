import pandas as pd
import streamlit as st  # nodig voor debug output

def normalize_vemcount_response(response_json: dict) -> pd.DataFrame:
    rows = []

    for shop_id, shop_content in response_json.items():
        dates = shop_content.get("dates", {})
        for date_label, day_info in dates.items():
            data = day_info.get("data", {})

            # 🧪 Debug: check welke keys beschikbaar zijn per dag
            st.write(f"🔍 {shop_id} - {date_label} - keys in dagdata:", list(data.keys()))

            row = {
                "shop_id": int(shop_id),
                "date": data.get("dt"),
                "turnover": float(data.get("turnover", 0)),
                "count_in": float(data.get("count_in", 0)),
                "conversion_rate": float(data.get("conversion_rate", 0)),
                # ✅ Gebruik fallback voor veiligheid (bijv. None of lege string)
                "sales_per_transaction": float(data.get("sales_per_transaction") or 0),
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    return df
