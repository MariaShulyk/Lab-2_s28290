import os
import json
import argparse
import pandas as pd

def _get_client():
    import gspread
    from google.oauth2.service_account import Credentials

    sa_json = os.environ.get("GOOGLE_SA_JSON")
    if not sa_json:
        raise RuntimeError("Missing env GOOGLE_SA_JSON (GitHub Secret).")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    info = json.loads(sa_json)
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)

def upload_csv(sheet_id: str, csv_path: str, worksheet: str = "data"):
    import gspread
    gc = _get_client()
    sh = gc.open_by_key(sheet_id)

    try:
        ws = sh.worksheet(worksheet)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=worksheet, rows=2000, cols=50)

    df = pd.read_csv(csv_path)

    # ---- KLUCZOWE: usuń NaN/Inf, bo API nie akceptuje takich wartości w JSON ----
    df = df.replace([float("inf"), float("-inf")], pd.NA)  # Inf -> NA
    df = df.replace([pd.NA, None], "")                     # NA/None -> ""
    df = df.fillna("")                                     # NaN -> ""

    # Jeżeli masz typy mieszane, zostawiamy jako "object" (listy list)
    values = [df.columns.tolist()] + df.astype(object).values.tolist()

    ws.clear()
    ws.update(values)
    print(f"Uploaded {csv_path} -> {worksheet} ({df.shape[0]} rows, {df.shape[1]} cols)")

def download_csv(sheet_id: str, out_path: str = "sheet_data.csv", worksheet: str = "data"):
    gc = _get_client()
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(worksheet)
    data = ws.get_all_records()
    pd.DataFrame(data).to_csv(out_path, index=False)
    print(f"Downloaded worksheet '{worksheet}' -> {out_path}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Sync CSV <-> Google Sheets")
    p.add_argument("--mode", choices=["upload", "download"], required=True)
    p.add_argument("--sheet-id", required=True)
    p.add_argument("--worksheet", default="data")
    p.add_argument("--csv", help="Path to CSV for upload")
    p.add_argument("--out", default="sheet_data.csv")
    a = p.parse_args()

    if a.mode == "upload":
        if not a.csv:
            raise SystemExit("Provide --csv for upload mode")
        upload_csv(a.sheet_id, a.csv, a.worksheet)
    else:
        download_csv(a.sheet_id, a.out, a.worksheet)
