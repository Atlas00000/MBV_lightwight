"""M2-W3: time-ordered train/val split, simple sanity stats, leakage column list."""
from __future__ import annotations

import pandas as pd

# Columns safe to use as *decision-time* inputs (SIGNAL row only; no OUTCOME join fields).
FEATURE_COLUMNS = [
    "bar_time",
    "symbol",
    "chart_tf",
    "ea_version",
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
    "schema",
]

# Do not train on these (post-trade or derived labels).
LABEL_AND_OUTCOME_COLUMNS = [
    "out_pnl",
    "out_dur_s",
    "out_mfe",
    "out_mae",
    "out_pos_id",
    "out_xdeal",
    "y_profitable",
    "y_mfe_positive",
    "y_mfe_ge_abs_mae",
    "y_catastrophic",
]


def time_split_signals(
    signals_with_labels: pd.DataFrame,
    train_ratio: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split SIGNAL rows by `bar_time` (chronological). Rows with missing/zero bar_time dropped."""
    s = signals_with_labels.copy()
    bt = pd.to_numeric(s["bar_time"], errors="coerce")
    s = s.loc[bt.notna() & (bt > 0)]
    s = s.sort_values("bar_time", kind="mergesort")
    n = len(s)
    if n < 2:
        raise ValueError("Not enough SIGNAL rows with bar_time>0 for split.")
    cut = max(1, min(n - 1, int(n * float(train_ratio))))
    train = s.iloc[:cut].reset_index(drop=True)
    val = s.iloc[cut:].reset_index(drop=True)
    return train, val


def monthly_pnl_summary(df: pd.DataFrame) -> str:
    """Text-only sanity: sum PnL by calendar month (UTC) on rows with `out_pnl` not null."""
    sub = df.loc[df["out_pnl"].notna()].copy()
    if sub.empty:
        return "monthly_pnl: no joined outcomes."
    ts = pd.to_datetime(sub["bar_time"], unit="s", errors="coerce")
    sub["_month"] = ts.dt.to_period("M")
    g = sub.groupby("_month", sort=True)["out_pnl"]
    lines = ["monthly sum(out_pnl) [account currency]:"]
    for m, ser in g:
        lines.append(f"  {m}: n={len(ser)} sum={ser.sum():.4f}")
    return "\n".join(lines)


def leakage_audit_text() -> str:
    return (
        "Leakage audit (M2-W3)\n"
        "---------------------\n"
        "- Use only FEATURE_COLUMNS as model inputs at decision time.\n"
        "- LABEL_AND_OUTCOME_COLUMNS come from the closing OUTCOME row; "
        "never feed them as inputs to predict the same trade.\n"
        "- On raw SIGNAL rows, `pnl`/`dur_s`/`mfe`/`mae`/`pos_id`/`xdeal` are "
        "placeholders (zeros); prefer dropping them for ML if present after export.\n"
        "- `signal_id` and `_source_file` are metadata: exclude from fit or use only for joins.\n"
    )


def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return X columns that exist in df (subset of FEATURE_COLUMNS)."""
    cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    return df[cols].copy()
