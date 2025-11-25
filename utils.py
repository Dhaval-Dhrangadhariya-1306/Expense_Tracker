import csv
from pathlib import Path
import pandas as pd
from datetime import datetime

def export_to_csv(rows, filepath):
    # rows is list of tuples (id, date, category, amount, note)
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "category", "amount", "note"])
        for r in rows:
            writer.writerow(r)

def export_to_csv_pandas(rows, filepath):
    # optional, nicer CSV with pandas
    cols = ["id", "date", "category", "amount", "note"]
    df = pd.DataFrame(rows, columns=cols)
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)

def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def format_date_for_input(dt):
    # return ISO YYYY-MM-DD
    if isinstance(dt, str):
        return dt
    return dt.strftime("%Y-%m-%d")

def parse_date(s):
    # accept YYYY-MM-DD or other common formats, return YYYY-MM-DD
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
    except:
        d = datetime.strptime(s, "%d-%m-%Y")
    return d.strftime("%Y-%m-%d")
