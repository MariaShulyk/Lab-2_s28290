import os
import argparse
import json
import pandas as pd
import numpy as np
import logging
from logging import Formatter, StreamHandler, FileHandler


NUMERIC_COLS = ["Wiek", "Średnie Zarobki"]
TIME_START = "Czas Początkowy Podróży"
TIME_END = "Czas Końcowy Podróży"

def get_logger(name: str = "clean_standard", log_file: str = "log.txt", level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    logger.propagate = False

    fmt = Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    ch = StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

LOGGER = get_logger()

def read_from_sheets(sheet_id: str, worksheet: str = "data") -> pd.DataFrame:
    LOGGER.info(f"Reading data from Google Sheets: sheet_id={sheet_id}, worksheet={worksheet}")
    import gspread
    from google.oauth2.service_account import Credentials

    sa_json = os.environ.get("GOOGLE_SA_JSON")

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    info = json.loads(sa_json)
    creds = Credentials.from_service_account_info(info, scopes=scope)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(worksheet)
    records = ws.get_all_records()
    df = pd.DataFrame(records)
    LOGGER.info(f"Loaded DataFrame from Sheets with shape {df.shape}")
    return df

def read_from_csv(csv_path: str) -> pd.DataFrame:
    LOGGER.info(f"Reading data from CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    LOGGER.info(f"Loaded DataFrame from CSV with shape {df.shape}")
    return df

def parse_time_to_minutes(x):
    try:
        h, m = str(x).split(":")
        h, m = int(h), int(m)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return np.nan
        return h * 60 + m
    except Exception:
        return np.nan

def compute_duration_minutes(start_min, end_min):
    if np.isnan(start_min) or np.isnan(end_min):
        return np.nan
    return (end_min - start_min) % (24 * 60)

def mode_or_nan(series: pd.Series):
    s = series.dropna()
    return s.mode().iloc[0] if not s.empty else np.nan

def standardize_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    mu = s.mean()
    sigma = s.std(ddof=0) or 1.0
    return (s - mu) / sigma

def clean_and_standardize_with_report(df: pd.DataFrame):
    LOGGER.info("=== Start cleaning & standardization ===")
    original_rows, original_cols = df.shape
    total_cells = original_rows * original_cols
    LOGGER.info(f"Original shape: rows={original_rows}, cols={original_cols} (total cells={total_cells})")

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")


    if TIME_START in df.columns:
        df["start_min"] = df[TIME_START].apply(parse_time_to_minutes)
    else:
        df["start_min"] = np.nan
    if TIME_END in df.columns:
        df["end_min"] = df[TIME_END].apply(parse_time_to_minutes)
    else:
        df["end_min"] = np.nan
    df["duration_min"] = df.apply(
        lambda r: compute_duration_minutes(r["start_min"], r["end_min"]), axis=1
    )


    invalid_duration = df["duration_min"] > 720
    too_many_nans = df.isna().sum(axis=1) >= 4
    to_drop = invalid_duration | too_many_nans
    rows_dropped = int(to_drop.sum())
    LOGGER.info(f"Rows to drop: {rows_dropped} "
                f"(invalid_duration={int(invalid_duration.sum())}, too_many_nans={int(too_many_nans.sum())})")
    df = df.loc[~to_drop].reset_index(drop=True)

    nans_before = df.isna().sum().sum()
    for col in df.columns:
        if col in ["start_min", "end_min", "duration_min"]:
            continue
        if df[col].dtype.kind in "iufc":
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(mode_or_nan(df[col]))

    if TIME_START in df.columns:
        df["start_min"] = df[TIME_START].apply(parse_time_to_minutes)
    if TIME_END in df.columns:
        df["end_min"] = df[TIME_END].apply(parse_time_to_minutes)
    df["duration_min"] = df.apply(
        lambda r: compute_duration_minutes(r["start_min"], r["end_min"]), axis=1
    )
    nans_after = df.isna().sum().sum()
    changed_by_imputation = int(max(0, nans_before - nans_after))
    LOGGER.info(f"Imputed cells: {changed_by_imputation}")

    changed_by_standardization = 0
    for col in NUMERIC_COLS:
        if col in df.columns:
            before = df[col].astype(float).values.copy()
            df[col] = standardize_series(df[col])
            after = df[col].astype(float).values
            changed_by_standardization += int(np.sum(before != after))
    LOGGER.info(f"Standardized numeric columns {NUMERIC_COLS}; changed cells by std: {changed_by_standardization}")

    changed_cells = min(changed_by_imputation + changed_by_standardization, total_cells)
    percent_changed = (changed_cells / total_cells * 100.0) if total_cells else 0.0
    percent_removed = (rows_dropped / original_rows * 100.0) if original_rows else 0.0

    report = [
        f"Original rows: {original_rows}, columns: {original_cols}",
        f"Total cells: {total_cells}",
        f"Rows dropped: {rows_dropped} ({percent_removed:.2f}%)",
        f"Cells changed (imputed + standardized): {changed_cells} ({percent_changed:.2f}%)",
    ]
    for line in report:
        LOGGER.info(line)

    out_df = df.drop(columns=[c for c in ["start_min", "end_min", "duration_min"] if c in df.columns])

    LOGGER.info("Cleaning & standardization finished")
    return out_df, "\n".join(report) + "\n"



def main():
    ap = argparse.ArgumentParser(description="Clean + standardize + report + logging (Sheets or CSV).")
    ap.add_argument("--source", choices=["sheets", "csv"], required=True)
    ap.add_argument("--sheet-id", help="Google Sheet ID (for --source sheets)")
    ap.add_argument("--worksheet", default="data")
    ap.add_argument("--csv-in", help="Input CSV (for --source csv)")
    ap.add_argument("--out", default="cleaned_data.csv")
    ap.add_argument("--report", default="report.txt")
    args = ap.parse_args()

    if args.source == "sheets":
        if not args.sheet_id:
            LOGGER.error("--sheet-id is required for --source sheets")
            raise SystemExit("--sheet-id is required for --source sheets")
        df = read_from_sheets(args.sheet_id, args.worksheet)
    else:
        if not args.csv_in:
            LOGGER.error("--csv-in is required for --source csv")
            raise SystemExit("--csv-in is required for --source csv")
        df = read_from_csv(args.csv_in)

    cleaned, report_text = clean_and_standardize_with_report(df)
    cleaned.to_csv(args.out, index=False)
    LOGGER.info(f"Saved cleaned data to '{args.out}'")

    with open(args.report, "w", encoding="utf-8") as f:
        f.write(report_text)
    LOGGER.info(f"Wrote report to '{args.report}'")

    LOGGER.info("Report summary: \n%s ", report_text)

if __name__ == "__main__":
    main()
