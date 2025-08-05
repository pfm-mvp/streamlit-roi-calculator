import pandas as pd

def normalize_vemcount_response(response_json: dict) -> pd.DataFrame:
    """
    Zet de geneste Vemcount API response om naar een platte Pandas DataFrame.
    """

    rows = []

    # 📦 Pak de juiste laag uit de JSON-structuur
    shop_level = response_json.get("data", {}).get("last_year", {})

    for shop_id, shop_content in shop_level.items():
        dates = shop_content.get("dates", {})
        for _, day_info in dates.items():
            data = day_info.get("data", {})

            row = {
                "shop_id": int(shop_id),
                "date": data.get("dt"),  # ✅ dt is aanwezig
                "turnover": float(data.get("turnover", 0)),
                "count_in": float(data.get("count_in", 0)),
                "conversion_rate": float(data.get("conversion_rate", 0))
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df
