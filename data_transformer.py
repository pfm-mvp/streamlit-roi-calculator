import pandas as pd

def normalize_vemcount_response(response_json: dict) -> pd.DataFrame:
    """
    Zet de geneste Vemcount API response om naar een platte Pandas DataFrame.
    Verwacht structuur:
    {
      "26646": {
        "data": {...},
        "dates": {
            "Mon. Jan 1, 2024": {"data": {"turnover": ..., "dt": ...}},
            ...
        }
      },
      ...
    }
    """
    rows = []

    for shop_id, shop_content in response_json.items():
        dates = shop_content.get("dates", {})
        for _, day_info in dates.items():
            data = day_info.get("data", {})
            row = {
                "shop_id": int(shop_id),
                "date": data.get("dt") or data.get("label") or data.get("x") or None,
                "turnover": float(data.get("turnover", 0)),
                "count_in": float(data.get("count_in", 0)),
                "conversion_rate": float(data.get("conversion_rate", 0))
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df
