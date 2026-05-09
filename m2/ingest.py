"""M2-W1: load MBV CSV logs, normalize dtypes, time-sort, duplicate signal_id QC."""
from __future__ import annotations

import glob
from pathlib import Path
from typing import Iterable

import pandas as pd

# Header from MBV_Log.mqh (must match file)
EXPECTED_COLS = [
    "event",
    "signal_id",
    "ea_version",
    "bar_time",
    "symbol",
    "chart_tf",
    "o",
    "h",
    "l",
    "c",
    "bb_u",
    "bb_m",
    "bb_l",
    "rsi",
    "atr",
    "adx",
    "pdi",
    "mdi",
    "trend_c",
    "trend_ema",
    "spread",
    "touch_b",
    "touch_s",
    "raw_b",
    "raw_s",
    "fin_b",
    "fin_s",
    "executed",
    "skip",
    "ord_ret",
    "side",
    "pnl",
    "dur_s",
    "mfe",
    "mae",
    "pos_id",
    "xdeal",
    "schema",
]


def _read_one_csv(path: Path) -> pd.DataFrame:
    for enc in ("utf-8-sig", "cp1252"):
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        df = pd.read_csv(path, encoding="cp1252", errors="replace")
    if list(df.columns) != EXPECTED_COLS:
        missing = [c for c in EXPECTED_COLS if c not in df.columns]
        extra = [c for c in df.columns if c not in EXPECTED_COLS]
        raise ValueError(f"{path}: column mismatch. Missing={missing!r} Extra={extra!r}")
    df["_source_file"] = str(path)
    return df


def load_csvs(paths: Iterable[str | Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for p in paths:
        frames.append(_read_one_csv(Path(p)))
    if not frames:
        raise ValueError("No CSV files loaded.")
    df = pd.concat(frames, ignore_index=True)
    return normalize_dtypes(df)


def load_glob(pattern: str) -> pd.DataFrame:
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No files match glob: {pattern!r}")
    return load_csvs(paths)


def normalize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bar_time"] = pd.to_numeric(out["bar_time"], errors="coerce").astype("Int64")
    int_cols = [
        "spread",
        "touch_b",
        "touch_s",
        "raw_b",
        "raw_s",
        "fin_b",
        "fin_s",
        "executed",
        "skip",
        "ord_ret",
        "dur_s",
        "pos_id",
        "xdeal",
    ]
    for c in int_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("Int64")
    float_cols = [
        "o",
        "h",
        "l",
        "c",
        "bb_u",
        "bb_m",
        "bb_l",
        "rsi",
        "atr",
        "adx",
        "pdi",
        "mdi",
        "trend_c",
        "trend_ema",
        "pnl",
        "mfe",
        "mae",
    ]
    for c in float_cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out["signal_id"] = out["signal_id"].fillna("").astype(str)
    out["ea_version"] = out["ea_version"].astype(str)
    out["symbol"] = out["symbol"].astype(str)
    out["chart_tf"] = out["chart_tf"].astype(str)
    out["side"] = out["side"].astype(str)
    out["schema"] = out["schema"].astype(str)
    return out


def sort_by_bar_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(["bar_time", "event", "signal_id"], kind="mergesort").reset_index(drop=True)


def check_duplicate_executed_signal_ids(df: pd.DataFrame) -> list[str]:
    """Return list of error messages (empty if OK)."""
    sig = df[(df["event"] == "SIGNAL") & (df["executed"] == 1) & (df["signal_id"].str.len() > 0)]
    dup = sig["signal_id"].value_counts()
    dup = dup[dup > 1]
    if dup.empty:
        return []
    msgs = [f"Duplicate executed signal_id {i!r} count={c}" for i, c in dup.items()]
    return msgs


def ingest_qc_report(df: pd.DataFrame) -> str:
    lines = [
        f"rows={len(df)}",
        f"events: {df['event'].value_counts().to_dict()}",
    ]
    dups = check_duplicate_executed_signal_ids(df)
    lines.append("duplicate executed signal_id: OK" if not dups else "DUPLICATES:\n  " + "\n  ".join(dups))
    return "\n".join(lines)
