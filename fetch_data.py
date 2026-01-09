import json
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data", "nifty_option_chain.json")

def get_option_chain():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data["records"]["data"]

    rows = []
    for item in records:
        strike = item.get("strikePrice")

        if "CE" in item:
            ce = item["CE"]
            rows.append({
                "strike": strike,
                "type": "CE",
                "oi": ce.get("openInterest", 0),
                "change_oi": ce.get("changeinOpenInterest", 0),
                "ltp": ce.get("lastPrice", 0)
            })

        if "PE" in item:
            pe = item["PE"]
            rows.append({
                "strike": strike,
                "type": "PE",
                "oi": pe.get("openInterest", 0),
                "change_oi": pe.get("changeinOpenInterest", 0),
                "ltp": pe.get("lastPrice", 0)
            })

    return pd.DataFrame(rows)
